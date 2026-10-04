# Third-party notices / 第三方声明

This repository contains patch scripts, anchor strings, original widget additions, one edited demo screenshot, two composed GIFs, a partial closed-eye overlay, and a maintainer-supplied support image. It does not bundle either third-party plugin or the complete character image. Install the plugins separately under their own licenses.

本仓库包含补丁脚本、定位原插件代码所需的锚点字符串、自写挂件功能、一张经编辑的演示截图、两张合成 GIF、一份闭眼局部叠加素材和维护者提供的赞赏图；不打包第三方插件或完整角色原图。请按各项目自身许可单独安装插件。

| Dependency / 依赖 | Version / 版本 | License / 许可 | Notice / 署名 |
| --- | --- | --- | --- |
| [dsh-whale-widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) | 0.3.12 | MIT | Copyright (c) 2026 MeteorNOX |
| [dsh-damage-pulse](https://github.com/wssfk12138/dsh-damage-pulse) | 4.0.11 / 4.2.3 | MIT | Copyright (c) 2026 dsh-damage-pulse contributors |
| [maid-atelier](https://github.com/Small-tailqwq/dsh-deep-whale/tree/main/maid-atelier) artwork / 美术 | Locally recolored custom role / 本机改色角色 | CC BY-NC-SA 4.0 | 上善 → ZipZipPipe → Small-tailqwq; see [NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) |

The MIT permission and warranty terms for this project's code appear in [LICENSE](LICENSE). The edited `docs/media/plugin-widget-demo.png` is a user-supplied widget screenshot using a black-haired local custom role adapted from `maid-atelier` artwork. The `docs/media/balance-update-overhead.gif` and `docs/media/charge-breakdown.gif` also show that role in a programmatically composed UI. The partial eye-state overlay at `tools/assets/black-whale-closed-eyes.png` was extracted from an AI-assisted closed-eye edit of the local role image and is used only to compose blinks. Local modifications: recoloring the hair and palette, cropping the character to an avatar, replacing the screenshot's balance values and adding a demo mark, then composing fictional balance, overhead charge, and blink animations for the GIFs. These four media files follow [CC BY-NC-SA 4.0 artwork terms](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK): attribution, noncommercial use, and ShareAlike. They are **not covered by this repository's MIT code license**. The complete role image is not bundled.

本项目代码的 MIT 授权与免责声明见 [LICENSE](LICENSE)。经编辑的演示截图 `docs/media/plugin-widget-demo.png` 和两张合成动图 `docs/media/balance-update-overhead.gif`、`docs/media/charge-breakdown.gif` 都使用本机改色的 `maid-atelier` 自定义角色。`tools/assets/black-whale-closed-eyes.png` 是从本机角色图辅助生成的闭眼变体中裁出的眼部局部，仅用于合成眨眼。修改包括黑发及配色调整、头像裁切、截图余额替换和演示标记，以及 GIF 中的虚构余额、头顶扣费和眨眼动画合成。这四份素材按 [CC BY-NC-SA 4.0 美术条款](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK) 使用：署名、非商业、相同方式共享，**不适用本仓库代码的 MIT 许可**。本仓库不单独分发完整角色图文件。

The optional hit reaction takes **interaction inspiration** from `dsh-damage-pulse`'s event-driven feedback. The animation, setting, and persistence code here are original; no character asset or implementation code was copied from that plugin. Its extra blue-haired character is not included in this repository.

可选受击动作借鉴了 `dsh-damage-pulse` 的**事件驱动反馈思路**。本仓库的动画、设置及持久化代码独立编写，未复制该插件的角色素材或实现代码；额外的蓝发角色不纳入本仓库。

The maintainer supplied `docs/media/support-lionwen.png` as an optional support image. It is included unchanged and is not covered by the MIT code license or the character artwork license.

`docs/media/support-lionwen.png` 是维护者提供的自愿赞赏图，按原图收录；不属于代码的 MIT 许可或角色美术许可范围。
