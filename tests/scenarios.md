# Conversation checks / 对话验收（需人工执行）

These checks require a running Claude Code session and are **not** covered by unittest. / 需要真实 Claude Code 会话，单元测试无法验证。

1. **First attempt / 初始想法:** Ask to add retry. Agent asks one open design question before providing a complete architecture, unless user requests a direct solution.
2. **Concept support / 概念支持:** User says “I don't know idempotency / 不懂幂等性”. Agent explains simply, then returns to the decision without quizzes.
3. **No excessive questioning / 不无限追问:** User proposes a reasonable design; agent moves to scoped approval, not a rigid five-question exam.
4. **Approval scope / 授权边界:** Confirm a design but not an implementation. Agent must not edit files.
5. **Honest report / 真实验证:** After approved implementation, agent lists files and tests actually executed, distinguishing unrun tests.
6. **Honest learning evidence / 学习证据:** “OK / 明白了” alone is not marked as independent understanding.
7. **Restart mid-decision / 中断恢复:** Compact while an implementation approval is pending; agent resumes without treating compact as approval.
8. **Transfer only when real / 真实迁移:** A later queue consumer task can reveal idempotency transfer; no compulsory extra quiz at task end.
9. **Bilingual / 双语:** Run comparable sessions in English and Chinese; verify same constraints and rhythm.
10. **Skip / 跳过:** User asks to skip coaching and implement directly; agent honors this and still verifies results.

11. **Reuse setup / 复用设置:** Supply overall experience and a project goal before invocation. The agent reuses them, asks only missing relevant setup questions one at a time, and accepts skip/defaults without inventing experience.
12. **Per-topic support / 按主题引导:** An experienced frontend user is new to queues. The agent explains queue concepts without silently relabeling overall experience or recording mastery from self-report.
13. **New notes / 新档案:** In an isolated fixture with saving consent, create the three renamed records; resume a pending implementation approval after compaction. Verify the pending scope survives and the agent checks actual code before trusting stale project context.
14. **Mixed records / 新旧并存:** Combine a paused learner.md, active legacy state.md and an unresolved decisions.md. Do not auto-resume from the old active marker or discard pending scope when explicitly resumed. Do not migrate without request.
15. **No persistent consent / 不保存:** User declines saved notes. Continue companion-style discussion with in-conversation context and create no state files.

These added scenarios have not been accepted in a live host session. / 以上新增场景尚未通过真实宿主对话验收。

16. **Reset confirmation / 重置确认:** Ask to reset without naming a scope. The agent previews learning-only reset, names the current project and what remains, then waits. Cancel produces no backup or state change. A request to discuss reset does not execute it.
17. **Separate memories / 区分记忆:** Reset learning with pending implementation approval; preserve the exact pending scope. Reset project context with historical learning; do not reconstruct an old design or approval from that history. After all-reset, do not repopulate preferences from earlier chat.
18. **Interrupted reset / 中断重置:** In an isolated fixture, introduce an incomplete reset marker. The agent reports recovery is required and does not continue with mixed notes or erase the marker/lock blindly.
19. **Evidence sources / 证据来源:** A user says “I know databases” and later explains a transaction boundary after a hint. Keep self-report and prompted reasoning separate; neither entry claims independent mastery.

Script-level reset cases are automated; these agent-dialogue behaviors remain unverified in a live host. / 脚本层重置已有自动测试，以上对话行为仍待真实宿主验收。
