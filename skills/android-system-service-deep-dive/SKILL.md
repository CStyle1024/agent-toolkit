---
name: android-system-service-deep-dive
description: Use when an Android Framework engineer asks for source-grounded understanding, tracing, explanation, or documentation of an AOSP System Service or Framework Service, including SystemServer lifecycle, Binder/API boundaries, state ownership, end-to-end call flows, concurrency, identity and security, multi-user behavior, cross-service dependencies, native boundaries, dumpsys, settings, or configuration.
---

# Android System Service Deep Dive

## 概览

基于当前源码仓库恢复 System Service 的真实运行模型。优先回答“系统实际上如何工作”，不要把 Android 通用知识、历史版本经验或类名联想写成当前实现事实。

## 工作边界

默认只交付源码分析报告。不要主动给出 patch、修改点、接口设计、安全策略插入或实现方案。

若用户请求新增功能、改变行为、选择拦截点、定制策略或代码实现：

1. 将请求归类为 Requirement Customization。
2. 保留已经通过源码确认的分析结果。
3. 若 `android-system-service-customization` 可用，切换到该 Skill；否则明确说明当前 Skill 只覆盖分析，并请求使用相应定制流程。
4. 不要在分析报告中附带“修改指南”来绕过边界。

## 不可破坏的证据契约

为关键结论标记证据等级：

- **已确认**：当前仓库的源码直接支持；给出文件、类、方法或字段，尽可能附行号。
- **推断**：由已确认结构推导；明确写出推断依据与验证方法。
- **未验证**：缺少源码、版本、生成代码、native/HAL 实现或运行时信息；不要补全成事实。

如果当前目录不是目标 AOSP 源码树，或无法确定实际版本/实现，先说明限制并列出需要的源码或 revision。可以给调查步骤和报告骨架，但不得伪造调用链。

## 核心原则

1. **Source First**：以当前仓库为准；发现多个同名实现、Mainline 模块或 legacy 实现时，确认构建实际选择的版本。
2. **Call Flow First**：从调用者追到真正执行者，标记进程、Binder、线程、身份和关键状态变化。
3. **State Before Methods**：先恢复状态所有权、维度、生命周期和锁，再解释单个方法。
4. **Scope Control**：先建整体模型，再深入 2～4 条代表性业务链；将其余大型子系统列为 Further Deep Dive。

## 分析工作流

### 1. 固定范围与源码基线

确认：

- 服务主体类与用户真正指定的子问题
- 当前分支、manifest/revision、Android 版本和本地修改（可获取时）
- 同名实现、模块化实现、生成代码和 legacy 分支
- 分析对象是否运行在 `system_server`、其它 Framework 进程或 native 进程

用户只给类名时，分析当前仓库实际使用的实现。不要擅自扩大到整个 Android 子系统。

### 2. 发现入口与生命周期

先用 `rg` 定位，不要从超大 Service 类首行顺序阅读：

```bash
rg -n "class <Service>|<Service>\\.Lifecycle|new <Service>" .
rg -n "publishBinderService|ServiceManager\.addService|LocalServices\.addService" .
rg -n "interface I.*<Stem>|<Stem>ManagerInternal|<Stem>Manager" .
```

恢复：

- `SystemServer` 的创建位置和 bootstrap/core/other 阶段
- constructor、`onStart()`、`onBootPhase()`、`systemReady()`/`systemRunning()`
- user、display、boot-completed 生命周期回调
- Lifecycle wrapper、真实实现、Binder 发布与 LocalService 发布之间的关系

### 3. 建立架构、API/Binder 与状态模型

只保留核心组件：service facade、Binder server、policy、controller、connection/session、state、dispatcher、observer、callback、internal service。

对每个核心组件记录：源码路径、职责、创建者、持有者、生命周期、关键依赖、主要线程和保护锁。

恢复以下边界；某层不存在时明确说明：

```text
Framework API / Manager
  -> Binder AIDL / Stub
  -> System Service
  -> Internal components / LocalServices
  -> callback or reverse Binder
```

识别 global、per-user、per-display、per-window、per-process、per-UID、connection/session/token/record 等状态。对每个核心状态回答：谁创建、谁持有、何时清理、按什么维度索引、什么锁保护、谁读写、与其它状态如何关联。

### 4. 追踪代表性端到端调用链

默认选择 2～4 条，覆盖最相关的组合：

- App → `system_server` 的主要入口
- `system_server` → App/其它进程的反向调用
- 关键状态变化或生命周期流程
- 权限或身份敏感流程

每条链都写明：业务目的、入口、逐级 caller/callee、同步/异步边界、进程、Binder 两端、线程切换、状态读写、callback、失败路径与返回路径。

使用下面的证据写法；类名仅表示格式：

```text
[App process] XxxManager.request()                         [已确认: path:line]
  ↓ Binder: IXxxManager
[system_server / Binder thread] XxxManagerService.request [已确认: path:line]
  ├─ enforce...()                                         [已确认: path:line]
  ├─ synchronized (mLock): read/update mUserStates        [已确认: path:line]
  ├─ Binder.clearCallingIdentity()                        [已确认: path:line]
  ↓ Handler / LocalServices / nested Binder
[Target process] ICallback.onResult()                     [已确认: path:line]
```

