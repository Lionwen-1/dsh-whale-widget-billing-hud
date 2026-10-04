"""Render original, fictional previews for the README (requires Pillow).

These are illustrations, not screenshots. Values and UI labels are examples.
No account details, DSH character art, or third-party plugin assets are used.
"""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "media"
SIZE = (1200, 675)
BG = "#081321"
PANEL = "#101f31"
PANEL_LIGHT = "#172a3d"
INK = "#eaf4f7"
MUTED = "#9db1be"
TEAL = "#58e2d0"
AMBER = "#f5c779"
CORAL = "#ff8796"
FONT_CJK = Path("C:/Windows/Fonts/msyh.ttc")
FONT_CJK_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_CJK_BOLD if bold else FONT_CJK), size)


def rr(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label(draw, pos, value, size, color=INK, bold=False):
    draw.text(pos, value, font=font(size, bold), fill=color)


def base(title, subtitle, frame=0):
    im = Image.new("RGB", SIZE, BG)
    d = ImageDraw.Draw(im)
    for y in range(SIZE[1]):
        t = y / SIZE[1]
        d.line((0, y, 1200, y), fill=(round(8 + 5*t), round(19 + 13*t), round(33 + 18*t)))
    d.ellipse((-120, 400, 390, 900), fill="#102c3c")
    d.ellipse((890, -360, 1460, 260), fill="#102b40")
    rr(d, (48, 42, 1152, 633), 28, "#0d1b2b", "#284152", 2)
    d.line((48, 105, 1152, 105), fill="#294151", width=2)
    for i, c in enumerate((CORAL, AMBER, TEAL)):
        d.ellipse((73 + i*23, 67, 84 + i*23, 78), fill=c)
    label(d, (164, 61), "WHALE  /  BILLING HUD", 18, MUTED, True)
    rr(d, (70, 132, 1130, 608), 22, "#0e1d2d", "#1b3446", 2)
    label(d, (100, 151), title, 34, INK, True)
    label(d, (101, 202), subtitle, 17, MUTED)
    rr(d, (892, 154, 1098, 186), 14, "#254455")
    label(d, (907, 158), "演示数据 · DEMO", 15, TEAL, True)
    label(d, (93, 573), "Illustrative UI · Fictional values · Original artwork", 13, MUTED)
    return im, d


def whale(d, x=326, y=354, bob=0):
    y += bob
    d.ellipse((x-154, y-17, x+139, y+170), fill="#0a566c")
    d.ellipse((x-145, y-51, x+142, y+144), fill="#5dc6ce")
    d.ellipse((x-111, y+40, x+112, y+145), fill="#b8f0e8")
    d.polygon([(x+124,y+49),(x+204,y+2),(x+195,y+93),(x+130,y+101)], fill="#48aeba")
    d.polygon([(x+38,y-33),(x+93,y-91),(x+113,y-20)], fill="#70d7d3")
    d.ellipse((x-77,y+9,x-56,y+30), fill="#132a3c")
    d.ellipse((x-71,y+12,x-65,y+18), fill="#ffffff")
    d.arc((x-65,y+23,x-21,y+56), 5, 160, fill="#18475a", width=3)
    d.ellipse((x-3,y-82,x+11,y-68), fill="#8ae8df")
    d.ellipse((x+13,y-110,x+23,y-100), fill="#8ae8df")
    d.ellipse((x-17,y-106,x-9,y-98), fill="#8ae8df")


def balance_box(d, amount="88.4200", today="1.58", glow=False):
    border = TEAL if glow else "#3d7a85"
    rr(d, (133, 510, 560, 558), 16, "#173443", border, 2)
    label(d, (155, 518), "余额  ¥", 19, MUTED)
    label(d, (254, 514), amount, 27, TEAL, True)
    label(d, (420, 520), f"今日 ¥{today}", 15, AMBER)


def info_card(d, y, title, content, accent=TEAL):
    rr(d, (649, y, 1077, y+83), 17, PANEL_LIGHT, "#29495a", 1)
    rr(d, (668, y+18, 673, y+65), 2, accent)
    label(d, (687, y+14), title, 17, MUTED)
    label(d, (687, y+40), content, 21, INK, True)


def overview():
    im, d = base("黑鲸挂件 · 余额与用量", "A desktop glance at your balance and per-call cost")
    whale(d)
    balance_box(d)
    info_card(d, 266, "实时余额 / Balance", "示例 ¥88.4200")
    info_card(d, 365, "逐笔扣费 / Per-call", "命中 · 未命中 · 输出", AMBER)
    info_card(d, 464, "挂件设置 / Widget", "移动 · 缩放 · 显示", "#9ba8ff")
    OUT.joinpath("overview.png").parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT / "overview.png", optimize=True)


