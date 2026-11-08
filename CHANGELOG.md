# Changelog / 更新记录

## v0.2.0 — 2026-11-08

### Added / 新增

- Default companion-style guidance during real project design, with experience-aware onboarding and optional preferences. / 在真实项目设计中默认陪伴式引导，按经验调整解释，支持默认设置和跳过。
- Three project-local records: `learner.md`, `learning-log.md`, `project-context.md`. Separate self-reported experience from observed reasoning and preserve pending decisions. / 三份档案分别保存画像、学习证据与项目上下文，区分自述和观察证据，保留待确认事项。
- Scoped reset for learning only (default), project context only, or all records, with a confirmed preview, verified backup, content-bound confirmation and interruption guards. / 重置支持仅学习、仅项目或全部，先预览确认，再备份校验，记录变化或中断时不误报成功。
- Claude Code `/reason-to-ship:reset` and the same reset workflow in standalone `.agents` and `.codex` packages. Reset requires Python 3.8+. / 新增重置入口，独立包包含同一流程。

### Compatibility / 兼容

- Existing `state.md` and `decisions.md` remain readable without automatic migration. / 兼容旧记录，不自动迁移。
- VibeWise-derived onboarding and templates include the original MIT copyright and license. / 借鉴的初始化与模板保留原作者 MIT 版权及许可。
- Install one standalone package per client and compare/back up an existing installation before replacing it. / 同一客户端只安装一份，升级前比较并备份旧技能目录。

### Validation and limits / 验证与限制

- 41 automated tests: 39 passed; 2 skipped because this Windows environment lacks symlink creation privileges. / 41 项测试，39 项通过，2 项因 Windows 符号链接权限跳过。
- Both extracted standalone packages executed preview and reset in temporary projects. Skill entrypoint validation and local resource-link checks passed. / 两种独立包均在临时项目执行过预览与重置，技能格式与资源链接检查通过。
- Native-host multi-turn dialogue, cross-client lifecycle recovery and learning outcomes remain unverified. No automatic backup-restore command is included. / 真实多轮对话、跨客户端生命周期恢复与学习效果仍待验收；尚无自动恢复备份命令。
