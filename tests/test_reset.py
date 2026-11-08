import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rts_reset', ROOT / 'skills/train/scripts/reset_state.py')
resetter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resetter)

LEARNER = ('# Learner Profile\n\nLearning mode: paused\nOnboarding: complete\n\n'
           '## Project\nBuilding: payments\n\n'
           '## Experience\nOverall programming: Intermediate (self-reported)\n\n'
           '## Goals\nPrimary: payments\nCapability goal: systems reasoning\n\n'
           '## Preferences\nQuestion style: Open-ended\n\n'
           '## Strong Concepts\nUnderstands transactions independently.\n\n'
           '## Developing Concepts\nRetry after a hint.\n\n'
           '## Revisit\nQueue recovery.\n')
PENDING = '## Pending decision\nDesign: retry budget\nAwaiting implementation approval; no edits authorized.\n'
LOG = '# Learning Progress\n\n## Transactions\nIndependently explained atomicity.\n\n' + PENDING
LEGACY = ('# Engineering decision\nTask: payment\nStatus: proposed\n'
          'Pending approval: retry implementation\nBaseline: retry everything\n'
          'After: distinguishes permanent failures independently\nFuture transfer: not observed\n')


class ResetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project with spaces'
        self.root.mkdir()
        (self.root / '.git').mkdir()
        self.folder = self.root / '.reason-to-ship'
        self.folder.mkdir()
        self.write('learner.md', LEARNER)
        self.write('learning-log.md', LOG)
        self.write('project-context.md', '# Project Map\nChosen design: database transaction.\n')
        (self.root / 'app.py').write_text('print("keep source")\n')

    def write(self, name, text):
        (self.folder / name).write_bytes(text.encode('utf-8'))

    def read(self, name):
        return (self.folder / name).read_text(encoding='utf-8')

    def apply(self, scope='learning'):
        preview = resetter.reset(str(self.root), scope)
        return resetter.reset(str(self.root), scope, preview['confirmation_token'])

    def test_preview_and_cancel_are_read_only(self):
        before = resetter.snapshot(self.folder)
        preview = resetter.reset(str(self.root))
        self.assertEqual(preview['scope'], 'learning')
        self.assertEqual(preview['status'], 'preview')
        self.assertEqual(before, resetter.snapshot(self.folder))
        self.assertFalse((self.folder / 'backups').exists())
        self.assertFalse((self.folder / '.reset.lock').exists())

    def test_learning_reset_preserves_profile_design_pending_and_exact_backup(self):
        self.write('decisions.md', LEGACY)
        before = resetter.snapshot(self.folder)
        result = self.apply()
        self.assertEqual(result['status'], 'complete')
        learner = self.read('learner.md')
        for retained in ('Learning mode: paused', 'Building: payments', 'Intermediate (self-reported)',
                         'Capability goal: systems reasoning', 'Question style: Open-ended'):
            self.assertIn(retained, learner)
        self.assertNotIn('Understands transactions independently.', learner)
        self.assertNotIn('Independently explained atomicity.', self.read('learning-log.md'))
        self.assertIn(PENDING, self.read('learning-log.md'))
        self.assertEqual(before['project-context.md'], (self.folder / 'project-context.md').read_bytes())
        self.assertIn('Pending approval: retry implementation', self.read('decisions.md'))
        self.assertNotIn('retry everything', self.read('decisions.md'))
        backup = Path(result['backup'])
        manifest = json.loads((backup / 'manifest.json').read_text(encoding='utf-8'))
        for name, content in before.items():
            self.assertEqual(content, (backup / name).read_bytes())
            self.assertEqual(resetter.digest(content), manifest['files'][name])
        self.assertIn('state.md', manifest['missing'])
        self.assertEqual((self.root / 'app.py').read_text(), 'print("keep source")\n')

    def test_project_reset_keeps_historical_evidence_including_legacy(self):
        self.write('decisions.md', LEGACY)
        self.apply('project')
        learner = self.read('learner.md')
        self.assertIn('Intermediate (self-reported)', learner)
        self.assertIn('Understands transactions independently.', learner)
        self.assertIn('Capability goal: systems reasoning', learner)
        self.assertNotIn('payments', learner)
        self.assertIn('Independently explained atomicity.', self.read('learning-log.md'))
        self.assertNotIn('Pending decision', self.read('learning-log.md'))
        self.assertNotIn('Chosen design', self.read('project-context.md'))
        self.assertIn('After: distinguishes permanent failures independently', self.read('decisions.md'))
        self.assertNotIn('Pending approval', self.read('decisions.md'))

    def test_all_reset_clears_profile_and_legacy_without_touching_unknown_files(self):
        self.write('state.md', 'Learning mode: active\nCurrent task: old\n')
        self.write('decisions.md', LEGACY)
        self.write('custom-notes.md', 'untouched')
        self.apply('all')
        self.assertIn('Onboarding reset: pending', self.read('learner.md'))
        for name in ('learner.md', 'learning-log.md', 'project-context.md', 'state.md', 'decisions.md'):
            for old in ('payments', 'Intermediate', 'Understands transactions', 'retry implementation', 'Current task: old'):
                self.assertNotIn(old, self.read(name))
        self.assertEqual(self.read('custom-notes.md'), 'untouched')
        status = json.loads(self.read('reset-status.json'))
        self.assertEqual(set(status['cleared']), {'learning', 'project', 'profile'})

    def test_chinese_sections_and_fenced_pending_example(self):
        self.write('learner.md', '# 学习者档案\nLearning mode: active\n\n## 经验\n总体编程经验：中级\n\n## 已展示较好理解的概念\n旧理解\n')
        self.write('learning-log.md', '# 学习进展\n\n## 事务\n```markdown\n## Pending decision\nexample only\n```\n\n' + PENDING)
        self.apply()
        self.assertIn('总体编程经验：中级', self.read('learner.md'))
        self.assertNotIn('旧理解', self.read('learner.md'))
        self.assertNotIn('example only', self.read('learning-log.md'))
        self.assertIn(PENDING, self.read('learning-log.md'))

    def test_stale_confirmation_and_wrong_scope_change_nothing(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        with self.assertRaises(resetter.ResetError):
            resetter.reset(str(self.root), 'all', token)
        self.write('learning-log.md', LOG + '\nUpdated by user.\n')
        before = resetter.snapshot(self.folder)
        with self.assertRaises(resetter.ResetError):
            resetter.reset(str(self.root), confirm=token)
        self.assertEqual(before, resetter.snapshot(self.folder))
        self.assertFalse((self.folder / 'backups').exists())

    def test_markdown_heading_variants_preserve_pending_scope(self):
        pending = '  ## Pending Decision ##\nAwaiting approval: no code changes.\n'
        self.write('learning-log.md', '# Learning Progress\n\n## Transactions\nOld evidence.\n\n' + pending)
        self.apply()
        self.assertIn(pending, self.read('learning-log.md'))
        self.assertNotIn('Old evidence.', self.read('learning-log.md'))

    def test_ambiguous_pending_heading_fails_without_mutation(self):
        self.write('learning-log.md', '# Learning Progress\n\n## Pending decision: payment\nNot approved.\n')
        before = resetter.snapshot(self.folder)
        with self.assertRaisesRegex(resetter.ResetError, 'Ambiguous pending-decision heading'):
            self.apply()
        self.assertEqual(before, resetter.snapshot(self.folder))
        self.assertFalse((self.folder / 'backups').exists())

    def test_chinese_project_reset_clears_goal_but_keeps_capability_goal(self):
        self.write('learner.md', '# 学习者档案\nLearning mode: active\n\n## 项目\n正在构建：支付\n\n## 经验\n总体编程经验：中级\n\n## 目标\n主要目标：完成支付\n能力提升目标：理解事务\n')
        self.apply('project')
        learner = self.read('learner.md')
        self.assertNotIn('支付', learner)
        self.assertIn('总体编程经验：中级', learner)
        self.assertIn('能力提升目标：理解事务', learner)

    def test_late_change_to_unmodified_note_prevents_success(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        original = resetter.atomic_write

        def change(path, data):
            original(path, data)
            if path == self.folder / 'learning-log.md':
                self.write('project-context.md', 'concurrently edited project')

        with patch.object(resetter, 'atomic_write', side_effect=change):
            with self.assertRaisesRegex(resetter.ResetError, 'Concurrent change detected'):
                resetter.reset(str(self.root), confirm=token)
        self.assertEqual(json.loads(self.read('reset-status.json'))['status'], 'incomplete')

    def test_backup_failure_leaves_all_active_notes_unchanged(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        before = resetter.snapshot(self.folder)
        with patch.object(resetter, 'backup_notes', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(resetter.ResetError, 'No notes reset'):
                resetter.reset(str(self.root), confirm=token)
        self.assertEqual(before, resetter.snapshot(self.folder))
        self.assertFalse((self.folder / '.reset.lock').exists())

    def test_corrupt_backup_is_detected_before_reset(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        before = resetter.snapshot(self.folder)
        original = Path.read_bytes

        def corrupt(path):
            if 'backups' in path.parts and path.name == 'learner.md':
                return b'corrupted copy'
            return original(path)

        with patch.object(Path, 'read_bytes', corrupt):
            with self.assertRaisesRegex(resetter.ResetError, 'Backup verification failed'):
                resetter.reset(str(self.root), confirm=token)
        self.assertEqual(before, resetter.snapshot(self.folder))

    def test_mid_write_failure_retains_backup_and_blocks_new_reset(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        before = resetter.snapshot(self.folder)
        original = resetter.atomic_write

        def fail(path, data):
            if path == self.folder / 'learning-log.md':
                raise OSError('write interrupted')
            return original(path, data)

        with patch.object(resetter, 'atomic_write', side_effect=fail):
            with self.assertRaisesRegex(resetter.ResetError, 'Reset incomplete'):
                resetter.reset(str(self.root), confirm=token)
        status = json.loads(self.read('reset-status.json'))
        self.assertEqual(status['status'], 'incomplete')
        for name, content in before.items():
            self.assertEqual(content, (self.folder / status['backup'] / name).read_bytes())
        with self.assertRaisesRegex(resetter.ResetError, 'previous reset is incomplete'):
            resetter.reset(str(self.root))

    def test_repeated_reset_keeps_backups_and_context_boundaries(self):
        first = self.apply('project')
        first_status = json.loads(self.read('reset-status.json'))
        second = self.apply('learning')
        second_status = json.loads(self.read('reset-status.json'))
        self.assertNotEqual(first['backup'], second['backup'])
        self.assertTrue(Path(first['backup']).is_dir())
        self.assertEqual(first_status['cleared']['project'], second_status['cleared']['project'])
        self.assertIn('learning', second_status['cleared'])

    def test_unknown_sections_and_unclosed_fences_refuse_partial_reset(self):
        self.write('learner.md', LEARNER + '\n## Custom memory\nUnclassified.\n')
        with self.assertRaisesRegex(resetter.ResetError, 'Unknown learner section'):
            resetter.reset(str(self.root))
        self.assertFalse((self.folder / 'backups').exists())
        self.write('learner.md', LEARNER)
        self.write('learning-log.md', LOG + '\n```\nUnclosed example\n')
        with self.assertRaisesRegex(resetter.ResetError, 'Unclosed Markdown fence'):
            resetter.reset(str(self.root))
        self.assertEqual(resetter.reset(str(self.root), 'all')['status'], 'preview')

    def test_nested_repo_worktree_and_non_git_boundaries(self):
        child = self.root / 'src'
        child.mkdir()
        self.assertEqual(resetter.reset(str(child))['project'], str(self.root.resolve()))
        (child / '.git').write_text('gitdir: elsewhere')
        self.assertEqual(resetter.reset(str(child))['status'], 'no_state')
        (child / '.git').unlink()
        (self.root / '.git').rmdir()
        self.assertEqual(resetter.reset(str(child))['status'], 'no_state')
        self.assertFalse((child / '.reason-to-ship').exists())

    def test_existing_lock_blocks_apply(self):
        token = resetter.reset(str(self.root))['confirmation_token']
        (self.folder / '.reset.lock').write_text('other process')
        with self.assertRaisesRegex(resetter.ResetError, 'reset lock exists'):
            resetter.reset(str(self.root), confirm=token)
        self.assertFalse((self.folder / 'backups').exists())

    def test_linked_backup_destination_is_rejected(self):
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        try:
            (self.folder / 'backups').symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            if sys.platform == 'win32' and exc.winerror == 1314:
                self.skipTest('Windows symlink creation privilege is unavailable')
            raise
        before = resetter.snapshot(self.folder)
        with self.assertRaisesRegex(resetter.ResetError, 'Linked paths'):
            self.apply()
        self.assertEqual(before, resetter.snapshot(self.folder))
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
