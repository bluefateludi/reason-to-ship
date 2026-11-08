# Minimal local state / 最小本地状态

Use only two local Markdown files in the *current Git project*, in `.reason-to-ship/`. No database. In an unfamiliar project, ask before creating state or adding a `.gitignore` entry. Do not commit private state by default. Avoid credentials, private source text and transcripts. Never follow symlinks or cross repository/worktree boundaries; create state at the current Git root. No automatic migration.

**state.md** (bounded snapshot, overwrite superseded entries):
```markdown
# Training state
Learning mode: active
Language: zh-CN
Current task: agent-retry
Checkpoint: awaiting reasoning

## Observed learning
- Retry errors — guided: identified permanent 400 errors after a hint; source: current task

## Next action
- Ask user which failures are transient.
```

**decisions.md** (one active decision card; archive older cards only on user request):
```markdown
# Engineering decision
Task: agent-retry
Status: proposed
Problem: ...
Options and rationale: ...
Execution flow: ...
Failure boundaries: ...
Tests actually run: none
Pending approval: implementation of model retry layer
Baseline: ...
After: ...
Future transfer: not observed
```

`Status` must differentiate `proposed`, `confirmed`, `implemented`, `verified`. A session restart cannot advance status. Keep short summaries; if a file becomes large, summarize prior entries in place after explicit consent. The hook emits a constant-size *pointer* only and never reads whole decisions.md.
