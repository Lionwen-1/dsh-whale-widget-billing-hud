# 演示素材 / Demo media

`plugin-widget-demo.png` 是用户提供的 DSH 插件截图经编辑后的演示图：将真实余额替换为虚构数值并标注“演示数据”。画面中的黑发自定义角色由本机对 `maid-atelier` 美术**改色、裁切**而来，并通过 `dsh-whale-widget` 显示。角色美术署名链：**上善 → ZipZipPipe → Small-tailqwq**；本机改动为黑发配色、头像裁切，演示图又替换了余额数字并加上标记。该演示图按 **CC BY-NC-SA 4.0** 使用：须保留署名与修改说明、限非商业用途，改编仍须相同方式共享；**不属于本仓库 MIT 代码许可范围**。来源见 [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) 与 [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK)。

其他 PNG 与 GIF 是原创、程序绘制的功能示意，不是 DSH 录屏；它们使用虚构金额和原创几何小鲸鱼。GIF 不构成真实扣费链路通过的证据。

`plugin-widget-demo.png` is an edited user-supplied DSH widget screenshot. The black-haired custom role is a locally **recolored and cropped** adaptation of `maid-atelier` artwork shown through `dsh-whale-widget`. Art attribution: **上善 → ZipZipPipe → Small-tailqwq**. Local changes: black hair recoloring and avatar crop; this demo further replaces balance values and adds a demo mark. The image is used under **CC BY-NC-SA 4.0**: retain attribution and modification notices, use it only noncommercially, and share adaptations alike. It is **outside this repository's MIT code license**. See the upstream [`maid-atelier` NOTICE](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/NOTICE) and [LICENSE-ARTWORK](https://github.com/Small-tailqwq/dsh-deep-whale/blob/main/maid-atelier/LICENSE-ARTWORK).

The other PNG and GIF files are original, programmatically drawn illustrations with fictional amounts and geometric whale art. They are not DSH recordings or evidence of an end-to-end charge test.

| 文件 / File | 内容 / Content |
| --- | --- |
| `plugin-widget-demo.png` | 实际插件画面，经数值脱敏 / Edited plugin screenshot with fictional values |
| `overview.png` | 功能总览 / Feature overview |
| `settings.png` | 设置项 / Settings |
| `balance-update.gif` | 余额更新示意 / Balance update illustration |
| `charge-breakdown.gif` | 单次扣费分项示意 / Per-call charge breakdown illustration |

原创示意图与 GIF 再生成 / Regenerate original diagrams and GIFs:

```bash
python -m pip install Pillow
python tools/render_demo.py
```

生成器需要 Windows 自带的 Microsoft YaHei 字体；其他平台可在 `tools/render_demo.py` 中调整 `FONT_CJK` 与 `FONT_CJK_BOLD`。The renderer uses the Microsoft YaHei font available on Windows; adjust the two font paths in the script for another platform.
