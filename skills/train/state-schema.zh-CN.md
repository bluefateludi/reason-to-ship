# 最简学习状态

在当前 Git 项目里使用 `.reason-to-ship/state.md` 和 `decisions.md` 两个本地 Markdown 文件。创建之前先征得用户同意，不自动更改 `.gitignore`。不保存账号、密钥、原始对话全文或隐私代码，也不跨仓库或符号链接读取。

- `state.md`：`Learning mode: active` 等激活标志、当前任务、语言、待办、观察到的学习证据。仅维护简短快照。
- `decisions.md`：当前真实任务的目标、备选方案、执行链路、异常、测试证据、待授权范围，以及训练前后观察。

决策状态必须明确区分 `proposed`（提出）、`confirmed`（确认）、`implemented`（已实现）、`verified`（已验证）。重启不能自动推进状态。旧记录变长时，须取得同意后再合并压缩。Hook 永远只输出固定长度的恢复提示，不读取整份决策历史。
