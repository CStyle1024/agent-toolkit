# Android System Service 分析检查表

## 目录

1. 范围与源码发现
2. 生命周期
3. 架构与 Binder
4. 状态与调用链
5. 并发与锁
6. 安全与 Multi-user
7. 依赖、native 与调试
8. Accessibility 专项
9. 交付前检查

只读取与当前服务相关的检查项；不要为了逐项打勾而扩展无关范围。

## 1. 范围与源码发现

### 范围

- [ ] 记录服务名、用户关心的能力和预期分析深度。
- [ ] 记录当前源码分支/revision；无法获取时明确限制。
- [ ] 确认同名实现、模块化/Mainline 实现和 legacy 实现。
- [ ] 确认构建实际选择的实现，而不是任选搜索结果。
- [ ] 区分源码事实、合理推断和未验证信息。

### 入口文件

- [ ] 主体 Service 类与 constructor
- [ ] `SystemService`/`SystemService.Lifecycle` wrapper
- [ ] `SystemServer` 创建位置
- [ ] `publishBinderService`/`ServiceManager.addService`
- [ ] `LocalServices.addService`/Internal API
- [ ] AIDL 与生成 Stub 的实现者
- [ ] Framework Manager/API
- [ ] callback/reverse Binder AIDL
- [ ] 相关 `Android.bp` 与测试模块（需要理解构建或验证时）

先建立：

```text
Framework API
  -> Manager
  -> Binder interface
  -> Binder server / System Service
  -> internal components
```

某层不存在时写明“不存在”，不要强行套层次。

## 2. 生命周期

- [ ] 判断 bootstrap/core/other service 启动阶段。
- [ ] 追踪 constructor 的依赖注入和早期副作用。
- [ ] 追踪 `onStart()` 发布的 Binder/LocalService。
- [ ] 追踪 `onBootPhase()` 各阶段行为。
- [ ] 查找 `systemReady()`、`systemRunning()` 或等价回调。
- [ ] 查找 boot completed 行为。
- [ ] 查找 user start/unlock/switch/stop/remove 回调。
- [ ] 查找 display add/change/remove 回调。
- [ ] 说明 wrapper 与真实 Service implementation 的持有关系。
- [ ] 说明注册 observer/listener/receiver 的时机和清理时机。

输出以当前源码验证的启动链，例如：

```text
SystemServer
  -> start...Services()
  -> XxxManagerService.Lifecycle
  -> XxxManagerService()
  -> onStart()
  -> publishBinderService()
```

## 3. 架构与 Binder

### 核心组件

只纳入真正承担职责或拥有状态的组件：

| 项目 | 要回答的问题 |
|---|---|
| 类/文件 | 定义在哪里？ |
| 职责 | 通过哪些调用和字段得到验证？ |
| 创建/持有 | 谁创建，谁长期持有？ |
| 生命周期 | 创建、激活、清理时机？ |
| 依赖 | Binder、LocalServices 或直接引用？ |
| 线程 | Binder/main/Handler/Executor？ |
| 锁 | 哪个锁保护哪些字段？ |

不要把常量类、简单 DTO、纯工具类列为核心架构。

### Binder/API

- [ ] Framework API/Manager 的公开入口
- [ ] AIDL 接口与 Binder 服务名
- [ ] Service 直接 extends Stub 或单独 BinderService
- [ ] Internal API 与 `LocalServices`
- [ ] callback/reverse Binder
- [ ] synchronous、oneway 与异步结果语义
- [ ] death recipient、RemoteCallbackList 与断连清理
- [ ] parcelable/token/session 的所有权与生命周期

对关键 Binder 入口记录：

| 字段 | 内容 |
|---|---|
| 客户端入口 | Manager/API 调用者 |
| 服务端实现 | Stub 方法与实际委托对象 |
| calling identity | UID、PID、user、package |
| identity change | clear/restore 位置与原因 |
| 状态读写 | 字段、owner、锁 |
| 外部调用 | Binder/LocalServices/callback |
| 失败语义 | exception、默认值、静默拒绝、超时 |

## 4. 状态与调用链

### 状态模型

寻找但不要仅凭命名下结论：

```text
*UserStates, *Connections, *Clients, *Sessions, *Records,
*Processes, *Windows, SparseArray, ArrayMap, ArraySet,
RemoteCallbackList
```

对每个核心状态确认：

- [ ] owner 与创建者
- [ ] global/per-user/per-display/per-window/per-process/per-UID 维度
- [ ] key/token/record 的含义
- [ ] 创建、更新、持久化和清理事件
- [ ] 锁或 thread confinement
- [ ] readers/writers
- [ ] 与其它状态对象的关系
- [ ] 用户/显示/进程死亡后的回收行为

### 调用链选择

从以下类型选择 2～4 条最能解释服务的流程：

- [ ] App → `system_server` 主入口
- [ ] `system_server` → App/远端进程 callback
- [ ] 核心状态变化
- [ ] service/process death 与恢复
- [ ] user/display 生命周期
- [ ] 安全敏感或跨 user 流程

每条链确认：

