---
name: android-selinux-policy-debug
description: Use when added Android SELinux types, service mappings, or allow rules do not appear on a flashed device, or access still fails after a policy change. Covers qssi/vendor split builds, firmware images, super and QFIL packages. 中文：SELinux新增未生效、策略缺失、刷机后规则没更新、服务注册或查找被拒绝。
---

# Android SELinux 新增配置未生效排查

目标是定位“源码 → 选定产品配置 → 编译产物 → 交付镜像 → 设备文件 → 内核加载策略 → 实际访问”之间已证实的差异。按现有证据选择最短路径，不必从源码依次走完全链。

脚本和参考资料的路径相对于本技能目录；实际调用脚本时解析为其绝对路径，避免在用户工程中误找同名 `scripts/`。

## 先选择分支

确认目标类型及其对象身份：Binder 服务名、属性名或文件路径；类型名与服务名不是同一概念。记录实际产品/变体、设备 serial/槽位及交付包身份，缺失信息只在影响下一步时询问。

| 已有证据或症状 | 优先动作 |
|---|---|
| 设备可读，怀疑新增类型根本不存在 | 导出运行策略并读取对应 contexts；先确认缺的是类型、映射还是授权 |
| 用户已提供刷机包，或设备离线 | 先检查交付包中相关分区，别先重编或遍历整个源码树 |
| 包内有、设备文件无 | 比较同一文件哈希，核对实际刷写包、清单、日志与启动槽位 |
| 本地新产物有、交付包无 | 差异已定位到交付之前；用各阶段输入输出记录追查具体步骤 |
| contexts 与类型看似存在，访问仍失败 | 核对精确服务名/对象标签、真实进程域及本次 AVC，再查有效权限 |
| 尚无编译产物或产品路径不清 | 先追踪所选产品的构建引用及最终变量，确认策略是否会参与构建 |

设备和镜像机制、命令见 [references/runtime-policy.md](references/runtime-policy.md) 与 [references/images-and-build.md](references/images-and-build.md)，只读当前分支需要的部分。

## 取得足以判定分支的证据

对同类文件比较，区分其来源：

- `/sys/fs/selinux/policy`：内核当前加载策略的二进制快照。
- 分区中的 CIL、`*_service_contexts`、`file_contexts`、`property_contexts`：不同用途的策略或标签输入。
- `precompiled_sepolicy`：候选预编译策略，位置及是否被加载由工程和启动匹配决定。

设备导出后可用 `scripts/inspect_policy_artifacts.py` 快速统计：

```bash
python3 scripts/inspect_policy_artifacts.py \
  --type assistant_guard_service --service assistant_guard \
  /tmp/package/vendor_sepolicy.cil \
  /tmp/package/vendor_service_contexts \
  /tmp/device/vendor_sepolicy.cil \
  /tmp/device/vendor_service_contexts \
  /tmp/device/policy
```

以上 `/tmp/...` 是说明性输入路径，替换为实际已提取的文件。脚本输出大小、SHA-256、名称字节次数、精确服务映射及相同内容分组；不解析 allow，不判断设备是否正在使用某文件。只有涉及 Binder 服务时才传 `--service`。只传小型策略文件，不传整份镜像。

- `strings`/原始字节命中只能定位名称；判断类型、属性和 allow 使用可读取该策略版本的 `seinfo`/`sesearch`。工具缺失或不支持时标为未验证，不把检索计数升级成权限结论。
- 注册常量必须与最终 contexts 的服务名精确对应。检查重复/冲突映射，及实际由哪个服务管理器读取哪个映射文件。
- 属性可能已经覆盖权限；缺少显式 `allow CLIENT TARGET` 不等于没有权限。用真实客户端域和目标类型查询，查看条件规则；再区分服务 `add/find`、Binder `call/transfer` 与接口内部 Android 权限。
- 编译策略里不保留源码行号；报告中的源码定位来自对应检出版本，不能声称从二进制反查出原文件行号。

## 只有需要时才向上游追踪

1. **构建引用**：实际 lunch 产品 → include/inherit → 策略目录变量 → Soong/Make 最终配置 → 产物。不能按路径名、组件安装位置或服务运行进程推断策略归属。
2. **分工程关系**：同一个 repo project 在 System/Vendor 下可能是独立检出；比较 remote、manifest revision、当前 HEAD 和最终构建变量，不假设自动同步。qssi 不必包含设备 Vendor 入口。
3. **交付链**：从最终刷写清单确认实际使用的镜像/分片，再查看其内容。镜像外的 out 目录或 manifest 不能代替最终包验证。
4. **启动加载**：分区文件正确但运行策略不同，检查预编译策略选择、System/Product/System_ext 哈希及启动编译日志；不要直接假定 ODM 文件就是已加载策略。

用 `rg` 对已选策略目录、构建文件和候选客户端做定向搜索，再按证据扩展；区分 tracked 源码、prebuilt 和 out。全树扫描未完成时明确搜索范围，不能报告“全工程没有其他配置”。

## 修复与构建的选择

先给出与已证实差异对应的最小修复，沿用用户已授权的范围；创建排查报告不意味着授权改源码、push 策略或刷机。

- **目录未被选定产品引用**：修正该产品入口，或在确认组件归属和可交付分区后迁移策略。
- **产物或包缺失**：核对实际构建目标、输入输出路径、合并/打包清单；新增客户端 allow 无法补回缺失的类型和服务映射。
- **有效权限缺失**：仅对确实需要调用的域补最小权限，不复制另一个服务的所有客户端授权。
- **系统侧策略迁移到 Product/System_ext private**：先确认目录被构建、策略兼容性和客户端需求；同时移动定义与映射、消除重复定义，并核对未来 Vendor 组合。不是所有系统服务都应固定迁到 Product。

构建前确认本地产品/变体、依赖和输出状态。优先现有产物比较或最小策略目标；完整构建不是每次排查的默认步骤。用户明确要求构建测试时执行相应目标。缺内核或闭源依赖导致失败，报告准确阻塞点；不为通过测试而塞入来源不明的内核或自动改无关模块。

`*-nodeps` 成功只证明现有目录能打包，目录可能不完整。只在需要隔离打包环节且范围已获授权时使用；产物标为测试用途，不能当作完整固件刷写。迁移或组合后的启动兼容性仍须实际验证。

## 结论和交付

输出以“已证实差异 → 直接证据 → 尚未确定的步骤 → 最小下一步”为主线。

- manifest revision 证明版本记录，不证明镜像内容。`build.date`、分片 mtime、固定文件系统时间不能确定单个策略文件的编译时刻。
- 同一文件 SHA-256 相同说明所采样内容相同，不证明整份镜像相同；历史设备样本不等于当前设备状态。
- 包缺新增配置能确认交付内容缺失；没有执行日志与阶段哈希时，不把缓存复用、未同步、拼错包等某个步骤认定为根因。

需要文档时使其独立可读：内嵌关键代码、命令输出、哈希对比和条件限制；完整日志/JSON 仅作可选复核资料。源码标注项目路径、版本与行号；不使用 S/V/D 路径简称，省略机器专属父目录。引用链用 ASCII 时注明相对路径基准，同级/子级省略共同父目录，跨根目录重设基准。

在报告中区分：源码已改、策略已编译、测试镜像已打包、最终交付包已核验、设备已加载、实际调用已通过；只声明有对应实测证据的状态。
