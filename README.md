# DSH 小鲸鱼挂件计费增强

让 DSH 桌面挂件成为随手可看的用量面板：**脚下显示余额与今日用量，头顶逐项提示模型调用费用**。还可以移动和缩放气泡、调整余额框，并按需开启扣费时的轻微受击动作。

[English](README.en.md) · [适用版本](#适用版本与验证范围) · [快速开始](#快速开始) · [验证记录](docs/VALIDATION.md) · [机制与排错](NOTES.md) · [素材与许可](THIRD_PARTY_NOTICES.md) · [支持项目](#支持项目)

这是基于 [`dsh-whale-widget`](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) 和 [`dsh-damage-pulse`](https://github.com/wssfk12138/dsh-damage-pulse) 的**独立社区补丁**，适合希望在现有角色上集中查看余额与费用、无需再开一套角色窗口的用户。仓库提供安装脚本和新增功能代码，不分发两款插件或完整角色原图，也不修改 DSH 本体。

## 效果预览

![黑鲸挂件、余额气泡与脚下余额框](docs/media/plugin-widget-demo.png)

| 余额更新与头顶扣费 | 逐项费用提示 |
| --- | --- |
| ![余额变化与头顶扣费动画](docs/media/balance-update-overhead.gif) | ![命中、未命中和输出费用依次飘出](docs/media/charge-breakdown.gif) |

主图改自用户提供的实际挂件截图；余额数值已替换为虚构值。GIF 是合成演示，包含眨眼和可选受击效果，**不代表真实扣费动画已完成现场验证**。角色美术按 CC BY-NC-SA 4.0 使用，代码采用 MIT。[素材说明与再生成方法](docs/media/README.md) · [设置示意图](docs/media/settings.png)

## 能做什么

| 功能 | 用途 |
| --- | --- |
| 常驻余额框 | 在角色脚下显示四位小数余额与今日用量；可拖动、调尺寸或隐藏。 |
| 单次费用飘字 | 从计费插件读取事件，在角色头顶依次显示命中、未命中、输出等费用；退款或加费显示绿字。 |
| 气泡与挂件设置 | 调整余额气泡的字号、大小和位置；设置保存在 `localStorage` 与 DSH 本地配置中。 |
| 可选受击动作 | 扣费时让当前角色轻微晃动；在 ☰ 菜单开关，默认关闭。 |
| 安全安装与回滚 | 安装前检查插件版本和代码锚点，首次修改时备份原文件，重复安装不会叠加补丁。 |

## 适用版本与验证范围

| DSH 桌面版 | 挂件插件 | 计费插件 | 安装器行为 |
| --- | --- | --- | --- |
| `0.2.0-rc.2` | `dsh-whale-widget` `0.3.12` | `dsh-damage-pulse` `4.2.3` | 修改挂件；计费插件仅预检，使用其原生账号态计费与事件接口。 |
| `0.1.7-rc.2` | `dsh-whale-widget` `0.3.12` | `dsh-damage-pulse` `4.0.11` | 修改挂件和旧版计费插件。 |

Windows 上已验证安装、设置持久化，以及一次真实调用写入正费用账本；**短暂的现场飘字与受击动画尚未捕捉到**。两张 GIF 只说明预期外观。详细证据见[验证记录](docs/VALIDATION.md)。其他版本会被预检拒绝，升级插件后应先核对兼容性。

## 快速开始

先在同一个 DSH profile 中安装上表对应的两款插件，再从仓库根目录运行：

```bash
python install.py --check
python install.py
```

安装后**完整退出并重新打开 DSH**。`Ctrl+R` 不会重新加载启动时注入的前端脚本。多个 profile 同时装有插件时，请使用 `--plugin-root "/path/to/profile/node_modules"` 指定目标；下文有完整说明。

---

## 安装前准备

| 需要 | 说明 |
|---|---|
| DSH 桌面版 | 已安装并**至少启动过一次**（否则没有 `~/.dsh/profiles/`） |
| 两款社区插件 | 在**同一个 profile** 中安装上表对应版本；计费事件来自 `/api/token-monitor/charge-events` |
| Python 3.8+ | 运行安装器 |
| Node.js（可选） | 安装时检查 JavaScript 语法；缺少时跳过此项 |

两个插件都在 DSH 里装好、能正常显示角色之后，再打补丁。

---

## 安装细节

```bash
# 多个 profile 同时安装了两款插件时，明确指定目标
python install.py --check --plugin-root "/path/to/profile/node_modules"
python install.py --plugin-root "/path/to/profile/node_modules"
```

脚本会做这些事：

1. 在同一个 `~/.dsh/profiles/*/node_modules/` 中定位两个插件，并在写入前检查版本和源码锚点。如果多个 profile 都装有这两个插件，用 `--plugin-root <node_modules目录>` 明确指定
2. 首次运行时备份需要改动的原文件：挂件始终备份到 `payload/whale-widget-backup-*`；仅旧版计费插件 `4.0.11` 备份到 `payload/damage-pulse-backup-*`
3. 对需要改动的文件从备份还原 → 重新打补丁，避免重复叠加；计费插件 `4.2.3` 只预检、不改文件
4. 用 Node.js 做 JavaScript 语法检查（找不到 Node.js 时跳过）
5. 在插件目录里写一份 `LOCAL-PATCH.md` 留痕

预检失败、补丁失败或语法检查失败时，安装器返回非零退出码，不会报告安装成功。预检会在两个插件均通过后才开始写入。当前仅支持上表列出的插件版本；升级插件后需先更新补丁兼容性，不能直接用旧备份覆盖新版。

源码检查可运行 `python -m unittest discover -s tests -v`、`python -m compileall -q install.py payload tests` 和 `node --check payload/balbox_patch.js`。完整打补丁的测试需使用对应版本的原版源码，在隔离的插件目录中运行 `python install.py --plugin-root <测试目录>`；仓库不附带第三方源码。

安装完成后按[快速开始](#快速开始)中的要求完整重启 DSH。

---

## 使用与设置

### 1. 脚下常驻余额条

```
        ┌───────────────────────┐
        │      余额 ¥88.4200     │   ← 虚构示例；4 位小数，逐笔更新
        │   今日 ¥1.58 · 谷      │
        └───────────────────────┘
                 （她站在上面）
```

- **拖框身** = 上下左右自由移动
- **拖右边缘** = 改宽度（30%~100%）
- **拖上边缘** = 改厚度
- **双击**框身 / 右边缘 / 上边缘 = 分别复位「位置 / 宽度 / 厚度」

### 2. 每次调用飘红字

模型每调用一次，她头顶右上飘出对应的费用（一条一条出现，不是一起蹦）：

```
        命中 -0.0135¥
        未命中 -0.0004¥
        输出 -0.0077¥
```

数字来源是 damage-pulse 的精确账本（缓存命中 / 未命中 / 输出分开计价），退款或充值会飘**绿字**。

### 3. ☰ 菜单里多出来的一组设置

| 菜单项 | 作用 |
|---|---|
| **显示余额框** | 隐藏 / 显示脚下那条框 |
| **余额框字号** | 框内字号 8~24px |
| **气泡字号** | 那张余额泡泡的**文字**倍数 0.5~2.0 |
| **泡泡大小** | 那张余额泡泡的**整体尺寸**（形状+文字一起缩放）0.5~2.0 |
| **泡泡位置 [复位]** | 把泡泡移回原位 |
| **泡泡抓手** | 隐藏 / 显示泡泡顶边那条拖动抓手 |
| **受击动作** | 扣费时轻微晃动当前角色；默认关闭，关闭后扣费飘字仍显示 |

**拖泡泡**：鼠标移到泡泡顶边正中的小横杠（抓手）上，按住就能把整张卡拖到任意位置；双击抓手复位。

所有设置都会**同时**存进浏览器 `localStorage` 和磁盘 `~/.dsh/.dshw-balbox.json`，换浏览器、清缓存、重启都不丢。

---

## 修改范围

| 文件 | 改动 |
|---|---|
| `<插件>/dsh-whale-widget/lib/index.js` | 余额缓存 25s→5s；无 API Key 时改走 DSH 账号登录态取余额；新增 `GET/POST /dsh-whale-balbox.json`（余额框设置落盘） |
| `<插件>/dsh-whale-widget/assets/whale-widget.js` | 注入：脚下余额框、扣费飘字、☰ 菜单设置项（含受击动作开关）、气泡缩放/位移、角色上抬 42px |
| `<插件>/dsh-damage-pulse/lib/index.js`、`lib/client.js` | **仅 4.0.11**：放开账号态计费资格、补足余额链路并隐藏其自带悬浮窗。**4.2.3 不修改这些文件**；它原生支持账号态与扣费事件，自己的悬浮窗可在插件设置中调整 |

---

## 回滚

安装包的 `payload/` 中保留着**被修改文件的原版备份**（已被 Git 忽略）。挂件备份始终存在；计费插件备份仅在旧版 `4.0.11` 路线产生：

```
payload/whale-widget-backup-0.3.12/{index.js,whale-widget.js}
payload/damage-pulse-backup-4.0.11/{index.js,client.js}
```

回滚有两种方式：

```bash
# 方式一：把备份文件复制回相应插件的 lib/ 或 assets/ 路径
# 方式二：通过 DSH 插件管理器重新安装原版插件
```

挂件插件升级会覆盖补丁。计费插件 `4.2.3` 无本地补丁；未知新版仍会被预检拦下，需先验证其事件接口和运行时兼容性。

---

## 许可与来源

- 本项目自写的安装器和补丁代码采用 [MIT 许可](LICENSE)；两款依赖插件需分别按其原许可安装，本仓库不附带它们的源码或安装备份。
- 演示截图、GIF 与眨眼局部包含改编的 `maid-atelier` 角色美术，采用 **CC BY-NC-SA 4.0**，不属于代码的 MIT 许可；完整角色原图不在仓库中。署名链：**上善 → ZipZipPipe → Small-tailqwq**。
- 受击反馈借鉴 `dsh-damage-pulse` 的事件驱动思路，动画和设置代码独立编写；其额外蓝发角色与素材没有收入本项目。
- 赞赏码由维护者提供，只作为自愿支持入口。素材修改、授权边界和来源见 [第三方声明](THIRD_PARTY_NOTICES.md)。

## 已知限制

1. **必须重启 DSH** 才生效（桌面壳不重载前端脚本）
2. 飘字数据依赖 damage-pulse 的宿主在跑；把它禁用就没红字了
3. 余额小数位、飘字位置/时长、角色上抬高度等都在 `payload/balbox_patch.js` / 补丁脚本里，改了要重跑 `install.py`
4. Windows + DSH `0.2.0-rc.2` 已验证 `4.2.3` 插件加载、挂件显示、事件格式，以及一次真实调用写入正费用账本；短暂的飘字动画尚未捕捉到，需单独复验。其他平台未验证

---

## 文件导航

```
dsh-whale-widget-billing-hud/
├─ install.py                     一键安装器（--check 可空跑）
├─ README.md                      本文件
├─ README.en.md                   English guide
├─ NOTES.md                       机制说明与踩坑记录（想改代码时看）
├─ LICENSE                        本仓库 MIT 许可证
├─ THIRD_PARTY_NOTICES.md         依赖插件的署名与许可
├─ docs/
│  ├─ VALIDATION.md               运行时验证记录
│  └─ media/                      截图、GIF 与赞赏码
├─ tools/                         演示素材生成脚本与眨眼局部素材
├─ tests/                        安装器行为测试
└─ payload/
   ├─ patch_whale_widget.py       挂件补丁（含注入代码）
   ├─ patch_damage_pulse.py       计费插件补丁
   └─ balbox_patch.js             注入进挂件前端的那段代码（余额框+飘字+菜单项）
```

## 支持项目

这个项目免费使用。如果它帮你把桌面用量看得更清楚，欢迎给仓库点 Star；也可以自愿赞赏维护者 Lionwen。赞赏与功能使用无关。

<a href="docs/media/support-lionwen.png"><img src="docs/media/support-lionwen.png" alt="Lionwen 的赞赏码" width="480"></a>

[打开原尺寸赞赏码](docs/media/support-lionwen.png)