def settings():
    im, d = base("按你的桌面调整", "Move, resize, and configure the widget")
    whale(d, x=315, y=340)
    balance_box(d)
    rr(d, (641, 250, 1080, 551), 18, PANEL_LIGHT, "#315164", 2)
    for line_y in (275, 282, 289):
        d.line((672, line_y, 693, line_y), fill=TEAL, width=3)
    label(d, (704, 266), "挂件设置 / Widget settings", 23, INK, True)
    rows = [
        ("显示余额框 / Show balance", "ON", TEAL),
        ("余额框字号 / Balance font", "20 px", AMBER),
        ("气泡大小 / Bubble size", "110%", AMBER),
        ("泡泡位置 / Bubble position", "自由拖动", TEAL),
    ]
    for i, (name, value, color) in enumerate(rows):
        yy = 320 + i*55
        d.line((666, yy-7, 1052, yy-7), fill="#355061")
        label(d, (670, yy), name, 17, INK)
        rr(d, (951, yy-4, 1055, yy+30), 12, "#254456")
        label(d, (968, yy), value, 15, color, True)
    im.save(OUT / "settings.png", optimize=True)


def balance_animation():
    frames = []
    values = ["88.4200"]*5 + ["88.4174"]*7 + ["88.4100"]*8
    for i, value in enumerate(values):
        im, d = base("余额随调用更新", "Balance updates after each model call")
        whale(d, bob=round(math.sin(i*0.45)*3))
        balance_box(d, value, "1.58" if i < 5 else "1.59", glow=5 <= i <= 12)
        info_card(d, 266, "当前余额 / Balance", f"¥{value}")
        info_card(d, 365, "今日用量 / Today", "¥1.58" if i < 5 else "¥1.59", AMBER)
        info_card(d, 464, "状态 / Status", "等待调用" if i < 5 else "已记录一笔费用", "#9ba8ff")
        frames.append(im.resize((960, 540), Image.Resampling.LANCZOS))
    frames[0].save(OUT / "balance-update.gif", save_all=True, append_images=frames[1:], duration=120,
                   loop=0, optimize=True, disposal=2)


def charge_animation():
    entries = [("缓存命中 / Cache hit", "-¥0.0026", TEAL),
               ("未命中 / Cache miss", "-¥0.0004", AMBER),
               ("输出 / Output", "-¥0.0070", CORAL)]
    frames = []
    for i in range(24):
        im, d = base("看清每次模型调用", "Illustrated charge-event sequence")
        whale(d, x=323, y=339, bob=round(math.sin(i*0.4)*3))
        balance_box(d, "88.4100")
        rr(d, (648, 257, 1077, 532), 18, PANEL_LIGHT, "#315164", 2)
        label(d, (672, 277), "单次费用 / Charge breakdown", 20, INK, True)
        visible = min(3, max(0, (i-2)//6+1))
        for j in range(visible):
            name, amount, color = entries[j]
            yy = 336+j*60
            rr(d, (672, yy, 1050, yy+47), 12, "#20394a")
            label(d, (686, yy+8), name, 16, INK)
            label(d, (937, yy+8), amount, 17, color, True)
            if i >= 7+j*5:
                fade_y = max(0, i-(7+j*5))*3
                label(d, (380+j*15, 280-j*33-fade_y), amount, 18, color, True)
        frames.append(im.resize((960, 540), Image.Resampling.LANCZOS))
    frames[0].save(OUT / "charge-breakdown.gif", save_all=True, append_images=frames[1:],
                   duration=125, loop=0, optimize=True, disposal=2)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    overview()
    settings()
    balance_animation()
    charge_animation()
    for item in sorted(OUT.glob("*")):
        if item.suffix in {".png", ".gif"}:
            print(f"{item.relative_to(ROOT)}: {item.stat().st_size:,} bytes")
