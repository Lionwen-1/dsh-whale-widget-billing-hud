# DSH 黑鲸女仆挂件增强包

[English](README.en.md) · [验证记录](docs/VALIDATION.md) · [机制与排错](NOTES.md) · [第三方声明](THIRD_PARTY_NOTICES.md)

## 演示 / Demo

主图由用户提供的**实际插件画面**编辑而成，余额已替换为虚构演示数值；黑发角色是本机对 `maid-atelier` 美术的改色与裁切，演示图按 **CC BY-NC-SA 4.0** 标注，**不属于本仓库代码的 MIT 许可范围**。署名：上善 → ZipZipPipe → Small-tailqwq；本机黑发改色与演示图编辑另行说明。下方 GIF 是原创几何图形示意，并非真实录屏。

![本机黑鲸自定义角色与虚构余额的演示图](docs/media/plugin-widget-demo.png)

| 余额更新示意 / Balance update | 单次费用示意 / Charge breakdown |
| --- | --- |
| ![虚构余额更新动画](docs/media/balance-update.gif) | ![虚构单次费用动画](docs/media/charge-breakdown.gif) |

[查看设置示意图](docs/media/settings.png) · [素材来源、许可与再生成方法](docs/media/README.md)

## 项目简介 / Overview

**中文：** 这是给 DSH 桌面端小鲸鱼娘挂件使用的本地补丁包，将挂件变成模型调用费用与余额的可视化仪表。它依赖现有社区插件，仓库保存我们的补丁脚本、注入代码和演示材料。

本项目是独立的社区补丁，与 DSH 或两款依赖插件的维护者没有隶属关系。

**English:** This local patch package turns the DSH desktop whale widget into a visual dashboard for model charges and account balance. It works with existing community plugins; this repository contains our patch scripts, injected code, and demo media.

## 主要功能与用途 / Features and use cases

| 功能 / Feature | 用途 / Use case |
| --- | --- |
| 常驻余额框 / Persistent balance panel | 在挂件脚下显示余额与今日用量，并可拖动、调整尺寸或隐藏。Show balance and today's usage beneath the widget, with controls to move, resize, or hide the panel. |
| 单次费用提示 / Per-call charge indicators | 从计费插件读取扣费事件，在角色旁显示每次调用的费用明细。Read charge events from the billing plugin and display per-call cost details beside the character. |
| 可选受击动作 / Optional hit reaction | 每次扣费时让当前挂件角色轻微晃动；在 ☰ 设置里开关，默认关闭。Lightly animate the currently selected widget character on each charge; toggle it in the ☰ menu. Off by default. |
| 气泡设置 / Bubble controls | 调整气泡字号、整体大小与位置，并保存设置。Adjust bubble text size, overall scale, and position with persistent settings. |
| 安装保护 / Installation checks | 打补丁前检查指定插件版本和源码锚点，保留原文件备份以便回滚。Check supported plugin versions and source anchors before patching, and keep original-file backups for rollback. |

**适合 / For:** 使用指定版本 DSH 插件、希望在桌面上随时查看模型用量与余额的人。Users of the supported DSH plugin versions who want at-a-glance usage and balance information on the desktop.

> 推荐组合：DSH `0.2.0-rc.2` + `dsh-whale-widget` **0.3.12** + `dsh-damage-pulse` **4.2.3**。旧版 `dsh-damage-pulse` **4.0.11** 仅保留给已验证的 DSH `0.1.7-rc.2` 路线；它在 DSH `0.2.0-rc.2` 会被兼容性门禁拦截。新版计费插件原生支持账号态计费和扣费事件，无需对其打补丁。详见[验证记录](docs/VALIDATION.md)。
> 效果全部来自**本地补丁**，不改 DSH 本体；每个补丁脚本都**幂等**，重复运行安全。

---

## 一、装之前

| 需要 | 说明 |
|---|---|
| DSH 桌面版 | 已安装并**至少启动过一次**（否则没有 `~/.dsh/profiles/`） |
| 插件 `dsh-whale-widget` | 挂件本体（角色 + 气泡 + 菜单）。需要 `0.3.12` |
| 插件 `dsh-damage-pulse` | 提供**精确扣费数据**（`/api/token-monitor/charge-events`）。推荐 `4.2.3`；旧 DSH 可用 `4.0.11` |
| Python 3.8+ | 用来跑补丁脚本（Windows 上 `python install.py`） |

两个插件都在 DSH 里装好、能正常显示角色之后，再打补丁。

---

## 二、安装

```bash
# 1) 检查插件版本与补丁锚点（不改任何文件）
python install.py --check

# 2) 正式打补丁（幂等，可反复运行）
python install.py

# 如果多个 profile 同时安装了两款插件，明确指定目标 profile
python install.py --check --plugin-root "/path/to/profile/node_modules"
```

脚本会做这些事：

