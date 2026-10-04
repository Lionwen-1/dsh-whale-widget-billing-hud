# 验证记录 / Validation record

测试日期 / Tested: 2026-10-04 · Windows · DSH `0.2.0-rc.2` · `dsh-whale-widget` `0.3.12`

## 当前组合 / Current combination

`dsh-damage-pulse` 已从 `4.0.11` 升到 `4.2.3`，并在 DSH 完整重启后加载。当前插件的 `module-state.json` 显示版本 `4.2.3`、`restartRequired: false`、无已卸载模块。DSH 界面出现新版计费插件的余额组件，原挂件和脚下余额框也仍显示。

`dsh-damage-pulse` was upgraded from `4.0.11` to `4.2.3` and loaded after a full DSH restart. Its module state reports version `4.2.3`, `restartRequired: false`, and no removed modules. The new billing balance component, original widget, and balance panel are visible in DSH.

| 检查 / Check | 结果 / Result |
| --- | --- |
| 对当前 desktop profile 运行 `python install.py --check` / Preflight against the current desktop profile | 通过 / Pass |
| `4.2.3` 运行载荷与计费模块清单存在，包含 `deepseek-account` 和 `/api/token-monitor/charge-events` / Native billing payload and charge endpoint present | 通过 / Pass |
| 挂件监听代码读取的事件字段与 `4.2.3` 的 `streamId`、`seq`、`events[]`、`breakdown.cacheHit/cacheMiss/output.cost` 对应 / Widget event fields match the new plugin's event shape | 通过静态核对 / Static contract check passed |
| 仓库安装器测试、Python 与 JavaScript 语法检查 / Installer tests and syntax checks | 通过 / Pass |
| 隔离目录完整安装两次，挂件宿主及前端文件哈希一致，新版计费文件哈希不变 / Two isolated installs yield identical widget hashes while the modern billing file remains unchanged | 通过 / Pass |
| DSH 完整重启后菜单显示新增的“受击动作”开关，开与关均写入磁盘设置 / New hit-reaction toggle appears after restart, and both enabled and disabled states persist | 通过 / Pass |
| 一条经用户授权的极短模型调用在账本新增 `deepseek-account`、`billingStatus: priced`、正费用记录 / One authorized short model call wrote a positively priced account-billing record | 通过 / Pass |
| 同一次调用的黑鲸挂件扣费飘字和角色晃动 / Widget floating charge text and hit movement for that call | 未捕捉到短暂动画，待可重复的界面观察 / Transient animation was not captured; repeatable visual check still pending |

## 历史问题 / Previous blocker

在同一 DSH `0.2.0-rc.2` 版本上，旧计费插件 `4.0.11` 被兼容性门禁拦截，无法生成扣费事件，因此挂件不会飘字。升到 `4.2.3` 并**完整重启 DSH** 后，兼容性门禁解除；旧进程不会因安装完成自动加载新版插件。

On DSH `0.2.0-rc.2`, the older billing plugin `4.0.11` was blocked by DSH's compatibility gate, so it could not produce charge events. Upgrading to `4.2.3` and **fully restarting DSH** removes this blocker; installing files alone does not replace the plugin in an already running host process.

`4.2.3` 原生支持 DSH 账号态的计费资格和扣费事件。本仓库安装器对该版本只进行预检，不改它的打包运行载荷。对旧 DSH `0.1.7-rc.2` 的 `4.0.11` 补丁路径继续保留。演示图使用虚构数值，GIF 仍为示意动画，不作为运行时验证证据。

Version `4.2.3` natively supports DSH account billing and charge events. This installer checks, but never patches, its packaged runtime. The legacy `4.0.11` patch path remains available for DSH `0.1.7-rc.2`. Demo media uses fictional values and does not count as runtime test evidence.

新版计费插件额外的蓝发角色通过它自己的“显示鲸鱼娘”菜单开关关闭，计费模块保留。仓库只实现当前黑鲸挂件上的可选受击动画，不包含蓝发角色或其素材。The billing plugin's extra blue-haired character was hidden with its own “Show Whale Girl” menu toggle while billing stayed enabled. This repository only implements an optional reaction on the current whale widget and contains none of that extra character's assets.
