---
name: android-framework-research
description: 基于 Android Framework 源码进行架构分析，恢复真实组件关系、调用流程、数据流和设计思想，所有结论必须基于源码验证，不允许猜测。
---

# Android Framework Research

# 目标
分析 Android Framework 某个模块的真实实现。
目标不是阅读源码，而是恢复 Android Framework 的真实设计。
最终输出可直接作为：
- Android 源码学习笔记
- 架构设计文档
- 公众号文章
- 技术分享材料
---

# 输入
用户需要提供以下任意一种信息：
- Framework 模块目录
- Java 包路径
- Service 名称
- 生命周期名称
- 功能模块名称

例如：
- frameworks/base/services/core/java/com/android/server/pm
- Permission Install Phase
- PermissionManagerService
- AppOpsService
- ActivityManagerService

---

# 基本原则
## 原则一：源码优先
- 所有结论必须来自源码。
- 禁止根据经验推测。
---

## 原则二：验证优先
- 调用关系必须按照以下顺序验证：
1. Debug Call Stack
2. Call Hierarchy
3. Find Usages
4. Source Code
5. 官方文档
- 不得跳过验证
---

## 原则三：调用流与数据流分离
- 调用关系与对象流转必须分别分析。
- 禁止混合到同一张图中。

---

## 原则四：所有结论必须有证据
- 如果没有源码证据, 标记为：⚠ 未验证（Unverified）
- 不要写入最终架构图。

## 原则五：优先恢复真实架构，而不是穷举代码
分析时应优先识别：
- 核心组件
- 核心调用链
- 核心数据流
- 核心对象
避免陷入工具类、辅助函数、异常处理等实现细节
目标是恢复 Android 的整体设计，而不是逐行解释源码

---

# 输出目录

在项目根目录生成：

proj_docs/

    <模块名称>/
    	research/
	docs/
		<模块名称>_doc.md
	article/
        images/
---

# 第一阶段：总体概览
## 输出目标
说明：
- 模块存在的原因
- 解决的问题
- 核心职责
- 上游模块
- 下游模块

要求：
- 不要描述源码实现。
- 重点描述设计目标。

---

# 第二阶段：总体架构
## 输出目标
恢复整个模块的总体架构

要求：
- 严格遵照源码中的关联
- 不跳过关键链路

要求生成：
- PlantUML
- Mermaid

架构必须包含：
- Application
- Framework API
- System Service
- Native
- HAL
- Kernel

列出所有核心组件, 输出表格：

|组件|职责|调用者|输出|源码位置|
|----|------|------|------|------|

同时说明：
- 为什么需要该组件。
- 为什么其它组件不能替代。
- 与其它组件的关系

建议：
调用流采用实线，数据流采用虚线
---

# 第三阶段：关键类
选择：
- 5~10 个核心类。
- 忽略工具类。

输出：
PlantUML 类图

每个类说明：
- 职责
- 源码路径（行数）
- 关键字段
- 关键方法
- 主要依赖和关联

---

# 第四阶段：典型场景
分析：
5~8 个典型场景。

例如：
- Install
- Grant
- Check
- Revoke
- Query

每个场景输出：
- 调用流程
- 数据变化
- 时序图
- 异常流程
---

# 第五阶段：调用流（Call Flow）
恢复真实函数调用关系。
所有箭头必须经过源码验证。
关键链路不能跳过。

输出：
- PlantUML 时序图
- 函数调用链

例如：
PackageManagerService

↓

InstallPackageHelper

↓

PackageParser2

↓

ParsingPackageUtils

↓

parseBaseApk()

↓

parseUsesPermission()

↓

pkg.addUsesPermission()

如果存在，则需要标注：
- Binder
- JNI
- Native
- HAL

需要：
在每个调用链下，文字说明

---

# 第六阶段：数据流（Data Flow）
恢复对象生命周期，建立真正的对象流

描述：

对象创建

↓

对象转换

↓

对象保存

↓

对象持有

↓

对象持久化

↓

对象销毁

例如：

AndroidManifest.xml

↓

ParsedUsesPermissionImpl

↓

ParsingPackage

↓

ParsedPackage

↓

Permission

↓

PermissionRegistry

数据流不能与调用流混合。

---

# 第七阶段：进程视图
描述：
- App
- system_server
- Native Service
- Binder
- HAL
- Kernel

说明：
- IPC
- Binder
- JNI
- 线程切换
---

# 第八阶段：实践验证
- 至少设计5 个实验。
- 每个实验包含：

实验目的

断点位置

观察变量

预期结果

验证结论

例如：
- 实验：增加 uses-permission
- 观察：pkg.addUsesPermission()
- 预期：Permission 加入 ParsingPackage

---

# 第九阶段：源码证据

建立源码证据表。

格式：

|编号|结论|源码位置|验证方式|可信度|
|----|------|------|------|------|


可信度：★★★★★

Debug + Call Stack ★★★★☆

Call Hierarchy ★★★☆☆

源码阅读 ★★☆☆☆

合理推断 ★☆☆☆☆

未验证

所有结论必须填写证据。

---

# 第十阶段：设计思想
分析：Google 为什么这样设计。
重点说明：
- 职责划分
- 可扩展性
- 性能
- 并发
- 对象模型
- 设计模式

回答：为什么需要。
例如权限定义时，为何需要如下类或组件：
- PackageParser2
- ParsingPackage
- PermissionRegistry
- Builder
- Immutable Object

---

# 第十一阶段：总结
输出：一页总结。

包括：
- 模块职责
- 总体架构
- 调用流
- 数据流
- 关键类
- 设计思想
---

# 图规范
所有图同时生成：
- PlantUML
- Mermaid

要求：
- 可正常渲染
- 无交叉箭头
- 无重叠
- 层次清晰
- 适合公众号排版
- 宽高比建议 3:4
- 字体大小统一

---

# 输出要求
所有 Markdown 文件统一使用：

一级标题：

# 标题

二级标题：

## 标题

三级标题：

### 标题

所有表格使用 Markdown Table。

所有代码使用 Markdown Code Block。

---

# 质量检查

输出前必须检查：

- [ ] 所有调用关系都有源码依据
- [ ] 所有数据流都有源码依据
- [ ] 所有组件职责已说明
- [ ] 调用流与数据流已分离
- [ ] Binder/JNI 已标注
- [ ] 所有图可以正常渲染
- [ ] 已生成实践验证
- [ ] 已生成源码证据表
- [ ] 已生成设计思想
- [ ] 未出现未经验证的结论

---
# 特殊要求

如果源码无法证明某个关系：

必须明确标记：⚠ 未验证（Unverified）

不得根据经验补充调用关系。

正确性优先于完整性。
如果发现已有结论与源码不一致，应以源码为准，并说明原因。
