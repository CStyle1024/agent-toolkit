# 镜像取证与分工程构建

## 优先最终包，避免昂贵的重编

对用户指定包先列清单/归档目录，不要先搜索整个工作盘。确认包身份和实际刷写清单；在隔离目录提取必要文件，不修改原始镜像。先检查是否已有原始产物和可用解包工具，再评估空间。

- 单独分区镜像：识别 raw ext4、EROFS、Android sparse 等格式。先 `file`/魔数判断；raw ext4 可直接读，不能一律先 simg2img。
- sparse super：先按工具支持转成 raw，再读取 LP 元数据，提取目标逻辑分区。
- QFIL 分片：结合实际使用的 `rawprogram*.xml` 和 LP 元数据定位；文件名带 super 不代表可按序直接拼接。

实际拆包工具及参数以本机 `--help` 为准，优先仓库已有 `lpdump`、`lpunpack`、`simg2img`。`lpunpack -i` 面向 LP 元数据中的额外块设备，不是任意 QFIL 分片的通用拼接开关。

## QFIL 偏移核算

需要手工还原时，先保存相关 XML 条目和 LP extent。核对 XML 的 `SECTOR_SIZE_IN_BYTES`、`start_sector`、`file_sector_offset`、`num_partition_sectors`、LUN 和分区标签。LP extent 的 sector 为 512 字节，不一定与 XML 相同。

对同一 super 所在设备，以已知分区起始字节为基准：

```text
分片在 super 中的偏移 = XML start_sector * XML sector_size - super 分区起始字节
分片读取起点 = XML file_sector_offset * XML sector_size
目标 extent 的 super 偏移 = LP physical_sector * 512
```

计算目标 extent 与各条 program 的交集，按交集分别读取和写入；验证源文件边界、覆盖区间、分区大小及对应槽位。多 extent 目标要按其逻辑次序重建。不要把 LUN 不同或另一个槽位的数据混入。

分片可能跳过 sparse/DONT_CARE 区域。未覆盖区间先确定是否由已知稀疏语义解释，不能无条件当成“数据完整”，也不能未经核实填零。保持稀疏输出以节约磁盘。

## 从文件系统提取策略

raw ext4 示例（debugfs 默认只读，不加 `-w`）：

```bash
debugfs -R 'ls -l /etc/selinux' vendor.raw.img
debugfs -R 'dump /etc/selinux/vendor_sepolicy.cil /tmp/vendor_sepolicy.cil' vendor.raw.img
debugfs -R 'dump /etc/selinux/vendor_service_contexts /tmp/vendor_service_contexts' vendor.raw.img
```

EROFS 用本机可用的相应只读提取工具。所有例子是说明性路径，不假设镜像属于特定项目。若 dump 工具打印错误但退出码为 0，应检查输出文件实际存在、大小与内容，而不是只看进程退出码。

按实际镜像查找 Product/System_ext/System/Vendor/ODM 的 CIL、contexts 和候选预编译策略。只检查相关分区；资源分区是否承载策略由目录与构建/挂载证据决定，不能凭镜像在 Vendor 工程生成就推断它含 Vendor 策略。

提取后使用 `scripts/inspect_policy_artifacts.py` 对明确文件比较。哈希相同只能证明文件内容相同；不同的 build.prop 不妨碍某几个策略文件相同。记录内部 build 属性和外部 mtime 时区分含义，不用它们替代内容检查。

## 构建引用追踪

沿实际选定产品检查：

```text
产品入口 / BoardConfig / inherit-product
    -> 实际 include 与条件
    -> BOARD_VENDOR_SEPOLICY_DIRS / BOARD_SEPOLICY_DIRS
       或 PRODUCT_{PUBLIC,PRIVATE}_SEPOLICY_DIRS
       或 SYSTEM_EXT_{PUBLIC,PRIVATE}_SEPOLICY_DIRS / BOARD_ODM_SEPOLICY_DIRS
    -> 当前配置的最终 Soong/Make 变量
    -> 对应分区的策略输出
```

最终变量应对应此次 lunch、源码版本和构建时间；旧 out 配置仅是历史样本。条件、变量覆盖和 prebuilt 替换都需用实际内容确认。不要因为目录在两个检出中同名就认为两个产品都会引用。

System 服务扩展不要求创建新进程域。先确认服务进程、客户端及交付边界，再选择 private/public/Vendor 放置；迁移到 Product private 不是通用补丁。保持服务标签属性和最小客户端访问需求，定义与映射一起迁移，处理重复定义和已发布 Vendor 的兼容组合。

## 预编译策略与增量更新

查看目标版本的 init 实现及本次启动日志：候选预编译策略与 System/System_ext/Product 的策略哈希可能参与匹配，不匹配可能触发 CIL 合并编译。存在某个 ODM 文件不能证明它被加载；更新 Product 不自动证明旧 ODM 被继续使用或一定启动成功。

对比“源码 → CIL/contexts → 分区镜像 → 合并 super → QFIL 分片 → 设备文件 → 运行策略”时，找到最早的已观测差异即可缩小范围；没有对应阶段记录则保留未知环节。

## 构建与修复边界

按用户要求构建时，先确认目标、现有输出、依赖和空间。用工程本身的标准目标；不要为了排查默认启动全量构建或扫描全部外部源码。保持原构建变体，不假定 userdebug 可替代 user。

完整镜像构建依赖可能包括内核、recovery、闭源模块和签名工具。缺依赖时保存关键错误，不能把“打包失败”说成“SELinux 编译失败”。不自动修改构建配置绕过真实依赖。

nodeps 只打包已有目录，不能证明文件安装完整或固件可刷写。若获授权进行该测试，将其与正式输出明显区分，报告完整目标失败与 nodeps 成功两种状态；未经完整性、组合策略和设备验证，不作为修复固件交付。
