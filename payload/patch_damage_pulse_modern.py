# -*- coding: utf-8 -*-
"""dsh-damage-pulse 4.2.x 外观补丁：隐去插件自带的悬浮窗（鲸鱼娘 + 余额卡）。

**为什么 4.2+ 只需要这一处**
- 计费资格（`deepseek-account`）与账号态余额，4.2 起官方已原生支持；
  宿主/客户端的旧门禁补丁（见 `patch_damage_pulse.py`，仅 4.0.11 用）不再需要。
- 飘字与余额显示已由 `dsh-whale-widget` 挂件接管；插件的悬浮窗会让画面出现
  两个人物、两套余额，所以默认隐去。

用法：
    python patch_damage_pulse_modern.py --check     # 只预检，不改文件
    python patch_damage_pulse_modern.py             # 打补丁（隐去悬浮窗）
    python patch_damage_pulse_modern.py --restore   # 从备份还原

幂等：重复运行会先把备份复制回去再重新打，不会层叠。
宿主无需改动，因此**不需要重启**也能看到悬浮窗消失——不过客户端脚本要重新加载页面。
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_pkg(name):
    """在任意 DSH profile 下找插件目录（不写死 profile 名）。"""
    override = os.environ.get("DSH_PATCH_PLUGIN_ROOT")
    if override:
        candidate = os.path.join(override, name)
        if os.path.isdir(candidate):
            return candidate
        raise SystemExit("测试插件目录不存在: " + candidate)
    for pat in (os.path.expanduser("~/.dsh/profiles/*/node_modules/" + name),
                os.path.expanduser("~/.dsh/**/node_modules/" + name)):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    raise SystemExit("!! 找不到插件目录 " + name + "，请先在 DSH 里安装该插件再运行本脚本")


def find_node():
    import shutil as _sh
    return _sh.which("node") or (_sh and (
        glob.glob(os.path.expanduser("~/.dsh/dsh-runtimes/**/node.exe"), recursive=True)
        or glob.glob(os.path.expanduser("~/.dsh/**/node"), recursive=True) or [""])[0])


PKG = find_pkg("dsh-damage-pulse")
CLIENT = os.path.join(PKG, "lib", "client.js")
NODE = find_node()

try:
    with open(os.path.join(PKG, "package.json"), encoding="utf-8") as fh:
        VERSION = json.load(fh).get("version", "0.0.0")
except (OSError, ValueError) as err:
    raise SystemExit("无法读取插件 package.json: %s" % err)

BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "damage-pulse-backup-%s" % VERSION)
BACKUP_CLIENT = os.path.join(BACKUP, "client.js")

# 两种排版都认：压缩成一行的，以及每个属性一行（制表符缩进）的
ANCHORS = (
    ('const CARD = { position: "fixed",',
     'const CARD = { display: "none", /* 本地补丁：隐去自带悬浮窗（飘字/余额已由挂件接管） */ position: "fixed",'),
    ('const CARD = {\n\t\t\tposition: "fixed",',
     'const CARD = {\n\t\t\tdisplay: "none",   // 本地补丁：隐去自带悬浮窗（飘字/余额已由挂件接管）\n\t\t\tposition: "fixed",'),
)


def read_client():
    try:
        with open(CLIENT, encoding="utf-8") as fh:
            return fh.read()
    except OSError as err:
        raise SystemExit("无法读取 %s: %s" % (CLIENT, err))


def choose_anchor(body):
    """返回 (命中数, from, to)；已打过补丁时命中数为 0 且标记存在。"""
    for frm, to in ANCHORS:
        if body.count(frm) == 1:
            return 1, frm, to
    return 0, None, None


def check():
    if not VERSION.startswith("4.2."):
        raise SystemExit("本脚本只处理 dsh-damage-pulse 4.2.x；当前 %s。"
                         "4.0.x/4.1.x 请用 patch_damage_pulse.py。" % VERSION)
    body = read_client()
    count, _frm, _to = choose_anchor(body)
    patched = 'display: "none"' in body.split("const CARD =", 1)[-1][:200]
    if count == 0 and not patched:
        raise SystemExit("插件源码与已验证版本不匹配：找不到唯一的 CARD 锚点；未修改文件。")
    print("preflight: dsh-damage-pulse %s，CARD 锚点%s" % (VERSION, "已打过补丁" if count == 0 else "通过"))


def restore():
    if not os.path.isfile(BACKUP_CLIENT):
        raise SystemExit("没有备份（%s），无法还原；可用重装插件代替。" % BACKUP_CLIENT)
    shutil.copy2(BACKUP_CLIENT, CLIENT)
    print("restored ->", CLIENT)


def main():
    ap = argparse.ArgumentParser(description="dsh-damage-pulse 4.2.x 外观补丁（隐去自带悬浮窗）")
    ap.add_argument("--check", action="store_true", help="仅预检，不修改文件")
    ap.add_argument("--restore", action="store_true", help="从备份还原插件原文件")
    args = ap.parse_args()

    print("插件版本:", VERSION)
    check()
    if args.restore:
        restore()
        return
    if args.check:
        print("预检通过；未修改任何文件。")
        return

    body = read_client()
    count, frm, to = choose_anchor(body)
    if count == 0:
        print("已打过补丁，无需改动")
        return

    # 备份（只备份要改的那一个文件）
    if not os.path.isfile(BACKUP_CLIENT):
        os.makedirs(BACKUP, exist_ok=True)
        shutil.copy2(CLIENT, BACKUP_CLIENT)
        print("backup ->", BACKUP)
    else:
        print("backup exists ->", BACKUP)
        shutil.copy2(BACKUP_CLIENT, CLIENT)   # 幂等：从原版重新开始

    body = read_client().replace(frm, to, 1)
    with open(CLIENT, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print("client: 自带悬浮窗已隐去")

    if NODE:
        tmp = os.path.join(os.environ.get("TEMP", "."), "chk-dp-modern-client.mjs")
        shutil.copy2(CLIENT, tmp)
        result = subprocess.run([NODE, "--check", tmp], capture_output=True, text=True)
        print("syntax client exit=%d %s" % (result.returncode, (result.stderr or "").strip()[:200]))
        if result.returncode != 0:
            restore()
            raise SystemExit("语法检查失败，已还原原文件。")
    else:
        print("syntax client 跳过（未找到 node）")

    note = os.path.join(PKG, "LOCAL-PATCH.md")
    with open(note, "w", encoding="utf-8") as fh:
        fh.write(
            "# 本地改动（非原作者内容）\n\n"
            "版本 %s。`lib/client.js` 的 `CARD` 样式加了 `display:none`，隐去插件自带的悬浮窗"
            "（鲸鱼娘 + 余额卡），因为飘字与余额已由 dsh-whale-widget 挂件接管。\n\n"
            "- 计费逻辑、宿主、计费模块**未改动**（4.2 起官方原生支持账号态计费）。\n"
            "- 撤销：`python payload/patch_damage_pulse_modern.py --restore`。\n" % VERSION
        )
    print("note ->", note)


if __name__ == "__main__":
    main()
