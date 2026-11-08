# Idempotent request handling

**Problem:** A network timeout causes a client to repeat a payment-like command. Prevent duplicate effects under concurrent requests.

**Constraints:** The client can retry with the same logical operation key; the server stores results.

**Your task:** Start with your own rough plan. With the assistant, trace a concrete implementation path, choose a design, identify failure boundaries, and write tests if working in a repository.

**Evidence of completion:** Test duplicate sequential requests, concurrent duplicates, conflicting payload under one key and recovery after a crash.

**Learning check:** After implementing, explain one key tradeoff without copying the AI response. Record transfer only on a later real task.

[简体中文](README.zh-CN.md)
