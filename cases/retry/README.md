# Retry and backoff

**Problem:** An agent intermittently fails when calling an upstream model API. Add retries without silently duplicating side effects.

**Constraints:** The API may return 429, 400 and transient 5xx responses; requests may be cancelled.

**Your task:** Start with your own rough plan. With the assistant, trace a concrete implementation path, choose a design, identify failure boundaries, and write tests if working in a repository.

**Evidence of completion:** Demonstrate error classification, bounded attempts, backoff and cancellation; test permanent error, transient recovery and exhausted retries.

**Learning check:** After implementing, explain one key tradeoff without copying the AI response. Record transfer only on a later real task.

[简体中文](README.zh-CN.md)
