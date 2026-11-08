"""Build self-contained .agents and .codex skill ZIPs (Python 3.8+, stdlib)."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]


def payload():
    files = {'SKILL.md': (ROOT / 'packaging/skill/SKILL.md').read_bytes(),
             'LICENSE': (ROOT / 'LICENSE').read_bytes()}
    for name in ('five-levels.md', 'five-levels.zh-CN.md',
                 'state-schema.md', 'state-schema.zh-CN.md',
                 'state-templates.md', 'state-templates.zh-CN.md',
                 'personalization.md', 'personalization.zh-CN.md',
                 'THIRD_PARTY_NOTICES.md', 'reset.md', 'reset.zh-CN.md'):
        files['references/' + name] = (ROOT / 'skills/train' / name).read_bytes()
    files['references/scripts/reset_state.py'] = (ROOT / 'skills/train/scripts/reset_state.py').read_bytes()
    for path in sorted((ROOT / 'cases').rglob('*.md')):
        files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    # Normalize text so package bytes do not depend on checkout line endings.
    return {name: data.replace(b'\r\n', b'\n') for name, data in files.items()}


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    version = json.loads((ROOT / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    files = payload()
    packages = []
    for target in ('agents', 'codex'):
        archive = output / ('reason-to-ship-v%s-%s.zip' % (version, target))
        with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
            for name, data in sorted(files.items()):
                info = ZipInfo('.%s/skills/reason-to-ship/%s' % (target, name), (2026, 11, 8, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                bundle.writestr(info, data)
        packages.append(archive)
    checksums = ''.join('%s  %s\n' % (hashlib.sha256(p.read_bytes()).hexdigest(), p.name) for p in packages)
    (output / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
    return packages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    for package in build(args.output_dir):
        print(package)