- [ ] 业务目的与触发条件
- [ ] 完整 caller/callee 与最终执行者
- [ ] 每个进程和 Binder 两端
- [ ] Binder thread、Handler、Executor 等线程切换
- [ ] identity 变化
- [ ] 状态字段读写和锁变化
- [ ] callback/返回路径
- [ ] 异常、超时、死亡或清理路径
- [ ] 每个关键箭头的源码依据

## 5. 并发与锁

### 线程

- [ ] `system_server` main looper
- [ ] Binder thread pool
- [ ] `Handler`/`HandlerThread`
- [ ] `Executor`/thread pool
- [ ] framework callback thread
- [ ] remote process thread
- [ ] native thread（如适用）
- [ ] 每次切线程的目的：序列化、避免持锁外调、延迟、IO 或性能隔离

### 锁

- [ ] `synchronized` monitor
- [ ] `@GuardedBy`
- [ ] `ReentrantLock`/`ReadWriteLock`
- [ ] lock hierarchy
- [ ] `lock → Binder`
- [ ] `lock → callback`
- [ ] `lock → other System Service`
- [ ] `lock A → lock B`
- [ ] copy-under-lock / call-after-unlock 模式
- [ ] Binder re-entry 与 death callback

报告“可能风险”时同时给出触发路径和源码证据。没有完整路径时保留为待验证问题。

## 6. 安全与 Multi-user

### 安全链

- [ ] `check/enforceCallingPermission`
- [ ] `Binder.getCallingUid/Pid()`
- [ ] `UserHandle.getAppId/getUserId`
- [ ] package 与 UID 绑定校验
- [ ] AppOps note/start/check
- [ ] role、DevicePolicy、user restriction
- [ ] calling identity clear/restore
- [ ] nested Binder 后看到的身份
- [ ] shell/root/system UID 特例
- [ ] native/HAL 路径上的 SELinux（如相关）

不要只确认“存在 permission check”；继续确认调用者是否可信、数据范围、跨 user 规则和拒绝方式。

### Multi-user

- [ ] calling/current/target/system user
- [ ] profile/managed profile/visible user
- [ ] `handleIncomingUser`/等价解析
- [ ] `USER_ALL`/`USER_CURRENT`/`USER_CURRENT_OR_SELF`
- [ ] global service + per-user state、真正 per-user 或 hybrid 模型
- [ ] user switch/unlock/stop/remove 对状态和 callback 的影响

## 7. 依赖、native 与调试

### Cross-service

对每个关键依赖标注一种机制：

- ServiceManager Binder
- LocalServices/Internal API
- 直接对象引用
- callback/listener
- broadcast
- ContentObserver

不要递归展开与当前服务核心机制无关的依赖实现。

### Native/JNI/HAL

- [ ] Java/JNI 边界
- [ ] native service 或 native Binder
- [ ] HAL 接口
- [ ] identity/security 边界
- [ ] 分析停止位置及其理由

### 配置和可观测性

- [ ] `dumpsys` 与 dump 内容
- [ ] `ShellCommand` 入口和主要命令
- [ ] `Settings.Secure/Global/System`
- [ ] `DeviceConfig`
- [ ] `SystemProperties`
- [ ] ContentObserver/BroadcastReceiver/PackageMonitor
- [ ] 配置的用户作用域、读取时机、动态更新和修改权限

## 8. Accessibility 专项

明确区分至少三个进程域：

```text
AccessibilityService process
system_server
target application process
```

不要把 `AccessibilityInteractionController`、`ViewRootImpl`、`View` 或 `AccessibilityNodeProvider` 自动归入 `system_server`。

分析 AccessibilityNodeInfo/交互流程时，将以下类视为搜索检查点，而不是预设调用链：

- `AccessibilityService`
- `AccessibilityInteractionClient`
- `IAccessibilityServiceConnection`
- `AbstractAccessibilityServiceConnection`
- `AccessibilityWindowManager`
- `RemoteAccessibilityConnection`
- `IAccessibilityInteractionConnection`
- `ViewRootImpl`
- `AccessibilityInteractionController`
- `AccessibilityNodeProvider`
- `View`

逐箭头验证当前版本实际经过的对象、窗口解析、连接对象、回调和结果返回路径。

额外确认：

- [ ] accessibility service 的 bind/connected/death/rebind 状态
- [ ] windowId 到目标 connection 的解析
- [ ] 事件/节点可见性与敏感内容策略
- [ ] service process 与 target app process 的 callback 线程
- [ ] user switch、profile 和多显示行为
- [ ] input filter、magnification 或手势链（仅在目标范围相关时）

## 9. 交付前检查

- [ ] 每条关键结论能跳回源码证据。
- [ ] 每条代表性流程标明进程、Binder、线程、状态和身份。
- [ ] 核心状态列明 owner、生命周期和锁。
- [ ] 图中的 participant 与实际进程一致。
- [ ] 推断和未验证项没有伪装成事实。
- [ ] 大型服务只深入约定的 2～4 条核心链。
- [ ] 报告没有混入 patch、修改点或实现方案。
- [ ] 每个逻辑图都按 Mermaid → PlantUML 顺序相邻配对。
- [ ] 每对图的核心节点、进程边界、箭头方向、调用顺序和证据状态语义一致。
- [ ] 给出按价值排序的源码阅读路线。
