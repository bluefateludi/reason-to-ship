#!/usr/bin/env bash
# Probe without consuming the JSON payload on stdin. Require Python 3.8+.
hook_dir="${BASH_SOURCE[0]%/*}"
for interpreter in python3 python; do
    if command -v "$interpreter" >/dev/null 2>&1 &&
       "$interpreter" -c 'import sys; sys.exit(sys.version_info < (3, 8))' </dev/null >/dev/null 2>&1; then
        exec "$interpreter" -B "$hook_dir/session_start.py"
    fi
done
if command -v py >/dev/null 2>&1 &&
   py -3 -c 'import sys; sys.exit(sys.version_info < (3, 8))' </dev/null >/dev/null 2>&1; then
    exec py -3 -B "$hook_dir/session_start.py"
fi
printf '%s\n' 'Reason to Ship: Python 3.8+ not found; session recovery skipped.' >&2
exit 0
