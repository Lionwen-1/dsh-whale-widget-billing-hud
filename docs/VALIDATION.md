# 验证记录 / Validation record

测试日期 / Tested: 2026-10-04 · Windows · DSH `0.2.0-rc.2` · `dsh-whale-widget` `0.3.12` · `dsh-damage-pulse` `4.0.11`

| 检查 / Check | 结果 / Result |
| --- | --- |
| `python install.py --check` 在当前 desktop profile 中检查插件版本和源码锚点 / Version and source-anchor preflight | 通过 / Pass |
| 隔离插件目录中完整执行安装器，四份生成的 JavaScript 通过 Node 语法检查 / Full installer run in an isolated plugin fixture; four generated JS files pass Node syntax checks | 通过 / Pass |
| 隔离目录连续两次安装，四份生成文件的 SHA-256 保持一致 / Two isolated installer runs produce identical SHA-256 hashes for all four patched files | 通过 / Pass |
| DSH 内挂件、余额框和设置菜单显示 / Widget, balance panel, and settings menu visible in DSH | 通过 / Pass |
| 当前 DSH 加载 `dsh-damage-pulse` / Billing plugin loaded by current DSH | **未通过 / Blocked**: DSH 报告 `4.0.11` 与 `0.2.0-rc.2` 不兼容 / DSH reports incompatibility |
| 当前 DSH 中生成、读取并展示单次扣费事件 / End-to-end charge event on current DSH | **未验证 / Not verified**: 计费插件未运行 / billing plugin is not running |

这份验证区分了安装器与 JavaScript 语法检查、挂件的实际显示，以及计费插件的运行状态。兼容性门禁未被绕过。README 中的 GIF 是虚构数据的动画示意，不能当作真实扣费链路的测试证据。

This record separates installer and syntax checks, actual widget rendering, and billing-plugin runtime status. The compatibility gate was not bypassed. The README GIFs use fictional data and are not evidence of a working charge-event pipeline.

在已验证的 DSH `0.1.7-rc.2` 环境中，若要复验完整扣费链路，应安装指定版本的两款插件、运行安装器并重启 DSH，然后完成一次真实模型调用，检查挂件飘字及账本事件。On the previously validated DSH `0.1.7-rc.2` version, an end-to-end retest requires the pinned plugins, installer, full DSH restart, and a real model call with both the widget indicator and ledger event checked.
