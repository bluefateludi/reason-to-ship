import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'hooks/session_start.py'
spec = importlib.util.spec_from_file_location('rts_hook', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        (self.repo / '.git').mkdir()
        self.state = self.repo / '.reason-to-ship'
        self.state.mkdir()
        (self.state / 'state.md').write_text('# State\nLearning mode: active\n', encoding='utf-8')
        (self.state / 'decisions.md').write_text('Status: proposed\n', encoding='utf-8')

    def run_hook(self, cwd=None, source='startup', raw=None):
        inp = raw if raw is not None else json.dumps({'hook_event_name': 'SessionStart', 'source': source, 'cwd': str(cwd or self.repo)})
        result = subprocess.run([sys.executable, '-B', str(HOOK)], input=inp, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def test_active_and_compact(self):
        for source in ('startup','resume','compact','clear','fork'):
            result = self.run_hook(source=source)
            self.assertIn('decisions.md', result['hookSpecificOutput']['additionalContext'])
            self.assertIn('not', result['hookSpecificOutput']['additionalContext'])

    def test_inactive(self):
        (self.state / 'state.md').write_text('Learning mode: paused\n')
        self.assertIsNone(self.run_hook())

    def test_incomplete_reset_returns_recovery_instead_of_resume(self):
        (self.state / 'reset-status.json').write_text(json.dumps({
            'version': 1, 'status': 'incomplete', 'cleared': {'learning': '2026-11-08'}}))
        context = self.run_hook()['hookSpecificOutput']['additionalContext']
        self.assertIn('Do not resume', context)
        self.assertNotIn('Resume the existing task', context)

    def test_invalid_reset_marker_or_lock_requires_recovery(self):
        marker = self.state / 'reset-status.json'
        for value in ('{', '[]', '{"version": 1, "status": "complete"}'):
            marker.write_text(value)
            self.assertIn('recovery inspection', self.run_hook()['hookSpecificOutput']['additionalContext'])
        marker.unlink()
        (self.state / '.reset.lock').write_text('other process')
        self.assertIn('recovery inspection', self.run_hook()['hookSpecificOutput']['additionalContext'])

    def test_completed_reset_preserves_paused_mode(self):
        (self.state / 'reset-status.json').write_text(json.dumps({
            'version': 1, 'status': 'complete', 'cleared': {'learning': '2026-11-08'}}))
        self.assertIn('cleared context boundaries', self.run_hook()['hookSpecificOutput']['additionalContext'])
        (self.state / 'state.md').write_text('Learning mode: paused\n')
        self.assertIsNone(self.run_hook())

    def test_new_learner_without_legacy_state(self):
        (self.state / 'state.md').unlink()
        (self.state / 'learner.md').write_text('Learning mode: active\nOnboarding: complete\n')
        result = self.run_hook(source='compact')
        context = result['hookSpecificOutput']['additionalContext']
        for name in ('learner.md', 'learning-log.md', 'project-context.md', 'decisions.md'):
            self.assertIn(name, context)

    def test_new_paused_state_overrides_legacy_active(self):
        (self.state / 'learner.md').write_text('Learning mode: paused\n')
        self.assertIsNone(self.run_hook())

    def test_invalid_new_profile_does_not_fall_back(self):
        (self.state / 'learner.md').mkdir()
        self.assertIsNone(self.run_hook())

    def test_oversized_new_profile_does_not_fall_back(self):
        (self.state / 'learner.md').write_text('Learning mode: active\n' + 'x' * 300000)
        self.assertIsNone(self.run_hook())

    def test_new_history_is_not_loaded_or_modified(self):
        (self.state / 'learner.md').write_text('Learning mode: active\n')
        before = self.run_hook()
        for name in ('learning-log.md', 'project-context.md'):
            (self.state / name).write_text('PRIVATE_SENTINEL' + 'x' * 500000)
        snapshot = {p.name: p.read_bytes() for p in self.state.iterdir()}
        self.assertEqual(before, self.run_hook())
        self.assertEqual(snapshot, {p.name: p.read_bytes() for p in self.state.iterdir()})

    def test_non_git_child_does_not_inherit_parent_notes(self):
        (self.repo / '.git').rmdir()
        child = self.repo / 'unrelated'
        child.mkdir()
        self.assertIsNone(self.run_hook(cwd=child))
        self.assertIsNotNone(self.run_hook())

    def test_child_directory(self):
        child=self.repo/'src';child.mkdir()
        self.assertIsNotNone(self.run_hook(cwd=child))

    def test_nested_repo_does_not_inherit(self):
        child=self.repo/'nested';child.mkdir();(child/'.git').mkdir()
        self.assertIsNone(self.run_hook(cwd=child))

    def test_worktree_does_not_inherit(self):
        child=self.repo/'worktree';child.mkdir();(child/'.git').write_text('gitdir: elsewhere')
        self.assertIsNone(self.run_hook(cwd=child))

    def test_no_git_parent_state_not_inherited(self):
        child=self.root/'separate';child.mkdir()
        self.assertIsNone(self.run_hook(cwd=child))

    def test_invalid_input_safe(self):
        for bad in ('', '{', '[]', 'null', '{"cwd": 3}', '{"hook_event_name":"Other","cwd":"/tmp"}'):
            self.assertIsNone(self.run_hook(raw=bad))

    def test_symlink_rejected(self):
        (self.state / 'state.md').unlink()
        target=self.root/'outside';target.write_text('Learning mode: active\n')
        try:
            (self.state / 'state.md').symlink_to(target)
        except OSError as exc:
            if sys.platform == 'win32' and exc.winerror == 1314:
                self.skipTest('Windows symlink creation privilege is unavailable')
            raise
        self.assertIsNone(self.run_hook())

    def test_configured_hook_with_python_only(self):
        if sys.platform == 'win32':
            git = shutil.which('git')
            bash = Path(git).parent.parent / 'bin/bash.exe' if git else None
        else:
            found = shutil.which('bash')
            bash = Path(found) if found else None
        if bash is None or not bash.is_file():
            self.skipTest('Bash is required for the configured hook integration test')
        # A minimal PATH reproduces Windows installations without python3.
        bin_dir = self.root / 'bin with spaces'
        bin_dir.mkdir()
        python = bin_dir / 'python'
        python.write_text('#!/bin/sh\nexec ' + shlex.quote(Path(sys.executable).as_posix()) + ' "$@"\n', encoding='utf-8')
        python.chmod(0o755)
        bash_wrapper = bin_dir / 'bash'
        bash_wrapper.write_text('#!/bin/sh\nexec ' + shlex.quote(bash.as_posix()) + ' "$@"\n', encoding='utf-8')
        bash_wrapper.chmod(0o755)
        config = json.loads((ROOT / 'hooks/hooks.json').read_text(encoding='utf-8'))
        command = config['hooks']['SessionStart'][0]['hooks'][0]['command']
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=ROOT.as_posix())
        if sys.platform == 'win32':
            converted = subprocess.run([str(bash), '-c', 'cygpath -u "$1"', '_', str(bin_dir)], capture_output=True, text=True, check=True).stdout.strip()
            env['PATH'] = converted
        else:
            env['PATH'] = str(bin_dir)
        # Run the config through bash, as the host does; no shell lookup needed.
        result = subprocess.run([str(bash), '-c', command], env=env,
            input=json.dumps({'hook_event_name': 'SessionStart', 'cwd': str(self.repo)}),
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Resume the existing task', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])

    def test_large_state_safe(self):
        (self.state / 'state.md').write_text('Learning mode: active\n' + 'x'*300000)
        self.assertIsNone(self.run_hook())

    def test_large_decisions_constant_output(self):
        before=self.run_hook()
        (self.state/'decisions.md').write_text('x'*5000000)
        self.assertEqual(before,self.run_hook())

    def test_never_writes(self):
        before={p.name:p.read_bytes() for p in self.state.iterdir()}
        self.run_hook()
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.state.iterdir()})

if __name__=='__main__': unittest.main()
