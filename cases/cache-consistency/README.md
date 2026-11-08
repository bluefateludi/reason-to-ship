# Cache consistency

**Problem:** A service updates the database while some reads still see an old Redis value. Design the freshness guarantees.

**Constraints:** Multiple instances read and write; cache expiry is available; strict serializability is not assumed.

**Your task:** Start with your own rough plan. With the assistant, trace a concrete implementation path, choose a design, identify failure boundaries, and write tests if working in a repository.

**Evidence of completion:** Show the read/write ordering, stale-read bound and race test; justify invalidation or update strategy.

**Learning check:** After implementing, explain one key tradeoff without copying the AI response. Record transfer only on a later real task.

[简体中文](README.zh-CN.md)
