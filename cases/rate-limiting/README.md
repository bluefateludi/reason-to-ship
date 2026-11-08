# API rate limiting

**Problem:** Protect a shared model API from bursts without starving quiet tenants.

**Constraints:** Per-tenant quotas, upstream 429 responses and multiple service replicas exist.

**Your task:** Start with your own rough plan. With the assistant, trace a concrete implementation path, choose a design, identify failure boundaries, and write tests if working in a repository.

**Evidence of completion:** Test burst allowance, concurrency, quota isolation, headers and behavior when limiter state is unavailable.

**Learning check:** After implementing, explain one key tradeoff without copying the AI response. Record transfer only on a later real task.

[简体中文](README.zh-CN.md)
