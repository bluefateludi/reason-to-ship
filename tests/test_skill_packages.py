import importlib.util
import json
import posixpath
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rts_packages', ROOT / 'scripts/build_skill_packages.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackageTests(unittest.TestCase):
    def test_install_layout_and_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            for archive in builder.build(tmp):
                target = 'agents' if archive.stem.endswith('-agents') else 'codex'
                prefix = '.%s/skills/reason-to-ship/' % target
                with ZipFile(archive) as bundle:
                    names = set(bundle.namelist())
                    self.assertIsNone(bundle.testzip())
                    self.assertIn(prefix + 'SKILL.md', names)
                    for resource in ('state-templates.md', 'state-templates.zh-CN.md',
                                     'personalization.md', 'personalization.zh-CN.md',
                                     'THIRD_PARTY_NOTICES.md', 'reset.md', 'reset.zh-CN.md',
                                     'scripts/reset_state.py'):
                        self.assertIn(prefix + 'references/' + resource, names)
                    notice = bundle.read(prefix + 'references/THIRD_PARTY_NOTICES.md').decode('utf-8')
                    self.assertIn('Copyright (c) 2026 Noah Kim', notice)
                    self.assertIn('Permission is hereby granted', notice)
                    self.assertTrue(all(n.startswith(prefix) and '..' not in n.split('/') for n in names))
                    self.assertFalse(any('/hooks/' in n or '/.reason-to-ship/' in n for n in names))
                    for case in ('retry', 'idempotency', 'cache-consistency', 'rate-limiting', 'async-jobs'):
                        for doc in ('README.md', 'README.zh-CN.md'):
                            self.assertIn(prefix + 'cases/' + case + '/' + doc, names)
                    # Every Markdown resource link must resolve inside the installed skill.
                    for name in names:
                        if not name.endswith('.md'):
                            continue
                        for link in re.findall(r'\]\(([^)]+)\)', bundle.read(name).decode('utf-8')):
                            if '://' in link or link.startswith('#'):
                                continue
                            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), link.split('#')[0]))
                            self.assertIn(resolved, names, (name, link))
                    install = Path(tmp) / ('install-' + target)
                    bundle.extractall(install)
                    self.assertTrue((install / prefix / 'SKILL.md').is_file())
                    # Exercise the helper from the extracted package, with no
                    # dependency on source-tree paths or a Claude installation.
                    project = Path(tmp) / ('reset-' + target)
                    notes = project / '.reason-to-ship'
                    notes.mkdir(parents=True)
                    learner = notes / 'learner.md'
                    learner.write_text('# Learner\nLearning mode: active\n\n## Experience\nSelf report\n\n## Strong Concepts\nOld evidence\n', encoding='utf-8')
                    helper = install / prefix / 'references/scripts/reset_state.py'
                    command = [sys.executable, '-X', 'utf8', '-B', str(helper), '--project', str(project)]
                    preview = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
                    token = json.loads(preview.stdout)['confirmation_token']
                    applied = subprocess.run(command + ['--confirm', token], capture_output=True, text=True, encoding='utf-8', check=True)
                    self.assertEqual(json.loads(applied.stdout)['status'], 'complete')
                    self.assertIn('Self report', learner.read_text(encoding='utf-8'))
                    self.assertNotIn('Old evidence', learner.read_text(encoding='utf-8'))

    def test_reproducible_and_same_training_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = builder.build(Path(tmp) / 'first')
            second = builder.build(Path(tmp) / 'second')
            self.assertEqual([p.read_bytes() for p in first], [p.read_bytes() for p in second])
            contents = []
            for archive in first:
                with ZipFile(archive) as bundle:
                    contents.append({n.split('/skills/reason-to-ship/', 1)[1]: bundle.read(n) for n in bundle.namelist()})
            self.assertEqual(contents[0], contents[1])


if __name__ == '__main__':
    unittest.main()
