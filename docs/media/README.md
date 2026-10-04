# 演示素材 / Demo media

这些图片和 GIF 是原创、程序绘制的**功能示意**，不是 DSH 截图或录屏。所有金额均为虚构示例；几何小鲸鱼与界面元素未取自 DSH 或第三方插件的美术资源。图内均标注“演示数据 · DEMO”。

These images and GIFs are original, programmatically drawn **illustrations**, not screenshots or recordings of DSH. All amounts are fictional. The geometric whale and UI elements do not use DSH or third-party plugin artwork. Every frame is marked “演示数据 · DEMO”.

| 文件 / File | 内容 / Content |
| --- | --- |
| `overview.png` | 功能总览 / Feature overview |
| `settings.png` | 设置项 / Settings |
| `balance-update.gif` | 余额更新示意 / Balance update illustration |
| `charge-breakdown.gif` | 单次扣费分项示意 / Per-call charge breakdown illustration |

再生成 / Regenerate:

```bash
python -m pip install Pillow
python tools/render_demo.py
```

生成器需要 Windows 自带的 Microsoft YaHei 字体；其他平台可在 `tools/render_demo.py` 中调整 `FONT_CJK` 与 `FONT_CJK_BOLD`。The renderer uses the Microsoft YaHei font available on Windows; adjust the two font paths in the script for another platform.
