# my-skills

个人积累的 skill、agent 和其他可复用资源。

## 目录约定

- `skills/`：独立的 skill，每个子目录都是一个完整的 skill。
- `agents/`：独立的 agent 定义，在需要时创建。
- `prompts/`：独立的可复用提示词，在需要时创建。
- `scripts/`：管理整个仓库的脚本，在需要时创建；skill 专用脚本放在对应 skill 内。
- `docs/`：仓库使用和维护文档，在需要时创建。
- `docs/experiments/`：Skill 实验的输入、输出、评估及迭代记录。
- `assets/`：示例原始材料及附件，供相关实验引用。

skill 内的 `references/`、`scripts/` 等资源与 `SKILL.md` 一起维护和分发。skill 内的 `agents/` 是该 skill 的配置，与根目录下的独立 agent 定义不同。

## 资源索引

| 类型 | 名称 | 用途 | 路径 |
| --- | --- | --- | --- |
| Skill | codebase-analysis | 分析代码库或模块并生成技术文档 | [skills/codebase-analysis](skills/codebase-analysis/SKILL.md) |
| Skill | clarify-prd | 提取 PRD 要求、定位歧义并维护单文档澄清记录 | [skills/clarify-prd](skills/clarify-prd/SKILL.md) |
| Skill | normalize-prd | 将原始材料整理为规范化 PRD，并将澄清结论回写需求及验收预期 | [skills/normalize-prd](skills/normalize-prd/SKILL.md) |
| Skill | rigorous-tech-writing | 规范技术文章、调研报告和设计文档的表达与证据 | [skills/rigorous-tech-writing](skills/rigorous-tech-writing/SKILL.md) |

## PRD 整理与澄清

`clarify-prd` 生成原始 PRD 的补充澄清记录，适合保留原文并集中核对明确要求、歧义和待确认问题。记录按功能分组，附有来源与确认历史；Android 或车机场景可使用内置检查清单。

`normalize-prd` 生成或更新规范化 PRD，适合将背景、范围、功能、场景、交互、异常及产品验收整理到一份现行正文，并在收到答复后同步回写。可直接处理原始材料，也可结合允许使用的澄清记录，不要求先运行 `clarify-prd`。

两者均保留未决事项，不替产品补完决策；技术设计和实现计划由后续流程处理。

## 实验材料

- [部分答复更新样例](docs/experiments/clarify-prd-update/)演示需求确认后的增量更新。

实验样例用于说明澄清状态和确认记录的维护方式，不代表真实产品需求已获确认。

## 安装 skill

将所需的完整 skill 目录复制或链接到目标工具配置的 skills 目录，保留其中的 `SKILL.md` 和相关资源。例如，将 `skills/codebase-analysis/` 整个目录安装到目标目录，而不是只复制 `SKILL.md`。

不同工具的目录位置和发现规则可能不同，请以对应工具的配置为准；添加后确认工具能够发现该 skill。
