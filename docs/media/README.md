# 演示素材 / Demo media

`plugin-widget-demo.png` 是用户提供的 DSH 插件截图经编辑后的演示图：将真实余额替换为虚构数值并标注“演示数据”。画面中的黑发自定义角色由本机对 `maid-atelier` 美术**改色、裁切**而来，并通过 `dsh-whale-widget` 显示。`balance-update.gif` 和 `charge-breakdown.gif` 使用同一角色图，程序合成余额变化、逐项扣费飘字和可选受击动作。GIF 也使用虚构金额，**不是 DSH 录屏或真实扣费链路的验证证据**。

包含角色的主图与 GIF 按 **CC BY-NC-SA 4.0** 使用：须保留署名与修改说明、限非商业用途，改编仍须相同方式共享；**不属于本仓库 MIT 代码许可范围**。角色美术署名链：**上善 → ZipZipPipe → Small-tailqwq**。本机改动为黑发配色、头像裁切；主图另替换余额并加演示标记，GIF 另加入合成界面和动画。来源见 [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) 与 [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK)。仓库不附带独立角色原图。

`overview.png` 与 `settings.png` 是程序绘制的原创几何鲸鱼示意图，使用虚构金额。

`plugin-widget-demo.png` is an edited user-supplied DSH widget screenshot with fictional balance values and a demo mark. Its black-haired custom role is a locally **recolored and cropped** adaptation of `maid-atelier` artwork shown through `dsh-whale-widget`. The two GIFs use the same role image to compose balance changes, sequential floating charges, and an optional hit reaction. Their amounts are fictional. The GIFs are **not DSH recordings or evidence of a completed end-to-end billing test**.

The main image and GIFs follow **CC BY-NC-SA 4.0**: retain attribution and modification notices, use them only noncommercially, and share adaptations alike. They are **outside this repository's MIT code license**. Art attribution: **上善 → ZipZipPipe → Small-tailqwq**. Local changes include black hair and palette recoloring and an avatar crop; the main image also replaces balance values and adds a demo mark, while the GIFs add a composed UI and animation. See the upstream [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) and [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK). The standalone role PNG is not bundled.

`overview.png` and `settings.png` are original geometric whale illustrations with fictional amounts.

| 文件 / File | 内容 / Content |
| --- | --- |
| `plugin-widget-demo.png` | 实际插件画面，经数值脱敏 / Edited plugin screenshot with fictional values |
| `overview.png` | 功能总览 / Feature overview |
| `settings.png` | 设置项 / Settings |
| `balance-update.gif` | 黑鲸挂件的余额更新合成动画 / Composed balance update with the black whale role |
| `charge-breakdown.gif` | 黑鲸挂件的逐项扣费飘字合成动画 / Composed sequential charge indicators with the black whale role |

再生成 / Regenerate:

```bash
python -m pip install Pillow
# Original geometric PNGs / 原创几何 PNG
python tools/render_demo.py
# GIFs: provide a locally licensed role PNG; the source is never copied into this repo
# GIF：指定本机有权使用的角色 PNG，原图不会复制到仓库
python tools/render_widget_gifs.py --role-image "/path/to/your/licensed-role.png"
```

生成器需要 Windows 自带的微软雅黑字体；其他平台可调整两个脚本中的字体路径。The renderers use Microsoft YaHei on Windows; adjust the font paths in both scripts for another platform.
