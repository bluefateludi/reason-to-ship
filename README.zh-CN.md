# Reason to Ship 🚢

**独立思考，以证据交付。**

[English](README.md) · [工程案例库](cases/README.md)

这不是一个每天布置学习任务的考试工具。你带来一个真实的 Bug、需求或者设计问题，AI 用最关键的问题引导你思考，确认方案后辅助写代码、运行测试，并帮助你形成可迁移的工程判断。

## Claude Code 本地启动

```bash
claude --plugin-dir /你的绝对路径/reason-to-ship
```

在 Claude Code 输入 `/reason-to-ship:train`。Hooks 使用 Python 3.8+，无需数据库或账号。

`--plugin-dir` 应指向包含 `.claude-plugin` 的目录。Hook 使用 Bash（Windows 使用 Git Bash），依次检查 `python3`、`python`、`py -3` 是否满足 Python 3.8+。均不可用时向标准错误输出提示并跳过恢复，不阻塞会话。

## 使用节奏

**理解问题 → 比较方案 → 走通代码链路 → 考虑异常 → 验证交付。** 五层只是内部检查角度，不会强迫用户回答五道题。每次最多追问一个关键决策；不知道时可以要求解释，也可以直接请求实现。

学习证据分为三种：在引导下完成、独立解释、未来真实任务中的迁移应用。第三种不作为本次交付的阻塞条件。不能把 AI 的解释或用户的同意记成用户已经掌握。

## 学习连续性

可选的 `.reason-to-ship/state.md` 和 `decisions.md` 仅保存简短进度与当前决策，不记录聊天全文。只读 SessionStart Hook 在启动、恢复或压缩上下文后提醒 AI 继续，避免把未批准的设计误判为批准。请不要把个人学习状态提交进公开仓库。

## v0.1 范围

一个 Claude Code Skill、五个原创中英双语案例、只读 Hooks、单元测试与人工对话测试清单。暂不包含 Codex 完整适配、Web 服务、积分系统或独立案例网站。

## 测试

```bash
python -B -m unittest discover -s tests -v
```

如果系统的 Python 3 命令是 `python3`，请使用该命令。Windows 缺少创建符号链接权限时，对应集成测试会明确标记为跳过，而非通过。

**当前限制：** 自动测试只能验证 Hook 等程序行为，不能证明用户真的提升能力。真实 CLI 已识别插件和训练命令，但对话验收尚未完成，详见[验证记录](tests/validation-2026-11-08.md)。
