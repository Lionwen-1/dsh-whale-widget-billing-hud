"""Render fictional widget GIFs from a locally supplied, licensed custom role.

The role image is read at render time and is never copied into this repository.
The generated GIFs are illustrations, not recordings or billing-test evidence.
Artwork in the GIFs follows the role image's CC BY-NC-SA 4.0 terms; see
THIRD_PARTY_NOTICES.md for attribution and modifications.
"""

from argparse import ArgumentParser
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "media"
WIDTH, HEIGHT = 720, 540
SCALE = 2
NAVY = "#23346e"
TEXT = "#263c7b"
BG = "#111318"
FONT = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")


def px(value):
    return round(value * SCALE)


def box(coords):
    return tuple(px(value) for value in coords)


def font(size, bold=False):
    source = FONT_BOLD if bold and FONT_BOLD.exists() else FONT
    if not source.exists():
        raise SystemExit("需要微软雅黑字体；请修改 tools/render_widget_gifs.py 中的 FONT 路径。")
    return ImageFont.truetype(str(source), px(size))


def text(draw, x, y, value, size, color, bold=False, anchor=None):
    draw.text((px(x), px(y)), value, font=font(size, bold), fill=color, anchor=anchor)


def background():
    image = Image.new("RGBA", (px(WIDTH), px(HEIGHT)), BG)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        tone = round(17 + 7 * y / HEIGHT)
        draw.line((0, px(y), px(WIDTH), px(y)), fill=(tone, tone + 2, tone + 5, 255), width=SCALE)
    draw.rounded_rectangle(box((15, 15, 705, 525)), radius=px(18), outline="#303946", width=px(1))
    draw.line(box((33, 37, 687, 37)), fill="#303946", width=px(1))
    text(draw, 34, 20, "演示动画 · DEMO", 12, "#b3bdc9", True)
    text(draw, 688, 20, "DSH 黑鲸挂件", 12, "#b3bdc9", True, anchor="ra")
    return image


def draw_character(image, role, frame, hit_at=None):
    bob = round(2 * math.sin(frame * 0.36))
    dx = 0
    brightness = 1.0
    if hit_at is not None:
        age = frame - hit_at
        if 0 <= age < 6:
            dx = (-4, 4, -3, 2, -1, 0)[age]
            brightness = (1.12, 1.28, 1.17, 1.09, 1.04, 1.0)[age]
    character = role if brightness == 1.0 else ImageEnhance.Brightness(role).enhance(brightness)
    image.alpha_composite(character, (px(296 + dx), px(119 + bob)))


def draw_bubble(image, balance, today, pulse=False):
    draw = ImageDraw.Draw(image)
    stroke = "#536cc0" if pulse else NAVY
    draw.ellipse(box((36, 45, 430, 228)), fill="#ffffff", outline=stroke, width=px(6))
    draw.ellipse(box((354, 222, 382, 239)), fill="#ffffff", outline=stroke, width=px(5))
    draw.ellipse(box((391, 245, 407, 256)), fill="#ffffff", outline=stroke, width=px(4))
    text(draw, 232, 78, "DeepSeek 余额", 24, "#586fae", True, anchor="mm")
    text(draw, 232, 135, f"¥ {balance:.2f}", 48, "#697bc8", True, anchor="mm")
    text(draw, 232, 181, f"今日已用 ¥{today:.2f}", 18, "#7286bd", False, anchor="mm")
    draw.rounded_rectangle(box((157, 199, 259, 221)), radius=px(10), fill="#63b867")
    text(draw, 208, 210, "谷 · 演示数据", 13, "#ffffff", True, anchor="mm")


def draw_balance_box(image, balance, today, pulse=False):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        box((321, 441, 692, 522)), radius=px(12),
        fill="#f8f9fc", outline="#7180a8" if pulse else "#aab1c1", width=px(2)
    )
    text(draw, 506, 468, f"余额 ¥{balance:.4f}", 24, TEXT, True, anchor="mm")
    text(draw, 506, 499, f"今日 ¥{today:.2f} · 谷", 17, "#6678ad", False, anchor="mm")


def floating_charge(image, label, cost, age, x, y):
    if age < 0 or age > 19:
        return
    alpha = min(255, age * 64 + 85, (20 - age) * 35)
    rise = age * 2.5
    value = f"{label} -{cost:.4f}¥"
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    text(gdraw, x, y - rise, value, 23, (255, 76, 72, alpha), True)
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(px(4))))
    image.alpha_composite(glow)


def make_frame(role, index, *, charge=False):
    image = background()
    hit_at = 4 if charge else None
    draw_character(image, role, index, hit_at=hit_at)
    updated = index >= (4 if charge else 12)
    pulse = (4 <= index <= 10) if charge else (12 <= index <= 18)
    draw_bubble(image, 88.41 if updated else 88.42, 1.59 if updated else 1.58, pulse)
    draw_balance_box(image, 88.4100 if updated else 88.4200, 1.59 if updated else 1.58, pulse)
    draw = ImageDraw.Draw(image)
    if charge:
        text(draw, 46, 298, "本次调用 · 逐项扣费", 18, "#d8e1ee", True)
        floating_charge(image, "命中", 0.0026, index - 4, 74, 367)
        floating_charge(image, "未命中", 0.0004, index - 13, 54, 384)
        floating_charge(image, "输出", 0.0070, index - 22, 83, 401)
        text(draw, 44, 485, "受击动作已开启（可在设置中关闭）", 13, "#9daec0")
    else:
        if index < 12:
            text(draw, 52, 343, "等待一次模型调用…", 19, "#c2ccdc", True)
        else:
            text(draw, 52, 343, "调用完成，余额已更新", 19, "#dce8f3", True)
            text(draw, 52, 386, "− ¥0.0100", 29, "#ff726e", True)
        text(draw, 44, 485, "演示数值 · 非真实录屏", 13, "#9daec0")
    return image.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def save_gif(path, frames, duration):
    palette = frames[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], loop=0,
                    duration=duration, optimize=True, disposal=2)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--role-image", type=Path,
                        default=Path.home() / ".dsh" / "whale-roles" / "maid-ink.png",
                        help="local licensed role PNG; never added to the repository")
    args = parser.parse_args()
    source = args.role_image.expanduser()
    if not source.is_file():
        raise SystemExit(f"找不到角色图：{source}；用 --role-image 指定本机有权使用的 PNG。")
    role = Image.open(source).convert("RGBA").resize((px(399), px(399)), Image.Resampling.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    balance_frames = [make_frame(role, i) for i in range(28)]
    charge_frames = [make_frame(role, i, charge=True) for i in range(38)]
    save_gif(OUT / "balance-update.gif", balance_frames, 120)
    save_gif(OUT / "charge-breakdown.gif", charge_frames, 110)
    for name in ("balance-update.gif", "charge-breakdown.gif"):
        path = OUT / name
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
