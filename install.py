# -*- coding: utf-8 -*-
"""DSH 黑鲸女仆挂件增强包 —— 一键安装

用法（在装了 DSH 的电脑上，Python 3.8+）：
    python install.py            # 打补丁（幂等，可反复运行）
    python install.py --check    # 只检查环境与现状，不改任何文件

前提：
    1. DSH 已安装并至少启动过一次（存在 ~/.dsh/profiles/<profile>/）
    2. 已装好这两个插件：dsh-whale-widget、dsh-damage-pulse
打完补丁必须**重启 DSH** 才生效（前端脚本的注入点在启动时收集）。
"""
import argparse
import glob
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "payload")


def select_plugin_root(explicit):
    """Use one profile for both plugins; never silently mix two profiles."""
    if explicit:
        return os.path.abspath(explicit)
    roots = sorted(set(glob.glob(os.path.expanduser("~/.dsh/profiles/*/node_modules"))))
    candidates = [root for root in roots if all(
        os.path.isdir(os.path.join(root, name))
        for name in ("dsh-whale-widget", "dsh-damage-pulse"))]
    if len(candidates) != 1:
        sys.exit("找到 %d 个同时含两款插件的 profile；请用 --plugin-root 指定 node_modules 目录。" % len(candidates))
    return candidates[0]


def version_of(p):
    try:
        with open(os.path.join(p, "package.json"), encoding="utf-8") as fh:
            return json.load(fh).get("version", "?")
    except Exception:
        return "?"


def check_modern_pulse(pulse):
    """4.2.3 ships account billing and charge events; leave its packaged payload untouched."""
    runtime = os.path.join(pulse, "runtime")
    manifest_path = os.path.join(runtime, "manifest.json")
    billing_path = os.path.join(runtime, "host", "billing.mjs")
    try:
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        with open(billing_path, encoding="utf-8") as fh:
            billing = fh.read()
    except (OSError, ValueError) as err:
        sys.exit("dsh-damage-pulse 4.2.3 的运行载荷不完整: %s" % err)
    modules = manifest.get("modules", [])
    billing_files = next((m.get("files", []) for m in modules if m.get("id") == "billing"), [])
    if manifest.get("version") != "4.2.3" or not any(
        item.get("root") == "host" and item.get("path") == "billing.mjs"
        for item in billing_files
    ):
        sys.exit("dsh-damage-pulse 4.2.3 的 manifest 缺少计费模块；未修改插件。")
    required = (
        'TOKEN_MONITOR_CHARGE_EVENTS_PATH = "/api/token-monitor/charge-events"',
        '"deepseek-account"',
        "recordCharge(record.cost, record.timestamp, kind,",
        "cacheHit: {",
        "cacheMiss: {",
        "output: {",
    )
    if any(billing.count(anchor) < 1 for anchor in required):
        sys.exit("dsh-damage-pulse 4.2.3 的计费事件源码与已验证版本不符；未修改插件。")
    state_path = os.path.join(os.path.dirname(os.path.dirname(pulse)), ".dsh-damage-pulse", "module-state.json")
    if os.path.isfile(state_path):
        try:
            with open(state_path, encoding="utf-8") as fh:
                state = json.load(fh)
        except (OSError, ValueError) as err:
            sys.exit("无法读取计费模块状态: %s" % err)
        if "billing" in state.get("removed", []):
            sys.exit("dsh-damage-pulse 计费模块已卸载；请先在插件设置中恢复该模块。")
        if state.get("restartRequired"):
            print("提示：计费插件安装后仍要求完整重启 DSH。")
    print("preflight: dsh-damage-pulse 4.2.3 原生支持账号计费与扣费事件；无需补丁")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查，不改文件")
    ap.add_argument("--plugin-root", help="指定同一 DSH profile 的 node_modules 目录")
    args = ap.parse_args()

    plugin_root = select_plugin_root(args.plugin_root or os.environ.get("DSH_PATCH_PLUGIN_ROOT"))
    whale = os.path.join(plugin_root, "dsh-whale-widget")
    pulse = os.path.join(plugin_root, "dsh-damage-pulse")
    os.environ["DSH_PATCH_PLUGIN_ROOT"] = plugin_root
    print("=" * 64)
    print("DSH 挂件增强包 · 环境检查")
    print("  dsh-whale-widget : %s" % ((whale + "   v" + version_of(whale)) if os.path.isdir(whale) else "未找到"))
    print("  dsh-damage-pulse : %s" % ((pulse + "   v" + version_of(pulse)) if os.path.isdir(pulse) else "未找到"))
    if not os.path.isdir(whale) or not os.path.isdir(pulse):
        sys.exit("需要同时安装 dsh-whale-widget 与 dsh-damage-pulse，未修改任何文件。")

    pulse_version = version_of(pulse)
    if pulse_version == "4.2.3":
        check_modern_pulse(pulse)
        scripts = ("patch_whale_widget.py",)
    elif pulse_version == "4.0.11":
        scripts = ("patch_whale_widget.py", "patch_damage_pulse.py")
    else:
        sys.exit("只支持 dsh-damage-pulse 4.0.11 或 4.2.3；当前版本 %s。未修改插件。" % pulse_version)

    py = sys.executable or "python"
    # First check both plugins. A missing anchor or unsupported version must stop
    # the install before either live plugin is changed.
    for script in scripts:
        print("检查 %s" % script, flush=True)
        code = subprocess.run([py, os.path.join(PAYLOAD, script), "--check"]).returncode
        if code:
            sys.exit("预检失败（%s，退出码 %d）；未开始安装。" % (script, code))
    if args.check:
        print("预检通过；未修改任何文件。")
        return

    for script in scripts:
        print("=" * 64, flush=True)
        print("运行 %s" % script, flush=True)
        code = subprocess.run([py, os.path.join(PAYLOAD, script)]).returncode
        if code:
            sys.exit("补丁失败（%s，退出码 %d）。请按 README 的回滚步骤检查。" % (script, code))

    print("=" * 64)
    print("补丁完成。**请重启 DSH**（整个关掉再打开），然后：")
    print("  1) 点挂件上的 ☰ 菜单，往下拉，会看到一组新设置：")
    print("     显示余额框 / 余额框字号 / 气泡字号 / 泡泡大小 / 泡泡位置 / 泡泡抓手 / 受击动作")
    print("  2) 她脚下常驻一条余额框（可拖、可拉伸、可调字号、可隐藏）")
    print("  3) 每次模型调用结束，她头顶右上会飘出红色扣费数字（命中/未命中/输出）")
    print("  4) 那张 DeepSeek 余额泡泡可拖动、可缩放，余额实时逐笔往下掉")


if __name__ == "__main__":
    main()
