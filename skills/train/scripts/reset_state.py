#!/usr/bin/env python3
"""Preview or apply a scoped, backup-first reset of Reason to Ship notes.

Python 3.8+, standard library only. Preview is read-only. Apply requires the
fingerprint returned by that preview; the caller obtains the user's confirmation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import uuid


NOTES = ('learner.md', 'learning-log.md', 'project-context.md', 'state.md', 'decisions.md')
STATUS = 'reset-status.json'
MAX_BYTES = 4 * 1024 * 1024
CONCEPTS = {'Strong Concepts', 'Developing Concepts', 'Revisit',
            '已展示较好理解的概念', '正在形成理解的概念', '需要回顾的内容'}
PROFILE = {'Project', 'Experience', 'Goals', 'Preferences',
           '项目', '经验', '目标', '偏好'}
PENDING = {'Pending decision', '待确认决策'}
CLEAR = 'No learning evidence recorded. / 尚无学习证据。\n\n'


class ResetError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exists(path):
    return os.path.lexists(path)


def check_path(path, kind=None):
    """Reject symlinks and Windows reparse points before any reads or writes."""
    for item in (path, *path.parents):
        if not exists(item):
            continue
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ResetError('Linked paths are not supported: ' + str(item))
    if exists(path) and kind:
        mode = path.stat().st_mode
        if not (stat.S_ISREG(mode) if kind == 'file' else stat.S_ISDIR(mode)):
            raise ResetError('Unexpected path type: ' + str(path))


def project_root(raw):
    path = Path(raw)
    if not path.is_absolute() or '..' in path.parts:
        raise ResetError('--project must be an absolute project path without ..')
    check_path(path, 'directory')
    if not path.is_dir():
        raise ResetError('Project directory does not exist')
    path = path.resolve()
    for parent in (path, *path.parents):
        if exists(parent / '.git'):
            return parent
    return path


def snapshot(folder):
    check_path(folder, 'directory')
    result = {}
    for name in (*NOTES, STATUS):
        path = folder / name
        check_path(path, 'file')
        if exists(path):
            if path.stat().st_size > MAX_BYTES:
                raise ResetError('Note exceeds reset size limit: ' + name)
            result[name] = path.read_bytes()
    return result


def read_status(saved):
    if STATUS not in saved:
        return {}
    try:
        value = json.loads(saved[STATUS].decode('utf-8'))
        if (not isinstance(value, dict) or value.get('version') != 1 or
                value.get('status') not in ('complete', 'incomplete') or
                not isinstance(value.get('cleared', {}), dict)):
            raise ValueError()
    except (ValueError, UnicodeError):
        raise ResetError('Invalid reset-status.json; inspect it before resetting')
    if value['status'] != 'complete':
        raise ResetError('A previous reset is incomplete. Recover from its backup first.')
    return value


def sections(text):
    """Split only real level-two headings; fenced examples are not sections."""
    parts = []
    title, lines = None, []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            run, rest = marker.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not rest.strip():
                fence = None
        heading = re.match(r'^ {0,3}##[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*(?:\r?\n)?$', line) if fence is None else None
        if heading:
            parts.append((title, ''.join(lines)))
            title, lines = heading.group(1).strip(), [line]
        else:
            lines.append(line)
    if fence is not None:
        raise ResetError('Unclosed Markdown fence; clarify note structure before a partial reset')
    parts.append((title, ''.join(lines)))
    return parts


def header_and_body(section):
    lines = section.splitlines(keepends=True)
    return lines[0], ''.join(lines[1:])


def reset_learner(text, scope):
    result = []
    for title, block in sections(text):
        if title is not None and title not in PROFILE | CONCEPTS:
            raise ResetError('Unknown learner section; classify it before resetting: ' + title)
        if title in CONCEPTS and scope == 'learning':
            block = header_and_body(block)[0] + CLEAR
        elif title in {'Project', '项目'} and scope == 'project':
            block = header_and_body(block)[0] + 'Not specified / 未说明\n\n'
        elif title in {'Goals', '目标'} and scope == 'project':
            block = re.sub(r'(?m)^(Primary|主要目标)([:：])[^\r\n]*',
                           r'\1\2 Not specified / 未说明', block)
        result.append(block)
    return ''.join(result)


def reset_log(text, scope):
    kept = []
    for title, block in sections(text):
        if title is None:
            # Only the document title and blank/template text belongs here.
            # A custom preamble could mix decisions and evidence; do not guess.
            extra = [line.strip() for line in block.splitlines()
                     if line.strip() and not line.startswith('# ')]
            allowed = {'No learning events recorded yet.', '尚未记录学习事件。',
                       'No learning evidence recorded. / 尚无学习证据。'}
            if any(line not in allowed for line in extra):
                raise ResetError('Move learning-log preamble content into topic or Pending decision sections first')
            kept.append('# Learning Progress / 学习进展\n\n')
        else:
            pending = title.casefold() in {name.casefold() for name in PENDING}
            if not pending and (title.casefold().startswith('pending') or title.startswith('待确认')):
                raise ResetError('Ambiguous pending-decision heading; normalize it before resetting: ' + title)
            if pending == (scope == 'learning'):
                kept.append(block)
    return ''.join(kept)


def reset_legacy_state(text, scope):
    result = []
    known = {'Observed learning', 'Next action', '观察到的学习', '下一步'}
    for title, block in sections(text):
        if title is not None and title not in known:
            raise ResetError('Unknown legacy state section: ' + title)
        if scope == 'learning' and title in {'Observed learning', '观察到的学习'}:
            block = header_and_body(block)[0] + CLEAR
        elif scope == 'project':
            if title in {'Next action', '下一步'}:
                block = header_and_body(block)[0] + 'Reinspect the current project with the user.\n\n'
            if title is None:
                block = re.sub(r'(?m)^(Current task|Checkpoint|当前任务|待确认节点)([:：])[^\r\n]*',
                               r'\1\2 Not specified / 未说明', block)
        result.append(block)
    return ''.join(result)


def reset_legacy_decisions(text, scope):
    # Historical versions use flat fields rather than sections. Refuse
    # multiline learning evidence: its boundary cannot be inferred safely.
    keys = ('Baseline', 'After', 'Future transfer', 'Baseline / independent explanation',
            '训练前', '训练后', '未来迁移')
    pattern = re.compile(r'^(' + '|'.join(re.escape(k) for k in keys) + r')[:：]\s*(.*)$')
    if scope == 'project':
        # Legacy decision cards also contain learning evidence. Preserve those
        # fields as history rather than discarding them with the design.
        evidence, keep = [], False
        for line in text.splitlines(keepends=True):
            if re.match(r'^[^:：\n]+[:：]', line):
                keep = bool(pattern.match(line.rstrip('\r\n')))
            elif line.startswith('#'):
                keep = False
            if keep:
                evidence.append(line)
        return ('# Engineering decision\n\n'
                'No current design or implementation approval recorded.\n'
                'Historical learning evidence only:\n' + ''.join(evidence))
    output, learning_field = [], False
    for line in text.splitlines(keepends=True):
        match = pattern.match(line.rstrip('\r\n'))
        if match:
            output.append(match.group(1) + ': not observed\n')
            learning_field = True
        else:
            if learning_field and line.strip() and not re.match(r'^[^:：\n]+[:：]', line) and not line.startswith('#'):
                raise ResetError('Ambiguous multiline learning evidence in decisions.md; normalize it first')
            output.append(line)
            if line.strip():
                learning_field = False
    return ''.join(output)


def replacements(saved, scope):
    result = {}
    for name in NOTES:
        if name not in saved:
            continue
        text = saved[name].decode('utf-8')
        if scope == 'all':
            fresh = {
                'learner.md': '# Learner Profile\n\nLearning mode: active\nOnboarding: incomplete\nOnboarding reset: pending\n',
                'state.md': '# Training state\n\nLearning mode: active\nOnboarding: incomplete\nOnboarding reset: pending\n',
                'learning-log.md': '# Learning Progress / 学习进展\n\n',
                'project-context.md': '# Project Map\n\nNot specified / 未说明\n',
                'decisions.md': '# Engineering decision\n\nNo current design or implementation approval recorded.\n',
            }
            updated = fresh[name]
        elif name == 'learner.md':
            updated = reset_learner(text, scope)
        elif name == 'learning-log.md':
            updated = reset_log(text, scope)
        elif name == 'project-context.md':
            updated = '# Project Map\n\nNot specified / 未说明\n' if scope == 'project' else text
        elif name == 'state.md':
            updated = reset_legacy_state(text, scope)
        else:
            updated = reset_legacy_decisions(text, scope)
        data = updated.encode('utf-8')
        if data != saved[name]:
            result[name] = data
    return result


def plan(raw_project, scope='learning'):
    if scope not in ('learning', 'project', 'all'):
        raise ResetError('Unknown reset scope')
    root = project_root(raw_project)
    folder = root / '.reason-to-ship'
    saved = snapshot(folder)
    previous = read_status(saved)
    updated = replacements(saved, scope)
    material = {'project': str(root), 'scope': scope,
                'before': {k: digest(v) for k, v in saved.items()},
                'after': {k: digest(v) for k, v in updated.items()}}
    token = digest(json.dumps(material, sort_keys=True).encode('utf-8'))
    return root, folder, saved, previous, updated, token


def atomic_write(path, data):
    check_path(path, 'file')
    fd, temporary = tempfile.mkstemp(prefix='.reset-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def backup_notes(folder, saved, scope, root):
    parent = folder / 'backups'
    check_path(parent, 'directory')
    parent.mkdir(exist_ok=True)
    backup = parent / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:12])
    backup.mkdir(mode=0o700)
    hashes = {}
    for name, content in saved.items():
        destination = backup / name
        with destination.open('xb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if destination.read_bytes() != content:
            raise ResetError('Backup verification failed: ' + str(destination))
        hashes[name] = digest(content)
    manifest = {'version': 1, 'project': str(root), 'scope': scope,
                'files': hashes, 'missing': [n for n in (*NOTES, STATUS) if n not in saved]}
    atomic_write(backup / 'manifest.json', json_bytes(manifest))
    if json.loads((backup / 'manifest.json').read_text(encoding='utf-8')) != manifest:
        raise ResetError('Backup manifest verification failed')
    return backup


def reset(raw_project, scope='learning', confirm=None):
    root, folder, saved, previous, updated, token = plan(raw_project, scope)
    preview = {'status': 'preview', 'project': str(root), 'state_directory': str(folder),
               'scope': scope, 'affected_files': sorted(updated),
               'backup_files': sorted(saved), 'confirmation_token': token}
    if not any(n in saved for n in NOTES):
        return dict(preview, status='no_state', confirmation_token=None)
    if confirm is None:
        return preview
    if confirm != token:
        raise ResetError('Notes or scope changed since preview; preview and confirm again')
    lock = folder / '.reset.lock'
    check_path(lock, 'file')
    try:
        lock_file = lock.open('x', encoding='utf-8')
    except FileExistsError:
        raise ResetError('A reset lock exists; inspect the previous reset before continuing')
    backup = None
    started = False
    try:
        with lock_file:
            lock_file.write(token)
        if snapshot(folder) != saved:
            raise ResetError('Notes changed before backup; preview again')
        backup = backup_notes(folder, saved, scope, root)
        if snapshot(folder) != saved:
            raise ResetError('Notes changed during backup; nothing was reset')
        cleared = dict(previous.get('cleared', {}))
        now = datetime.now(timezone.utc).isoformat()
        for category in (('learning', 'project', 'profile') if scope == 'all' else (scope,)):
            cleared[category] = now
        status = {'version': 1, 'status': 'incomplete', 'scope': scope,
                  'backup': backup.relative_to(folder).as_posix(), 'cleared': cleared}
        atomic_write(folder / STATUS, json_bytes(status))
        started = True
        for name, data in updated.items():
            check_path(folder / name, 'file')
            if (folder / name).read_bytes() != saved[name]:
                raise ResetError('Concurrent edit detected in ' + name)
            atomic_write(folder / name, data)
            if (folder / name).read_bytes() != data:
                raise ResetError('Reset write verification failed: ' + name)
        expected = dict(saved, **updated)
        expected[STATUS] = json_bytes(status)
        if snapshot(folder) != expected:
            raise ResetError('Concurrent change detected before reset completion')
        status['status'] = 'complete'
        atomic_write(folder / STATUS, json_bytes(status))
        if (folder / STATUS).read_bytes() != json_bytes(status):
            raise ResetError('Completion marker verification failed')
        return {'status': 'complete', 'project': str(root), 'scope': scope,
                'backup': str(backup), 'affected_files': sorted(updated)}
    except (OSError, ResetError) as exc:
        phase = 'Reset incomplete; do not resume notes' if started else 'No notes reset'
        raise ResetError('%s. Backup: %s. %s' % (phase, backup or 'not completed', exc))
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--scope', choices=('learning', 'project', 'all'), default='learning')
    parser.add_argument('--confirm', help='Exact fingerprint from the confirmed preview')
    args = parser.parse_args()
    try:
        result = reset(args.project, args.scope, args.confirm)
    except (OSError, UnicodeError, ResetError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
