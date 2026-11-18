# agent-toolkit

个人积累的 skill、agent 和其他可复用资源。

## 目录约定

- `skills/`：独立的 skill，每个子目录都是一个完整的 skill。
- `configs/`：工具全局配置的维护源文件；其中 `configs/codex/AGENTS.md` 用于维护 Codex 全局协作约束。
- `agents/`：独立的 agent 定义，在需要时创建。
- `prompts/`：独立的可复用提示词，在需要时创建。
- `scripts/`：管理整个仓库的脚本，在需要时创建；skill 专用脚本放在对应 skill 内。
- `docs/`：仓库使用和维护文档，在需要时创建。
- `assets/`：示例原始材料及附件，供相关实验引用。

skill 内的 `references/`、`scripts/` 等资源与 `SKILL.md` 一起维护和分发。skill 内的 `agents/` 是该 skill 的配置，与根目录下的独立 agent 定义不同。

## 资源索引

| 类型 | 名称 | 用途 | 路径 |
| --- | --- | --- | --- |
| 配置 | Codex 全局约束 | 方案讨论、技术判断和验证原则 | [configs/codex/AGENTS.md](configs/codex/AGENTS.md) |
| Skill | analyzing-kotlin-code | 沿业务与执行路径分析 Kotlin 代码，讲解影响实现的 Kotlin 特性及 Java/JVM 互操作 | [skills/analyzing-kotlin-code](skills/analyzing-kotlin-code/SKILL.md) |
| Skill | android-framework-research | 基于 Framework 源码恢复模块架构、组件关系、调用流程和设计思想 | [skills/android-framework-research](skills/android-framework-research/SKILL.md) |
| Skill | android-selinux-policy-debug | 排查 SELinux 新增类型、服务映射或 allow 规则在刷机后未生效的问题 | [skills/android-selinux-policy-debug](skills/android-selinux-policy-debug/SKILL.md) |
| Skill | android-system-service-deep-dive | 基于源码分析 AOSP System Service 的生命周期、Binder 边界、调用链与安全模型 | [skills/android-system-service-deep-dive](skills/android-system-service-deep-dive/SKILL.md) |
| Skill | clarify-prd | 提取 PRD 要求、定位歧义并维护单文档澄清记录 | [skills/clarify-prd](skills/clarify-prd/SKILL.md) |
| Skill | codebase-analysis | 分析代码库或模块并生成技术文档 | [skills/codebase-analysis](skills/codebase-analysis/SKILL.md) |
| Skill | git-commit | 按任务范围创建本地 Git 提交，保留无关修改并核实提交结果 | [skills/git-commit](skills/git-commit/SKILL.md) |
| Skill | normalize-prd | 将原始材料整理为规范化 PRD，并将澄清结论回写需求及验收预期 | [skills/normalize-prd](skills/normalize-prd/SKILL.md) |
| Skill | rigorous-tech-writing | 规范技术文章、调研报告和设计文档的表达与证据 | [skills/rigorous-tech-writing](skills/rigorous-tech-writing/SKILL.md) |

## PRD 整理与澄清

`clarify-prd` 生成原始 PRD 的补充澄清记录，适合保留原文并集中核对明确要求、歧义和待确认问题。记录按功能分组，附有来源与确认历史；Android 或车机场景可使用内置检查清单。

`normalize-prd` 生成或更新规范化 PRD，适合将背景、范围、功能、场景、交互、异常及产品验收整理到一份现行正文，并在收到答复后同步回写。可直接处理原始材料，也可结合允许使用的澄清记录，不要求先运行 `clarify-prd`。

两者均保留未决事项，不替产品补完决策；技术设计和实现计划由后续流程处理。`normalize-prd` 的设计动机与收益见 [说明文档](docs/normalize-prd.md)。

## 安装 skill

将所需的完整 skill 目录复制或链接到目标工具配置的 skills 目录，保留其中的 `SKILL.md` 和相关资源。例如，将 `skills/codebase-analysis/` 整个目录安装到目标目录，而不是只复制 `SKILL.md`。

不同工具的目录位置和发现规则可能不同，请以对应工具的配置为准；添加后确认工具能够发现该 skill。

## 维护 Codex 全局约束

以 [configs/codex/AGENTS.md](configs/codex/AGENTS.md) 为维护源文件。修改并审核后，从仓库根目录手动同步到 Codex 配置目录；仓库中的修改不会自动影响已安装的全局配置。

```bash
codex_config_dir="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_config_dir"
cp -i configs/codex/AGENTS.md "$codex_config_dir/AGENTS.md"
```

覆盖前检查目标文件是否有尚未回写仓库的修改。若目标目录存在非空的 `AGENTS.override.md`，Codex 会优先使用该文件。同步后，退出并恢复已开启的 Codex CLI 会话以确保重新加载。

此文件是待安装的全局配置，不承担本仓库根目录 `AGENTS.md` 的项目维护职责。
