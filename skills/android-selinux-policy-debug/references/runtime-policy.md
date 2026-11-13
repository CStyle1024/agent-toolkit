# 运行策略、标签和有效权限

## 采样与身份

先 `adb devices -l` 选择目标。使用明确 serial，不能在多设备时依赖默认选择。记录采样时间、启动槽位、构建指纹及客户端域。离线可继续分析包内数据，但不能假装重新验证设备。

```bash
adb -s "$serial" shell 'id; getenforce; getprop ro.boot.slot_suffix; getprop ro.build.fingerprint; getprop ro.vendor.build.fingerprint'
adb -s "$serial" shell ps -AZ
adb -s "$serial" pull /sys/fs/selinux/policy /tmp/device-policy
```

需要读取权限。没有权限时报告并利用其他证据，不能为只读检查自动关闭 SELinux 或改变设备启动状态。进程实际域以 `ps -AZ` 等观测为准，不能从签名、包名或安装分区猜测。

从实际安装目录读取相关 contexts 和 CIL。并非所有工程都将预编译策略放在 ODM；按实际文件和 init 代码判断。比较包、设备、本地产物时标注对应文件的分区和来源。

## 二进制查询

`strings` 或字节计数只作初筛。SETools 例子：

```bash
seinfo -t assistant_guard_service -x /tmp/device-policy
sesearch --allow -t assistant_guard_service -c service_manager /tmp/device-policy
sesearch --allow -s system_server -t assistant_guard_service -c service_manager -p add /tmp/device-policy
sesearch --allow -s system_app -t assistant_guard_service -c service_manager -p find /tmp/device-policy
sesearch --allow -s system_app -t system_server -c binder -p call /tmp/device-policy
```

用实际域和类型替换例子。默认属性间接匹配很重要：不要加 `-ds/-dt` 限制后又据此宣称没有属性授权；不要将结果再按目标类型名称 grep，从而丢掉显示属性名的匹配规则。`-p add,find` 默认匹配任一权限，不能仅凭有输出就断言两个权限都允许；分别查询更清楚。条件 allow 还需确认条件值。

若解析器不支持策略版本，结果是“未解析”，不是“无规则”。不要临时依赖未经验证的 libsepol 内部结构解析器；优先使用匹配版本的现有工具或保留未知项。

参考工具官方参数：
- https://github.com/SELinuxProject/setools/blob/main/seinfo
- https://github.com/SELinuxProject/setools/blob/main/sesearch

## 服务与文件/属性映射

服务名 `assistant_guard` 与类型 `assistant_guard_service` 是两个身份：

```text
assistant_guard u:object_r:assistant_guard_service:s0
```

比对注册代码、最终生效的 service_contexts、服务管理器种类及 `service check assistant_guard`。此名称映射不由 `/sys/fs/selinux/policy` 单独提供。类型在策略中存在但映射缺失/冲突，仍可能注册失败或获得其他标签；没有日志时不臆造实际 tcontext。

对文件/属性问题分别检查最终 file_contexts/property_contexts、实际对象标签和 AVC。已经存在的文件可能保留旧标签，修改 contexts 不自动证明对象已经重标记。任何重标记和文件推送都应属于已授权修复范围。

## 从拒绝定位到具体层

优先保存与本次失败时间相符的 AVC：`scontext`、`tcontext`、`tclass`、权限、进程及对象。限制 logcat/dmesg 范围和耗时，避免全缓冲持续扫描。设备离线、历史日志或日志缺失时说明限制；没有 AVC 不等于访问已获允许。

- `service_manager add`：注册域、服务名映射、目标类型和属性。
- `service_manager find`：真实客户端域和目标标签。
- `binder call/transfer`：客户端与服务进程域；不是服务标签之间的 Binder 权限。
- Java `SecurityException`：接口内部权限、声明与实际授予；不是所有异常都属于 SELinux。

`audit2allow` 可辅助解释拒绝，但不应直接复制输出作为最终修复。窗口服务等其他服务的可访问域不等于当前服务的业务需求。

## 验收

重新获取修复后的运行策略和实际对象标签，查询相关权限，确认服务注册及目标客户端真实调用成功。在 Enforcing 下核验本次相关拒绝。仅有服务列表条目不能证明所有接口可调用。
