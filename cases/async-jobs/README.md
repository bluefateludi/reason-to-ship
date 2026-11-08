# Durable async jobs

**Problem:** A report-generating job runs for several minutes. Users must be able to check status and recover after worker restart.

**Constraints:** Work may execute twice and workers may crash; the UI should not hold a request open.

**Your task:** Start with your own rough plan. With the assistant, trace a concrete implementation path, choose a design, identify failure boundaries, and write tests if working in a repository.

**Evidence of completion:** Verify state transitions, retry/lease expiry, duplicate processing, cancellation and user-visible status.

**Learning check:** After implementing, explain one key tradeoff without copying the AI response. Record transfer only on a later real task.

[简体中文](README.zh-CN.md)
