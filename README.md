# Reason to Ship 🚢

**Think independently. Ship with evidence.**

[中文说明](README.zh-CN.md) · [Cases / 案例](cases/README.md)

**Standalone installs:** [.agents and .codex skill ZIPs](INSTALL.md) include all five bilingual cases. These preview packages resume state when invoked and do not install the Claude SessionStart hook.

Reason to Ship is a small Claude Code learning plugin for *real engineering work*. It builds a repeatable habit: understand the problem → weigh options → trace code and data → consider failures → verify the result. AI can write the implementation; the engineer owns the decisions.

## Install locally (Claude Code)

```bash
claude --plugin-dir /absolute/path/to/reason-to-ship
```

In Claude Code: `/reason-to-ship:train`. Marketplace installation can be configured after publishing the repo. Requires Python 3.8+ for the optional read-only SessionStart hook.

Point `--plugin-dir` at the folder containing `.claude-plugin`. The hook uses Bash (Git Bash on Windows) and tries `python3`, `python`, then `py -3`, checking for Python 3.8+. If none is available, it reports the missing dependency on stderr and skips recovery without blocking the session.

## In practice

**You:** Add retries to this model request.

**Skill:** Which errors should be retried? If a parameter is invalid, would sending the same request again help?

The assistant then helps inspect the real implementation, agree on boundaries, implement an approved change, run tests and explain the result. Five design lenses are **not** five obligatory questions. The learner can skip or request direct implementation.

## Learning continuity

Optional `.reason-to-ship/state.md` and `decisions.md` in each project hold a small snapshot and an active decision. The Claude Code SessionStart hook restores a pointer after startup, resume, clear, compact or fork. It is read-only, bounded and respects repository boundaries. Project learning state is intended to stay uncommitted.

## First release

- One bilingual core skill, five engineering lenses, guided → independent → later authentic transfer evidence
- Five original bilingual scenario briefs: retry, idempotency, cache consistency, rate limiting, async jobs
- Claude Code hook plus Python unit tests, manual dialogue evaluation checklist

**Limitations:** Automatic tests cannot prove learning outcomes. Standalone skill packages are available for `.agents` and `.codex`; full Codex lifecycle integration and cross-client dialogue acceptance remain unverified. A live Claude CLI run recognized the plugin and training command, but dialogue acceptance is still incomplete. See [validation results](tests/validation-2026-11-08.md).

## Checks

```bash
python -B -m unittest discover -s tests -v
python -m json.tool .claude-plugin/plugin.json
python -m json.tool hooks/hooks.json
```

Use `python3` if your system exposes Python 3 under that name. On Windows without symlink creation privileges, the symlink integration test is reported as skipped, not passed.

## Contributing

Cases must be original or properly licensed; do not copy textbook answers. See [CONTRIBUTING.md](CONTRIBUTING.md). MIT license.
