# my-skills

个人积累的 skill、agent 和其他可复用资源。

## 目录约定

- `skills/`：独立的 skill，每个子目录都是一个完整的 skill。
- `agents/`：独立的 agent 定义，在需要时创建。
- `prompts/`：独立的可复用提示词，在需要时创建。
- `scripts/`：管理整个仓库的脚本，在需要时创建；skill 专用脚本放在对应 skill 内。
- `docs/`：仓库使用和维护文档，在需要时创建。

skill 内的 `references/`、`scripts/` 等资源与 `SKILL.md` 一起维护和分发。skill 内的 `agents/` 是该 skill 的配置，与根目录下的独立 agent 定义不同。

## 资源索引

| 类型 | 名称 | 用途 | 路径 |
| --- | --- | --- | --- |
| Skill | codebase-analysis | 分析代码库或模块并生成技术文档 | [skills/codebase-analysis](skills/codebase-analysis/SKILL.md) |

## 安装 skill

将所需的完整 skill 目录复制或链接到目标工具配置的 skills 目录，保留其中的 `SKILL.md` 和相关资源。例如，将 `skills/codebase-analysis/` 整个目录安装到目标目录，而不是只复制 `SKILL.md`。

不同工具的目录位置和发现规则可能不同，请以对应工具的配置为准；添加后确认工具能够发现该 skill。