同时解释 `Binder.getCallingUid/Pid()`、userId、`clearCallingIdentity()`/`restoreCallingIdentity()` 与 nested Binder call。不要只根据方法参数推断调用身份。

### 5. 审计并发、安全与系统边界

并发模型至少覆盖：Binder thread、main looper、Handler/HandlerThread、Executor/thread pool、callback/native thread，以及切线程原因。

锁分析至少覆盖：

- `synchronized`、`@GuardedBy`、显式锁保护的状态
- lock hierarchy
- `lock → Binder`、`lock → callback`、`lock A → lock B`
- 是否复制状态后解锁再外调

只在源码支持时报告死锁、重入、优先级倒置或 Binder starvation 风险。

安全模型按实际入口追踪 permission、UID/PID、package↔UID 绑定、AppOps、calling/current/target user、跨 user、role/device policy/user restriction、shell/root/system UID 特例，以及相关 SELinux/native 边界。

### 6. 补齐依赖、native 与可观测接口

区分跨服务关系的机制：ServiceManager Binder、LocalServices、直接引用、listener/callback、broadcast、ContentObserver。只展开理解当前服务必需的部分。

调用进入 native/JNI/HAL 时，追到足以说明边界和责任的位置；无关的底层细节在边界停止。

检查 `dumpsys`、ShellCommand、Settings、DeviceConfig、SystemProperties、ContentObserver、BroadcastReceiver、PackageMonitor：说明配置来源、读取/更新时机、修改权限和可观察状态。

### 7. 形成报告并做证据回查

使用 [references/report-template.md](references/report-template.md) 组织输出。根据服务特征省略明确不适用的章节，不要为了模板机械填充。

回查每条关键结论：

- 是否能从结论跳回源码证据
- 是否混淆 framework API、Binder server、LocalService 与真正执行者
- 是否遗漏进程、身份、线程或状态变化
- 是否把推断写成事实
- 是否越界进入需求定制

需要逐阶段检查项时，读取 [references/analysis-checklist.md](references/analysis-checklist.md)。分析 Accessibility 相关服务时必须读取其中的 Accessibility 专项检查。

## 图表契约

最终报告中的每个逻辑图必须相邻提供 Mermaid 与语义等价的 PlantUML。先输出 Mermaid fenced code block，再紧跟 PlantUML fenced code block；不要用不同范围的两张图满足形式要求。

| 逻辑图 | Mermaid | PlantUML | 最低要求 |
|---|---|---|---|
| 系统架构/跨服务依赖 | `flowchart` | component diagram | 标明进程边界 |
| 核心组件关系 | `classDiagram` | class diagram | 只展示少量核心类，避免类海 |
| 调用时序 | `sequenceDiagram` | sequence diagram | participant 名称包含所属进程 |
| 启动或复杂决策流程 | `flowchart` | activity diagram；组件关系为主时用 component diagram | 仅在流程确实需要图示时使用 |

每对图保持相同的核心节点、类或 participant，相同的进程边界、箭头方向、调用顺序、同步/异步语义和证据状态。只允许为适应语法调整标签或布局。

每条代表性调用链通常配一对紧凑时序图；结构简单时可以合并逻辑视图，但合并后的 Mermaid 与 PlantUML 仍须一一对应。

## 快速参考

| 问题 | 必须找到的证据 |
|---|---|
| 服务从哪里启动？ | `SystemServer`/Lifecycle 创建点、boot phase、publish 点 |
| API 如何进入服务？ | Manager、AIDL、Stub 实现、进程边界 |
| 谁真正执行？ | 完整 caller/callee 链和最终执行对象 |
| 状态在哪里？ | owner、索引维度、创建/清理点、读写点 |
| 什么保护状态？ | lock、thread confinement、Handler/Executor |
| 调用者是谁？ | UID/PID/user/package 校验和 identity 切换 |
| 还依赖谁？ | Binder/LocalServices/listener 等具体依赖机制 |
| 如何观察或配置？ | dumpsys、Shell、Settings、DeviceConfig、properties |

## 常见错误

| 错误 | 修正 |
|---|---|
| 用通用 Android 知识描述当前分支 | 重新定位当前构建实际引用，并标注证据等级 |
| 罗列类和方法但没有调用关系 | 选择业务入口，逐箭头追踪到真正执行者和返回路径 |
| 根据类名推断职责 | 检查 callers、callees、字段用法和构造/持有关系 |
| 把所有组件放进 `system_server` | 为每个 participant 标注真实进程与 Binder 边界 |
| 看到 permission check 就结束安全分析 | 继续检查 UID/package/user/AppOps/identity 与特殊调用者 |
| 看到锁就断言死锁 | 先恢复锁顺序、外调位置和可重入路径，再报告证据与风险 |
| 对 AMS/WMS/PMS 无边界展开 | 深入 2～4 条核心链，其余列为 Further Deep Dive |
| 在分析报告中附加修改方案 | 切换到 Requirement Customization 流程 |
