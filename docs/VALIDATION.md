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

---

# 2026-10 追加验证 / October 2026 follow-up

测试环境 / Environment: Windows · DSH `0.2.1-rc.2`（自动更新）· `dsh-whale-widget` `0.3.12` · `dsh-damage-pulse` `4.2.6`（由 `4.2.3` 升级）

## 被版本门禁静默拦截 / Silent version-gate block

DSH 自动更新到 `0.2.1-rc.2` 后，`dsh-damage-pulse` 在加载器里的 `rows` 为空，并报告
`incompatible-version`（插件 peer 区间只写到 `0.2.1-rc.1`）。表现：侧栏会话金额、挂件飘字消失，
`~/.dsh/data/dsh-token-monitor/usage.jsonl` 停在 `2026-10-06 02:41`。

After DSH auto-updated to `0.2.1-rc.2`, the billing plugin loaded no rows and reported
`incompatible-version` (its peer range stops at `0.2.1-rc.1`). Session costs and widget charge text
disappeared; the usage ledger froze at `2026-10-06 02:41`.

| 检查 / Check | 结果 / Result |
| --- | --- |
| 改动前备份账本与 `compatibility.json` / Ledger and compatibility file backed up first | 通过（2345 行、1.28 MB）/ Pass |
| 对 `dsh-damage-pulse@4.2.6 ↔ 0.2.1-rc.2` 授精确版本豁免（用户明确同意后）/ Exact-pair exemption with explicit user consent | 通过 / Pass |
| `remove_bundle` → `install_bundle` 升到 `4.2.6` / Upgrade path | 通过，依赖钉到精确版本 / Pass |
| 升级后 `usage.jsonl` 恢复写入 / Ledger resumed after upgrade | 通过：新增 13 条、合计 ¥0.1514，最后一条 `2026-10-17 21:46:59` / Pass |
| 计费规则继承官方价目表 / Billing rules inherit the official table | 通过：`ruleSource: official-family`，`deepseek-flash` 峰 ¥2 / 缓存 ¥0.04 / 输出 ¥8（每百万 token）/ Pass |
| `/api/token-monitor/charge-events`、`/session-costs` 路由存在 / Routes present | 通过（未鉴权 401 而非 404）/ Pass |
| 4.2.x 外观补丁只改 `CARD` 一行样式 + 语法检查 / Appearance patch touches one style line | 通过 / Pass |
| 安装器接受任意 `4.2.x`（不再写死 `4.2.3`），`--hide-billing-float` 可选 / Installer accepts any `4.2.x` | 通过：`compileall` + 9 项单测 + `node --check` / Pass |

> 豁免属于“补丁号级错配”的人工放行，不是作者的兼容承诺；本次运行正常，但仓库不据此把
> `0.2.1-rc.2` 视为上游支持的组合。Exemptions are a manual, patch-level bypass rather than an
> upstream compatibility statement; a working session here does not imply author support.
