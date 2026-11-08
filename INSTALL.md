# Standalone skill packages / 独立技能安装包

These v0.1.0 preview packages contain the same bilingual training skill and five cases. They do not install Claude plugins or hooks. / 两份预览安装包的训练内容相同，不安装 Claude 插件或 Hook。

They also include VibeWise-derived onboarding and state templates, renamed to `learner.md`, `learning-log.md` and `project-context.md` inside each project's `.reason-to-ship/`, with upstream MIT attribution. Legacy `state.md` and `decisions.md` remain readable without automatic migration. / 同时包含改编自 VibeWise 的双语初始化流程、三份改名档案模板与原作者 MIT 许可；兼容旧记录，不自动迁移。默认陪伴式引导，允许跳过设置，未知项记为未说明。

For a scoped reset, ask `$reason-to-ship 重置学习记录` (learning only by default), or specify project context or all records. The agent previews the scope and asks for confirmation before the bundled helper verifies a backup and applies the reset. Only reset requires Python 3.8+; installation and normal coaching do not. / 重置可选仅学习、仅项目或全部；预览确认后先校验备份再改记录，默认保留偏好、经验和项目决策。仅重置脚本需要 Python 3.8+，安装与普通使用不需要。重置指南及脚本均包含在独立包中。

## Choose one / 二选一

| Package | Extract into | Result |
| --- | --- | --- |
| [通用 .agents](dist/reason-to-ship-v0.1.0-agents.zip) | 项目根目录，或用户主目录 | `.agents/skills/reason-to-ship/SKILL.md` |
| [Codex .codex](dist/reason-to-ship-v0.1.0-codex.zip) | 用户主目录 | `.codex/skills/reason-to-ship/SKILL.md` |

优先选 `.agents`：当前 [Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)将项目级和用户级 `.agents/skills` 列为发现目录。这里的“通用”指标准 `SKILL.md` 和自包含资源；其他工具是否自动发现 `.agents` 取决于其自身支持。

`.codex` 包供仍使用 `~/.codex/skills` 的 Codex 环境使用；本机已有该技能目录，[官方 Cookbook](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)也给出 `$CODEX_HOME/skills` 用法。它不是对所有客户端版本的兼容性承诺。设置了自定义 `CODEX_HOME` 时，将包内的 `reason-to-ship` 文件夹放入 `$CODEX_HOME/skills/`。不要把自定义路径覆盖成默认路径。

Install only one copy visible to a given client to avoid duplicate skill names. / 同一客户端可发现的范围内只安装一份。

## Windows PowerShell

先从上表下载 ZIP（GitHub 文件页选择 Download raw file），或从仓库的 `dist` 目录使用。下列命令假设在仓库根目录运行。

项目级 `.agents` 安装，把路径换成你的项目：

```powershell
$projectRoot = 'D:\your-project'
if (Test-Path -LiteralPath (Join-Path $projectRoot '.agents/skills/reason-to-ship')) {
    throw 'Skill already exists. Back it up and review before replacing.'
}
Expand-Archive -LiteralPath '.\dist\reason-to-ship-v0.1.0-agents.zip' -DestinationPath $projectRoot
```

Codex 默认用户级目录：

```powershell
if ($env:CODEX_HOME -and $env:CODEX_HOME -ne (Join-Path $HOME '.codex')) {
    throw 'Custom CODEX_HOME detected. Copy the extracted skill into its skills directory.'
}
if (Test-Path -LiteralPath (Join-Path $HOME '.codex/skills/reason-to-ship')) {
    throw 'Skill already exists. Back it up and review before replacing.'
}
Expand-Archive -LiteralPath '.\dist\reason-to-ship-v0.1.0-codex.zip' -DestinationPath $HOME
```

用户级 `.agents`：将第一段的 `$projectRoot` 设为 `$HOME`。这些命令不需要 Python，也不会修改 `config.toml`、`AGENTS.md` 或现有 Hook 配置。

## macOS / Linux

在仓库根目录选择一个安装位置。`unzip -n` 不覆盖已有文件；升级前先比较、备份旧的同名技能，避免混用版本。

```bash
# Project-level shared skill
unzip -n dist/reason-to-ship-v0.1.0-agents.zip -d /path/to/your-project

# OR user-level shared skill
unzip -n dist/reason-to-ship-v0.1.0-agents.zip -d "$HOME"

# OR default Codex user directory (only when CODEX_HOME is unset/default)
unzip -n dist/reason-to-ship-v0.1.0-codex.zip -d "$HOME"
```

For a custom `CODEX_HOME`, extract to a temporary folder and copy only `.codex/skills/reason-to-ship` into `$CODEX_HOME/skills/`. Keep hidden folders visible in your file manager.

## Invoke and resume / 调用与恢复

In Codex, select `reason-to-ship` in the skills picker, or enter:

```text
$reason-to-ship 用重试案例带我做一次工程决策训练，先让我表达想法。
```

After consenting to save a checkpoint in a Git project, continue in that same project with:

```text
$reason-to-ship 读取当前项目的训练状态，继续上次尚未完成的决策。
```

If the skill is missing, confirm `SKILL.md` is directly inside `skills/reason-to-ship/`, then restart the client. Other agents may use a different invocation syntax.

恢复发生在调用技能时；不承诺启动、压缩上下文或恢复会话时自动触发。训练状态保存在当前项目，不写进安装目录。此包仍沿用 v0.1 题干和证据标准，没有新增参考答案，也没有完成跨客户端真实对话验收。

## Rebuild and verify / 构建与验证

Maintainers need Python 3.8+; users only need to extract the ZIP.

```bash
python -B scripts/build_skill_packages.py
python -B -m unittest discover -s tests -v
```

The builder uses `packaging/skill/SKILL.md`, shared five-level/state references and `cases/`; output goes to `dist/`. Two packages are deterministic for the same inputs and build runtime. [SHA256SUMS.txt](dist/SHA256SUMS.txt) records their checksums. Windows: `Get-FileHash .\dist\*.zip -Algorithm SHA256`; Linux: run `sha256sum -c SHA256SUMS.txt` from `dist`.

Package checks cover extraction layout, bundled resources, relative links and reproducibility. They do not establish host discovery or training quality. Existing Claude Hook tests remain separate, and the Windows symlink test may be skipped when creation privileges are absent.
