# -*- coding: utf-8 -*-
"""给 dsh-damage-pulse 打两处本地补丁（幂等：先从备份还原再打）：

1) 余额：没配 DEEPSEEK_API_KEY 时走 DSH 账号登录态（ctx.deepseekAccount.getBalance）
2) 计费资格：originally 只认 provider === "deepseek-official"，
   而本机 DSH 用的是 "deepseek-account" → 一次调用都不计费、没有红色飘字。
   放开为同时接受这两个 provider（宿主 + 客户端两处门禁都改）。

宿主改动需重启 DSH；客户端改动硬刷新页面即可。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def __find_pkg(name):
    """在任意 DSH profile 下找插件目录（不写死 profile 名）。"""
    import glob as _glob
    override = os.environ.get("DSH_PATCH_PLUGIN_ROOT")
    if override:
        candidate = os.path.join(override, name)
        if os.path.isdir(candidate):
            return candidate
        raise SystemExit("测试插件目录不存在: " + candidate)
    pats = [
        os.path.expanduser("~/.dsh/profiles/*/node_modules/" + name),
        os.path.expanduser("~/.dsh/**/node_modules/" + name),
    ]
    for pat in pats:
        hits = _glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    raise SystemExit("!! 找不到插件目录 " + name + "，请先在 DSH 里安装该插件再运行本脚本")


PKG = __find_pkg("dsh-damage-pulse")
WORK = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(WORK, "damage-pulse-backup-4.0.11")
HOST = os.path.join(PKG, "lib", "index.js")
CLIENT = os.path.join(PKG, "lib", "client.js")
def __find_node():
    """找一个可用的 node 做语法检查；找不到就跳过（不影响打补丁）。"""
    import glob as _glob
    import shutil as _sh
    return _sh.which("node") or (_glob.glob(os.path.expanduser("~/.dsh/dsh-runtimes/**/node.exe"), recursive=True)
                                 or _glob.glob(os.path.expanduser("~/.dsh/**/node"), recursive=True) or [""])[0]


NODE = __find_node()
OTHER_PROVIDER = "deepseek-account"

# ---------- 1) 余额兜底（宿主） ----------
HELPER = '''/** 本地补丁：余额链路诊断——每次尝试写一行到 DATA_DIR/balance-probe.txt，便于外部查看卡在哪。 */
function pulseProbe(line) {
	try {
		mkdirSync(DATA_DIR, { recursive: true });
		appendFileSync(join(DATA_DIR, "balance-probe.txt"), new Date().toISOString() + " " + line + "\\n");
	} catch (err) {}
}
/** 本地补丁：没配 DEEPSEEK_API_KEY 时，改走 DSH 账号登录态取余额（充值钱包 + 赠金钱包）。 */
async function fetchBalanceViaDshAccount(ctx) {
	try {
		const account = ctx && typeof ctx.get === "function" ? ctx.get("deepseekAccount") : void 0;
		if (!account || typeof account.getBalance !== "function") {
			pulseProbe("账号服务不可用（ctx.get 返回 " + (account === void 0 ? "undefined" : typeof account) + "）");
			return void 0;
		}
		const res = await account.getBalance({
			version: "0.1.7",
			locale: "zh-CN",
			timezoneOffsetSeconds: -new Date().getTimezoneOffset() * 60
		});
		if (!res || res.status !== "ready") {
			pulseProbe("getBalance 返回 status=" + (res && res.status));
			return void 0;
		}
		const wallets = Array.isArray(res.value) ? res.value : [];
		const bonuses = Array.isArray(res.bonusWallets) ? res.bonusWallets : [];
		const cur = (wallets[0] && wallets[0].currency) || (bonuses[0] && bonuses[0].currency) || "CNY";
		const sum = (list) => list.filter((w) => w && w.currency === cur)
			.reduce((acc, w) => acc + (Number(w.balance) || 0), 0);
		const total = sum(wallets) + sum(bonuses);
		if (!Number.isFinite(total)) return void 0;
		return {
			currency: cur,
			totalBalance: total,
			grantedBalance: sum(bonuses),
			toppedUpBalance: sum(wallets),
			isAvailable: true,
			updatedAt: Date.now()
		};
	} catch (err) {
		return void 0;
	}
}
'''
ANCHOR_HELPER = "/** 余额服务：定时轮询 + 缓存最新值。 */"
ANCHOR_NO_KEY = "if (apiKey === void 0) {"
INJECT = '''if (apiKey === void 0) {
				const viaAccount = await fetchBalanceViaDshAccount(this.ctx);
				if (viaAccount) {
					this.latest = viaAccount;
					if (this.lastLoggedTotal !== viaAccount.totalBalance) {
						this.lastLoggedTotal = viaAccount.totalBalance;
						console.log("[dsh-token-monitor] 余额 " + viaAccount.currency + " " + viaAccount.totalBalance.toFixed(2) + "（DSH 账号态）");
					}
					return viaAccount;
				}'''

# ---------- 2) 计费资格放开（宿主 + 客户端） ----------
# 启动时快速重试 + 缩短轮询：插件一加载就查余额，那时账号服务常未就绪，原版要干等 60s
START_FROM = """	start() {
		this.refresh();
		this.timer = setInterval(() => void this.refresh(), this.pollMs);
	}"""
START_TO = """	start() {
		// 本地补丁：开机第一次常拿不到账号服务 → 快速重试（2.5s×12），之后仍按 pollMs 轮询
		let _tries = 0;
		const _kick = () => {
			_tries += 1;
			Promise.resolve().then(() => this.refresh()).then((r) => {
				if (!r && _tries < 12) setTimeout(_kick, 2500);
			}).catch(() => { if (_tries < 12) setTimeout(_kick, 2500); });
		};
		setTimeout(_kick, 1500);
		this.timer = setInterval(() => void this.refresh(), this.pollMs);
	}"""
POLL_FROM = "constructor(ctx, pollMs = 6e4) {"
POLL_TO = "constructor(ctx, pollMs = 15e3) {"
HOST_GATE_FROM = 'if (provider !== "deepseek-official" || typeof model !== "string") return void 0;'
HOST_GATE_TO = ('if ((provider !== "deepseek-official" && provider !== "%s") || typeof model !== "string") return void 0;'
                % OTHER_PROVIDER)
CLIENT_GATE_FROM = 'if (pricing.provider !== "deepseek-official") return false;'
CLIENT_GATE_TO = ('if (pricing.provider !== "deepseek-official" && pricing.provider !== "%s") return false;'
                  % OTHER_PROVIDER)
CLIENT_RET_FROM = 'return current.provider === pricing.provider && typeof current.model === "string" && matchesPricedModel(current.model, pricing.models);'
CLIENT_RET_TO = ('const __okProv = ["deepseek-official", "%s"];\n'
                 'return __okProv.indexOf(current.provider) >= 0 && __okProv.indexOf(pricing.provider) >= 0 '
                 '&& typeof current.model === "string" && matchesPricedModel(current.model, pricing.models);'
                 % OTHER_PROVIDER)

# 隐藏它自己的悬浮窗（鲸鱼娘 + 余额卡）：飘字已由 dsh-whale-widget 的挂件接管，
# 避免"两个人物 / 两套余额"。想恢复：把下面这行 display 去掉再跑一次本脚本。
CARD_FROM = 'const CARD = {\n\t\t\tposition: "fixed",'
CARD_TO = 'const CARD = {\n\t\t\tdisplay: "none",   // 本地补丁：隐去自带悬浮窗（改用挂件内的飘字与余额）\n\t\t\tposition: "fixed",'


def preflight():
    """Check the exact upstream build and all required anchors before writing."""
    try:
        with open(os.path.join(PKG, "package.json"), encoding="utf-8") as fh:
            version = json.load(fh)["version"]
    except (OSError, KeyError, ValueError) as err:
        raise SystemExit("无法读取计费插件版本: %s" % err)
    if version != "4.0.11":
        raise SystemExit("只支持 dsh-damage-pulse 4.0.11；当前版本 %s。未修改插件。" % version)
    sources = (
        (HOST, os.path.join(BACKUP, "index.js")),
        (CLIENT, os.path.join(BACKUP, "client.js")),
    )
    if os.path.isdir(BACKUP) and not all(os.path.isfile(saved) for _, saved in sources):
        raise SystemExit("备份不完整，请人工检查 %s" % BACKUP)
    try:
        bodies = []
        for live, saved in sources:
            with open(saved if os.path.isdir(BACKUP) else live, encoding="utf-8") as fh:
                bodies.append(fh.read())
        host, client = bodies
    except OSError as err:
        raise SystemExit("无法读取插件源码: %s" % err)
    required_host = [ANCHOR_HELPER, ANCHOR_NO_KEY, HOST_GATE_FROM,
                     "return {\n\t\tprovider: OFFICIAL_PROVIDER_ID,\n\t\tmodel,", START_FROM, POLL_FROM]
    required_client = [CLIENT_GATE_FROM, CLIENT_RET_FROM, CARD_FROM]
    missing = (["host:%s" % item[:65] for item in required_host if host.count(item) != 1] +
               ["client:%s" % item[:65] for item in required_client if client.count(item) != 1])
    if "fetchBalanceViaDshAccount" in host or "__okProv" in client:
        missing.append("已有本地补丁代码")
    if missing:
        raise SystemExit("插件源码与已验证版本不匹配；缺少或重复锚点: " + ", ".join(missing))
    print("preflight: dsh-damage-pulse 4.0.11，源码锚点通过")


parser = argparse.ArgumentParser(description="给 dsh-damage-pulse 4.0.11 打补丁")
parser.add_argument("--check", action="store_true", help="仅预检，不修改文件")
args = parser.parse_args()
preflight()
if args.check:
    raise SystemExit(0)

# 备份
if not os.path.isdir(BACKUP):
    os.makedirs(BACKUP)
    shutil.copy2(HOST, os.path.join(BACKUP, "index.js"))
    print("backup ->", BACKUP)
else:
    print("backup exists ->", BACKUP)
if not os.path.exists(os.path.join(BACKUP, "client.js")):
    shutil.copy2(CLIENT, os.path.join(BACKUP, "client.js"))
    print("backup client.js ->", BACKUP)

shutil.copy2(os.path.join(BACKUP, "index.js"), HOST)
shutil.copy2(os.path.join(BACKUP, "client.js"), CLIENT)

# 1) 宿主：余额兜底
s = open(HOST, encoding="utf-8").read()
if ANCHOR_HELPER in s and ANCHOR_NO_KEY in s:
    s = s.replace(ANCHOR_HELPER, HELPER + ANCHOR_HELPER, 1)
    i = s.index(ANCHOR_NO_KEY)
    line_start = s.rfind("\n", 0, i) + 1
    indent = re.match(r"[ \t]*", s[line_start:i]).group(0)
    body = INJECT.replace("\n\t\t\t\t", "\n" + indent + "\t")
    s = s[:line_start] + indent + body + s[i + len(ANCHOR_NO_KEY):]
    print("host  : 已注入账号态余额兜底")
else:
    print("!! 余额兜底锚点未找到")

# 2) 宿主：计费资格放开 + 返回真实 provider
if HOST_GATE_FROM in s:
    s = s.replace(HOST_GATE_FROM, HOST_GATE_TO, 1)
    print("host  : 计费资格已放开（接受 %s）" % OTHER_PROVIDER)
else:
    print("!! 宿主计费资格锚点未找到")
j = s.find("function resolvePricingEligibility")
if j >= 0:
    seg = s[j:j + 800]
    if "provider: OFFICIAL_PROVIDER_ID" in seg:
        seg2 = seg.replace("provider: OFFICIAL_PROVIDER_ID", "provider: provider", 1)
        s = s[:j] + seg2 + s[j + 800:]
        print("host  : 返回的 provider 改为真实值（客户端比对才通过）")

# 3) 宿主：启动快速重试 + 轮询 60s → 15s
if START_FROM in s:
    s = s.replace(START_FROM, START_TO, 1)
    print("host  : 余额启动改为快速重试（2.5s×12）")
else:
    print("!! start() 锚点未找到")
if POLL_FROM in s:
    s = s.replace(POLL_FROM, POLL_TO, 1)
    print("host  : 余额轮询 60s -> 15s")
else:
    print("!! pollMs 锚点未找到")
open(HOST, "w", encoding="utf-8", newline="").write(s)

# 3) 客户端：两道门禁放开
c = open(CLIENT, encoding="utf-8").read()
n1 = c.count(CLIENT_GATE_FROM)
n2 = c.count(CLIENT_RET_FROM)
if n1:
    c = c.replace(CLIENT_GATE_FROM, CLIENT_GATE_TO, 1)
if n2:
    c = c.replace(CLIENT_RET_FROM, CLIENT_RET_TO, 1)
if CARD_FROM in c:
    c = c.replace(CARD_FROM, CARD_TO, 1)
    print("client: 自带悬浮窗已隐藏（飘字改由挂件渲染）")
else:
    print("!! CARD 锚点未找到（悬浮窗仍在显示）")
open(CLIENT, "w", encoding="utf-8", newline="").write(c)
print("client: 门禁改动 前置检查=%d 处，provider 比对=%d 处" % (n1, n2))

# 语法检查
for path, tmp, kind in ((HOST, "chk-dp-host.mjs", "宿主"), (CLIENT, "chk-dp-client.mjs", "客户端")):
    dst = os.path.join(tempfile.gettempdir(), tmp)
    shutil.copy2(path, dst)
    if not NODE:
        print("syntax %-4s 跳过（未找到 node，不影响补丁生效）" % kind)
        continue
    try:
        r = subprocess.run([NODE, "--check", dst], capture_output=True, text=True)
        print("syntax %-4s exit=%d %s" % (kind, r.returncode, (r.stderr or "").strip()[:200]))
        if r.returncode:
            raise SystemExit("JavaScript 语法检查失败: " + kind)
    except Exception as err:
        raise SystemExit("JavaScript 语法检查无法执行: %s" % err)

note = os.path.join(PKG, "LOCAL-PATCH.md")
open(note, "w", encoding="utf-8").write(
    "# 本地改动（非原作者内容）\n\n"
    "1. `lib/index.js`：`BalanceService.refresh()` 在「未配置 DEEPSEEK_API_KEY」时兜底走\n"
    "   `ctx.get(\"deepseekAccount\").getBalance(...)`（充值钱包 + 赠金钱包）。\n"
    "2. **计费资格放开**：原作者只认 `provider === \"deepseek-official\"`，而本机 DSH 用 "
    "`deepseek-account`，\n"
    "   导致所有调用被判「不合格」→ 无账本、无红色飘字。现宿主 `resolvePricingEligibility()` "
    "与客户端\n"
    "   `isRouteEligible()` 均接受这两个 provider，且宿主返回真实 provider 以便客户端比对通过。\n"
    "3. 宿主改动需**重启 DSH**；客户端改动**硬刷新页面**。\n"
    "   复现脚本：本仓库 `payload/patch_damage_pulse.py`（幂等）；备份：安装包内的"
    " `payload/damage-pulse-backup-4.0.11/`。\n"
)
print("note ->", note)
