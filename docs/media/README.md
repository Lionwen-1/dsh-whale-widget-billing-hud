# 演示素材 / Demo media

`plugin-widget-demo.png` 是用户提供的 DSH 插件截图经编辑后的演示图：将真实余额替换为虚构数值并标注“演示数据”。画面中的黑发自定义角色由本机对 `maid-atelier` 美术**改色、裁切**而来，并通过 `dsh-whale-widget` 显示。`balance-update.gif` 和 `charge-breakdown.gif` 使用同一角色图，程序合成余额变化、眨眼、角色头顶逐项扣费飘字和可选受击动作。GIF 也使用虚构金额，**不是 DSH 录屏或真实扣费链路的验证证据**。

包含角色的主图、GIF 和 `tools/assets/black-whale-closed-eyes.png` 眨眼局部素材按 **CC BY-NC-SA 4.0** 使用：须保留署名与修改说明、限非商业用途，改编仍须相同方式共享；**不属于本仓库 MIT 代码许可范围**。角色美术署名链：**上善 → ZipZipPipe → Small-tailqwq**。本机改动为黑发配色、头像裁切；主图另替换余额并加演示标记，GIF 另加入合成界面和动画。眨眼素材由本机角色图辅助生成闭眼变体后，仅提取眼部区域。来源见 [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) 与 [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK)。仓库不附带完整角色原图。

`overview.png` 与 `settings.png` 是程序绘制的原创几何鲸鱼示意图，使用虚构金额。

`plugin-widget-demo.png` is an edited user-supplied DSH widget screenshot with fictional balance values and a demo mark. Its black-haired custom role is a locally **recolored and cropped** adaptation of `maid-atelier` artwork shown through `dsh-whale-widget`. The two GIFs use the same role image to compose balance changes, blinking, sequential floating charges above the character's head, and an optional hit reaction. Their amounts are fictional. The GIFs are **not DSH recordings or evidence of a completed end-to-end billing test**.

The main image, GIFs, and `tools/assets/black-whale-closed-eyes.png` partial blink overlay follow **CC BY-NC-SA 4.0**: retain attribution and modification notices, use them only noncommercially, and share adaptations alike. They are **outside this repository's MIT code license**. Art attribution: **上善 → ZipZipPipe → Small-tailqwq**. Local changes include black hair and palette recoloring and an avatar crop; the main image also replaces balance values and adds a demo mark, while the GIFs add a composed UI and animation. The blink overlay was extracted from an assisted closed-eye variant of the local role image. See the upstream [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) and [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK). The complete role PNG is not bundled.

`overview.png` and `settings.png` are original geometric whale illustrations with fictional amounts.

| 文件 / File | 内容 / Content |
| --- | --- |
| `plugin-widget-demo.png` | 实际插件画面，经数值脱敏 / Edited plugin screenshot with fictional values |
| `overview.png` | 功能总览 / Feature overview |
| `settings.png` | 设置项 / Settings |
| `balance-update.gif` | 黑鲸挂件的余额更新、头顶扣费和眨眼合成动画 / Composed balance update, overhead charge, and blink |
| `charge-breakdown.gif` | 黑鲸挂件头顶逐项扣费飘字与眨眼合成动画 / Composed overhead charges and blink |
| `tools/assets/black-whale-closed-eyes.png` | 仅含闭眼局部的叠加素材 / Partial closed-eye overlay only |

再生成 / Regenerate:

```bash
python -m pip install Pillow
# Original geometric PNGs / 原创几何 PNG
python tools/render_demo.py
# GIFs: provide the matching locally licensed black whale role PNG.
# GIF：指定与仓库眨眼局部素材匹配、且本机有权使用的黑鲸角色 PNG。
# The complete role image is never copied into this repo / 完整角色图不会复制到仓库。
python tools/render_widget_gifs.py --role-image "/path/to/your/licensed-role.png"
```

若改用其他角色图，请同时通过 `--blink-overlay` 指定与之匹配的闭眼局部素材。For a different role image, provide a matching eye-state overlay with `--blink-overlay`.

生成器需要 Windows 自带的微软雅黑字体；其他平台可调整两个脚本中的字体路径。The renderers use Microsoft YaHei on Windows; adjust the font paths in both scripts for another platform.
