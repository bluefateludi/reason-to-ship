# v0.1 validation / 验证记录

Date: 2026-11-08 (Asia/Hong_Kong). Environment: Windows, Git Bash, Python 3.12, Claude Code 2.1.312.

## Automated checks

- `python -B -m unittest discover -s tests -v`: 12 tests, 11 passed, 1 skipped.
- The skipped symlink integration test requires a Windows privilege unavailable in this environment. Rejection of real symbolic links remains unverified here; a skip is not a pass.
- The new configured-command integration test first failed with `python3: command not found`, then passed after adding the launcher. It executes the command from `hooks/hooks.json` with only `python` available and asserts the active-session recovery context is returned.
- The launcher probes Python 3.8+ via `python3`, `python`, then `py -3`, without consuming the hook input. The `python` fallback is integration-tested; other launcher branches have not been separately exercised in this environment.
- `claude plugin validate .`: passed with warnings for missing author, marketplace description and icon. These listing metadata warnings do not block local validation.

## Live CLI smoke attempt

A signed-in CLI was launched with this plugin directory, the `/reason-to-ship:train` command and a Chinese request to discuss retry design without editing files. Only Read and Skill tools were exposed; MCP configuration was disabled. Native user settings and other installed plugins were still present.

- Initialization listed `reason-to-ship@inline` version 0.1.0 and `reason-to-ship:train`.
- Native startup hook events reported `EPERM` while Claude tried to create its plugin data and session environment directories outside the writable workspace. Thus the host-level hook execution was blocked before the hook script could run. The passing configured-command test does not establish successful host-level recovery.
- The run attempted to read an unrelated project referenced in the local context instead of completing the intended first-turn training check. It was stopped. The exact source of that context was not isolated.
- Plugin discovery is confirmed. First-question quality, answer leakage, multi-turn progression, bilingual equivalence and session recovery are **not accepted** on the basis of this run.
- Raw logs remain local and are intentionally excluded from this public repository because they include machine-specific context.

## Design alignment and remaining acceptance

The supplied frozen design calls for sequential five-level training and explicit Guided, Independent and Transfer stages. Current skill documents instead use five internal lenses, allow skipping, treat stages as evidence, and observe transfer only in later real tasks. This is a product decision difference, not something the launcher fix resolves. Training rules were preserved.

Next: run the scenarios in `tests/scenarios.md` in an isolated Claude Code project, without unrelated plugins or project memories; verify an active state fixture across actual resume/compact events; establish which training contract is the acceptance baseline. No full training or learning-outcome claim is made by this validation.
