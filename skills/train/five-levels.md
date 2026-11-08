# Five lenses × three evidence stages / 五层追问 × 三阶段证据

## Five lenses / 五层
1. **Why / 问题与目标**: what is broken or missing; what observable outcome proves success?
2. **Options / 方案与取舍**: why choose this approach over alternatives, under which constraints?
3. **Flow / 代码与数据链路**: which components/files run, where data changes, and how to verify the path?
4. **Failures / 异常与边界**: retries, side effects, idempotency, races, authorization, timeouts, recovery?
5. **Evidence / 生产验证与沟通**: tests, metrics, compatibility, rollout, rollback, concise explanation?

Only cover the lenses relevant to the change. Return to a gap when real implementation reveals it; do not mechanically march 1→5 or multiply them into fifteen questions.

## Three evidence stages / 三阶段
- **Guided / 引导完成**: user improves a design with coaching. Note exactly what prompt was needed.
- **Independent / 独立解释**: user states a rationale *without being given the answer in that turn*. This is evidence of reasoning, not permanent mastery.
- **Transfer / 迁移应用**: in a later authentic task with different conditions, user independently recognizes an applicable pattern. Do not schedule an artificial quiz.

Record baseline (before), observed reasoning (after), evidence source and uncertainty. An AI explanation or user approval is **not** demonstrated understanding. Keep records concise. A missing transfer event is not failure.