1. 在同一个 `~/.dsh/profiles/*/node_modules/` 中定位两个插件，并在写入前检查版本和源码锚点。如果多个 profile 都装有这两个插件，用 `--plugin-root <node_modules目录>` 明确指定
2. 首次运行时备份需要改动的原文件：挂件始终备份到 `payload/whale-widget-backup-*`；仅旧版计费插件 `4.0.11` 备份到 `payload/damage-pulse-backup-*`
3. 对需要改动的文件从备份还原 → 重新打补丁，避免重复叠加；计费插件 `4.2.3` 只预检、不改文件
4. 用 Node.js 做 JavaScript 语法检查（找不到 Node.js 时跳过）
5. 在插件目录里写一份 `LOCAL-PATCH.md` 留痕

预检失败、补丁失败或语法检查失败时，安装器返回非零退出码，不会报告安装成功。预检会在两个插件均通过后才开始写入。当前仅支持上表列出的插件版本；升级插件后需先更新补丁兼容性，不能直接用旧备份覆盖新版。

源码检查可运行 `python -m unittest discover -s tests -v`、`python -m compileall -q install.py payload tests` 和 `node --check payload/balbox_patch.js`。完整打补丁的测试需使用对应版本的原版源码，在隔离的插件目录中运行 `python install.py --plugin-root <测试目录>`；仓库不附带第三方源码。

**打完必须重启 DSH**（整个关掉再打开）。原因：前端脚本的 `<script>` 注入点是 DSH 启动时收集的，`Ctrl+R` 在桌面壳里不会重新拉脚本。

---

## 三、重启后你会看到

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

## 四、动了哪些文件

| 文件 | 改动 |
|---|---|
| `<插件>/dsh-whale-widget/lib/index.js` | 余额缓存 25s→5s；无 API Key 时改走 DSH 账号登录态取余额；新增 `GET/POST /dsh-whale-balbox.json`（余额框设置落盘） |
| `<插件>/dsh-whale-widget/assets/whale-widget.js` | 注入：脚下余额框、扣费飘字、☰ 菜单设置项（含受击动作开关）、气泡缩放/位移、角色上抬 42px |
| `<插件>/dsh-damage-pulse/lib/index.js`、`lib/client.js` | **仅 4.0.11**：放开账号态计费资格、补足余额链路并隐藏其自带悬浮窗。**4.2.3 不修改这些文件**；它原生支持账号态与扣费事件，自己的悬浮窗可在插件设置中调整 |

---

## 五、卸载 / 回滚

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

## 六、出处与许可

- 挂件本体：**dsh-whale-widget**（社区插件）
- 扣费数据：**dsh-damage-pulse / dsh-token-monitor**（社区插件）
- 本仓库包含本地补丁脚本、注入代码，以及一张用于说明效果的**经编辑截图**；不打包原插件源码或独立角色素材。首次安装产生的原版备份只留在本机，不纳入 Git
- 本仓库自有代码以 **MIT** 许可证开源，详见 [LICENSE](LICENSE)；演示截图中的自定义角色美术按 **CC BY-NC-SA 4.0**，来源、修改与署名见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- 受击反馈的交互思路参考 `dsh-damage-pulse`；动画、开关和持久化由本项目独立实现，未复制其角色素材或实现代码。额外的蓝发角色不在本仓库中
- 若你另外用了黑鲸女仆皮肤（`maid-atelier`）：其插画为 **CC BY-NC-SA 4.0**（署名 上善 → ZipZipPipe → Small-tailqwq，**禁止商用**），代码为 MIT

## 七、已知限制

1. **必须重启 DSH** 才生效（桌面壳不重载前端脚本）
2. 飘字数据依赖 damage-pulse 的宿主在跑；把它禁用就没红字了
3. 余额小数位、飘字位置/时长、角色上抬高度等都在 `payload/balbox_patch.js` / 补丁脚本里，改了要重跑 `install.py`
4. Windows + DSH `0.2.0-rc.2` 已验证 `4.2.3` 插件加载、挂件显示、事件格式，以及一次真实调用写入正费用账本；短暂的飘字动画尚未捕捉到，需单独复验。其他平台未验证

---

## 八、目录结构

```
dsh-whale-widget-billing-hud/
├─ install.py                     一键安装器（--check 可空跑）
├─ README.md                      本文件
├─ README.en.md                   English guide
├─ NOTES.md                       机制说明与踩坑记录（想改代码时看）
├─ LICENSE                        本仓库 MIT 许可证
├─ THIRD_PARTY_NOTICES.md         依赖插件的署名与许可
├─ tests/                        安装器行为测试
└─ payload/
   ├─ patch_whale_widget.py       挂件补丁（含注入代码）
   ├─ patch_damage_pulse.py       计费插件补丁
   └─ balbox_patch.js             注入进挂件前端的那段代码（余额框+飘字+菜单项）
```
