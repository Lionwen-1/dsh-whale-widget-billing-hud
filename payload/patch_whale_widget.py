# -*- coding: utf-8 -*-
"""给 dsh-whale-widget 打上「实时滚动 + 常驻余额条」的本地补丁。

改两个文件（幂等：每次都先从备份还原再打补丁）：
  lib/index.js           宿主：BALANCE_TTL_MS 25000 → 5000（上游余额缓存）
  assets/whale-widget.js 前端：REFRESH_MS 60000 → 15000，并追加常驻余额条模块
                         （前端文件由宿主按 mtime 热读取，硬刷新页面即生效）
  → 宿主的改动需要重启一次 DSH 才生效。
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


PKG = __find_pkg("dsh-whale-widget")
WORK = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(WORK, "whale-widget-backup-0.3.12")
def __find_node():
    """找一个可用的 node 做语法检查；找不到就跳过（不影响打补丁）。"""
    import glob as _glob
    import shutil as _sh
    return _sh.which("node") or (_glob.glob(os.path.expanduser("~/.dsh/dsh-runtimes/**/node.exe"), recursive=True)
                                 or _glob.glob(os.path.expanduser("~/.dsh/**/node"), recursive=True) or [""])[0]


NODE = __find_node()

HOST = os.path.join(PKG, "lib", "index.js")
CLIENT = os.path.join(PKG, "assets", "whale-widget.js")

HOST_TTL_FROM, HOST_TTL_TO = "const BALANCE_TTL_MS = 25000", "const BALANCE_TTL_MS = 5000"
CLIENT_MS_FROM, CLIENT_MS_TO = "var REFRESH_MS = 60000", "var REFRESH_MS = 15000"
MARK = "/*__DSHW_BALANCE_BAR__*/"


def preflight():
    """Check the exact upstream build and all required anchors before writing."""
    try:
        with open(os.path.join(PKG, "package.json"), encoding="utf-8") as fh:
            version = json.load(fh)["version"]
    except (OSError, KeyError, ValueError) as err:
        raise SystemExit("无法读取挂件插件版本: %s" % err)
    if version != "0.3.12":
        raise SystemExit("只支持 dsh-whale-widget 0.3.12；当前版本 %s。未修改插件。" % version)
    sources = (
        (HOST, os.path.join(BACKUP, "index.js")),
        (CLIENT, os.path.join(BACKUP, "whale-widget.js")),
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
    if not os.path.isfile(os.path.join(WORK, "balbox_patch.js")):
        raise SystemExit("缺少 payload/balbox_patch.js")
    required_host = [
        HOST_TTL_FROM,
        "    disposers.push(registerRoute({\n      kind: 'exact',\n      path: '/dsh-whale/size.json',",
        "    async function fetchBalance() {",
        "      if (!cred) {\n        return { ok: false, code: 'NO_KEY', error: '未配置 DEEPSEEK_API_KEY' }\n      }",
    ]
    required_client = [
        CLIENT_MS_FROM,
        "menuBtn.innerHTML = '<span></span><span></span><span></span>'",
        "root.appendChild(menuBtn)", "checkUsageAlerts(nb, state.todayUsage)",
        "menuBox.appendChild(rowRes)",
        "function usageLineFontPx(level) {\n  var n = Math.max(1, Math.min(50, Math.round(Number(level) || 7)))\n  return Math.min(40, Math.round(12 + (n - 1) * 0.8))\n}",
        "function bubbleModuleFontU(level) {\n  var n = Number(level) || 6\n  n = Math.max(1, Math.min(50, Math.round(n)))\n  return Math.round(40 + (n - 1) * 200 / 49)\n}",
        "'.dshwv-pop{position:absolute;left:0;top:0;width:100%;aspect-ratio:1026/700;",
        ".dshwv-img{position:absolute;right:0;bottom:0;width:59.45%",
    ]
    missing = (["host:%s" % item[:65] for item in required_host if host.count(item) != 1] +
               ["client:%s" % item[:65] for item in required_client if client.count(item) != 1])
    if "__DSHW_TOP_PROBE__" in client or "dshw-balance-box" in client:
        missing.append("client:已有调试或补丁代码")
    if missing:
        raise SystemExit("插件源码与已验证版本不匹配；缺少或重复锚点: " + ", ".join(missing))
    print("preflight: dsh-whale-widget 0.3.12，源码锚点通过")


parser = argparse.ArgumentParser(description="给 dsh-whale-widget 0.3.12 打补丁")
parser.add_argument("--check", action="store_true", help="仅预检，不修改文件")
args = parser.parse_args()
preflight()
if args.check:
    raise SystemExit(0)

# 1) 备份一次
if not os.path.isdir(BACKUP):
    os.makedirs(BACKUP)
    shutil.copy2(HOST, os.path.join(BACKUP, "index.js"))
    shutil.copy2(CLIENT, os.path.join(BACKUP, "whale-widget.js"))
    print("backup ->", BACKUP)
else:
    print("backup exists ->", BACKUP)

# 2) 从备份还原（保证可重复执行）
shutil.copy2(os.path.join(BACKUP, "index.js"), HOST)
shutil.copy2(os.path.join(BACKUP, "whale-widget.js"), CLIENT)

# 3) 宿主：缩短上游余额缓存
s = open(HOST, encoding="utf-8").read()
if HOST_TTL_FROM not in s:
    print("!! 宿主标记未找到:", HOST_TTL_FROM)
else:
    s = s.replace(HOST_TTL_FROM, HOST_TTL_TO, 1)
    print("host  : %s -> %s" % (HOST_TTL_FROM, HOST_TTL_TO))

# 3.5) 宿主：新增"余额框设置落盘"路由（GET 读 / POST 写 ~/.dsh/.dshw-balbox.json）
BALBOX_HOST = """
    // —— 本地补丁：余额框设置落盘（位置/宽度/厚度/字号/显隐），不只依赖浏览器缓存 ——
    const BALBOX_CFG_FILE = path.join(DSH_HOME, '.dshw-balbox.json');
    function readBalBoxCfg() {
      try { return JSON.parse(fs.readFileSync(BALBOX_CFG_FILE, 'utf8')); } catch (err) { return null; }
    }
    disposers.push(registerRoute({
      kind: 'exact',
      path: '/dsh-whale-balbox.json',
      handler: async (req, res) => {
        if (req.method === 'POST' || req.method === 'PUT') {
          try {
            const parsed = JSON.parse(await readBody(req));
            const out = {};
            for (const k of ['x', 'y', 'w', 'pad', 'fs', 'bscale', 'pscale', 'popx', 'popy', 'pgrip', 'hidden']) {
              const v = parsed ? parsed[k] : void 0;
              if (typeof v === 'number' && isFinite(v)) out[k] = v;
              else if (typeof v === 'boolean') out[k] = v;
            }
            fs.writeFileSync(BALBOX_CFG_FILE, JSON.stringify(out), 'utf8');
            res.writeHead(200, JSON_HEADERS);
            res.end(JSON.stringify({ ok: true, cfg: out }));
          } catch (err) {
            res.writeHead(400, JSON_HEADERS);
            res.end(JSON.stringify({ ok: false, error: String((err && err.message) || err).slice(0, 160) }));
          }
          return;
        }
        res.writeHead(200, JSON_HEADERS);
        res.end(JSON.stringify({ ok: true, cfg: readBalBoxCfg() }));
      },
    }))
"""
if "dsh-whale-balbox.json" in s:
    print("host  : 余额框落盘路由已存在，跳过")
else:
    anchor = ("    disposers.push(registerRoute({\n"
              "      kind: 'exact',\n"
              "      path: '/dsh-whale/size.json',")
    if anchor in s:
        s = s.replace(anchor, BALBOX_HOST.strip("\n") + "\n" + anchor, 1)
        open(HOST, "w", encoding="utf-8", newline="").write(s)
        print("host  : 已加 /dsh-whale-balbox.json 路由（设置落盘）")
    else:
        print("!! 宿主路由锚点未找到")

# 4) 前端：只放宽自身轮询间隔（余额显示交给挂件自带气泡，不再注入任何元素）
c = open(CLIENT, encoding="utf-8").read()
if "__DSHW_TOP_PROBE__" in c:
    print("!! 前端里残留探针，请先从备份还原")
if CLIENT_MS_FROM not in c:
    print("!! 前端标记未找到:", CLIENT_MS_FROM)
else:
    c = c.replace(CLIENT_MS_FROM, CLIENT_MS_TO, 1)
    print("client: %s -> %s" % (CLIENT_MS_FROM, CLIENT_MS_TO))

# 4.2) 前端：把常驻余额小框做成挂件自己的节点（代码在 balbox_patch.js，见下方读取）
_OLD_NATIVE_BOX = """// [已废弃] 余额框注入代码现由同目录 balbox_patch.js 提供
var DSHW_BALBOX_W_KEY = 'dshw-balance-box-w'
var DSHW_BALBOX_X_KEY = 'dshw-balance-box-x'
var DSHW_BALBOX_W_DEFAULT = 62   // 默认宽度（占挂件盒百分比）
var DSHW_BALBOX_X_DEFAULT = 39   // 默认左边距（%）：角色占盒子右侧 ≈59%，39% 即她正下方
var balBox = document.createElement('div')
balBox.id = 'dshw-balance-box'
balBox.style.cssText = [
  'position:absolute', 'bottom:5px', 'z-index:4',
  'display:block', 'padding:3px 8px', 'box-sizing:border-box',
  'background:rgba(255,255,255,.93)', 'border:1px solid rgba(32,49,112,.30)',
  'border-radius:8px', 'box-shadow:0 2px 8px rgba(15,30,72,.20)',
  'color:#203170', 'font-size:11px', 'line-height:1.35', 'white-space:nowrap',
  'font-variant-numeric:tabular-nums', 'pointer-events:auto', 'cursor:move',
  'user-select:none', '-webkit-user-select:none', 'text-align:center',
].join(';')
balBox.innerHTML = '<div class="dshw-bal-l1" style="font-weight:800;font-size:12.5px">余额 --</div>'
  + '<div class="dshw-bal-l2" style="font-size:10px;opacity:.85;margin-top:1px">今日 --</div>'
  + '<div class="dshw-bal-grip" title="左右拖动 = 拉伸宽度（双击恢复默认宽度）" style="position:absolute;top:0;right:-3px;width:14px;height:100%;cursor:ew-resize;border-radius:0 8px 8px 0"></div>'

// 位置(左%) + 宽度(%) 应用与持久化：拖框身左右移动，拖右边缘改宽度，双击恢复默认
function dshwBalBoxNum(key, dflt, min, max) {
  var v = NaN;
  try { v = Number(localStorage.getItem(key)); } catch (e) {}
  if (!isFinite(v)) v = dflt;
  if (v < min) v = min;
  if (v > max) v = max;
  return v;
}
function dshwBalBoxApply() {
  try {
    var el = document.getElementById('dshw-balance-box');
    if (!el) return;
    var w = dshwBalBoxNum(DSHW_BALBOX_W_KEY, DSHW_BALBOX_W_DEFAULT, 30, 100);
    var x = dshwBalBoxNum(DSHW_BALBOX_X_KEY, DSHW_BALBOX_X_DEFAULT, 0, 100 - w);
    el.style.width = w + '%';
    el.style.left = x + '%';
    el.style.right = 'auto';
    el.style.marginLeft = '0';
    el.setAttribute('data-dshw-w', String(w));
    el.setAttribute('data-dshw-x', String(x));
  } catch (e) {}
}
;(function () {
  try {
    var grip = balBox.querySelector('.dshw-bal-grip');
    if (grip) {
      grip.addEventListener('mouseenter', function () { grip.style.background = 'rgba(32,49,112,.12)' });
      grip.addEventListener('mouseleave', function () { grip.style.background = '' });
      grip.addEventListener('pointerdown', function (e) {
        e.preventDefault(); e.stopPropagation();
        try { grip.setPointerCapture(e.pointerId) } catch (err) {}
        var startX = e.clientX, startW = balBox.getBoundingClientRect().width;
        var rootEl = document.querySelector('.dshwv-root');
        var rootW = (rootEl ? rootEl.getBoundingClientRect().width : 250) || 250;
        function move(ev) {
          var pct = Math.round((startW + (ev.clientX - startX)) / rootW * 100);
          if (pct < 30) pct = 30;
          if (pct > 100) pct = 100;
          try { localStorage.setItem(DSHW_BALBOX_W_KEY, String(pct)) } catch (err) {}
          dshwBalBoxApply();
        }
        function up() {
          window.removeEventListener('pointermove', move);
          window.removeEventListener('pointerup', up);
        }
        window.addEventListener('pointermove', move);
        window.addEventListener('pointerup', up);
      });
      grip.addEventListener('dblclick', function (e) {
        e.preventDefault(); e.stopPropagation();
        try { localStorage.removeItem(DSHW_BALBOX_W_KEY) } catch (err) {}
        dshwBalBoxApply();
      });
    }
    // 拖框身 = 自由左右移动（位置记在 localStorage）
    balBox.addEventListener('pointerdown', function (e) {
      e.preventDefault(); e.stopPropagation();
      var rootEl = document.querySelector('.dshwv-root');
      var rootW = (rootEl ? rootEl.getBoundingClientRect().width : 250) || 250;
      var startX = e.clientX;
      var x0 = Number(balBox.getAttribute('data-dshw-x'));
      var w = Number(balBox.getAttribute('data-dshw-w'));
      if (!isFinite(x0)) x0 = DSHW_BALBOX_X_DEFAULT;
      if (!isFinite(w)) w = DSHW_BALBOX_W_DEFAULT;
      balBox.style.cursor = 'grabbing';
      function move(ev) {
        var nx = x0 + (ev.clientX - startX) / rootW * 100;
        if (nx < 0) nx = 0;
        if (nx > 100 - w) nx = 100 - w;
        balBox.style.left = nx + '%';
        balBox.setAttribute('data-dshw-x', String(nx));
      }
      function up() {
        balBox.style.cursor = 'move';
        try { localStorage.setItem(DSHW_BALBOX_X_KEY, String(Math.round(Number(balBox.getAttribute('data-dshw-x'))))) } catch (err) {}
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
      }
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
    });
    balBox.addEventListener('dblclick', function (e) {
      e.preventDefault(); e.stopPropagation();
      try { localStorage.removeItem(DSHW_BALBOX_X_KEY) } catch (err) {}
      dshwBalBoxApply();
    });
  } catch (e) {}
})();

// 由挂件自己的余额刷新路径直接写入（见 checkUsageAlerts 调用点后的注入）
function dshwUpdateBalBox(bal, today, isPeak) {
  try {
    var el = document.getElementById('dshw-balance-box');
    if (!el) return;
    var l1 = el.querySelector('.dshw-bal-l1');
    var l2 = el.querySelector('.dshw-bal-l2');
    if (!l1 || !l2) return;
    var b = isFinite(Number(bal)) ? Number(bal).toFixed(2) : '--';
    var t = (today === null || today === undefined) ? '--' : Number(today).toFixed(2);
    var pk = (isPeak === undefined || isPeak === null) ? ''
      : (isPeak ? ' · <b style="color:#c0392b">峰</b>' : ' · <b style="color:#1f8a4c">谷</b>');
    l1.innerHTML = '余额 ¥' + b;
    l2.innerHTML = '今日 ¥' + t + pk;
    el.title = '余额 ¥' + b + ' · 今日 ¥' + t + '（拖右边缘改宽度，双击恢复默认）';
    el.setAttribute('data-dshw-state', 'ready');
  } catch (err) {}
}
"""
BALBOX_JS = os.path.join(WORK, "balbox_patch.js")
NATIVE_BOX = open(BALBOX_JS, encoding="utf-8").read()   # 真正生效的余额框注入代码
ANCHOR_MENUBTN = "menuBtn.innerHTML = '<span></span><span></span><span></span>'"
ANCHOR_APPEND = "root.appendChild(menuBtn)"
ANCHOR_ALERT_CALL = "checkUsageAlerts(nb, state.todayUsage)"
ANCHOR_MENU_ROW = "menuBox.appendChild(rowRes)"

if "dshw-balance-box" in c:
    print("client: 脚下余额框已存在，跳过")
elif ANCHOR_MENUBTN not in c or ANCHOR_APPEND not in c or ANCHOR_ALERT_CALL not in c:
    print("!! 脚下余额框锚点未找到")
else:
    c = c.replace(ANCHOR_MENUBTN, ANCHOR_MENUBTN + "\n\n" + NATIVE_BOX.rstrip("\n"), 1)
    c = c.replace(ANCHOR_APPEND, ANCHOR_APPEND + "\nroot.appendChild(balBox)\ntry { dshwBalBoxApply() } catch (err) {}\ntry { dshwApplyPopScale() } catch (err) {}\ntry { dshwBalBoxPull() } catch (err) {}", 1)
    # 把更新挂到挂件自己的余额刷新路径上（气泡也是走这里），无需自己取数
    c = c.replace(ANCHOR_ALERT_CALL,
                  ANCHOR_ALERT_CALL + "\ntry { dshwUpdateBalBox(nb, state.todayUsage, state.isPeak) } catch (err) {}", 1)
    # 在挂件自己的 ☰ 菜单里追加「余额框」设置（显示开关 + 字号）
    if ANCHOR_MENU_ROW in c:
        c = c.replace(ANCHOR_MENU_ROW, ANCHOR_MENU_ROW + "\ntry { dshwBalSettingsMount(menuBox) } catch (err) {}", 1)
        print("client: 已在 ☰ 菜单挂入「余额框」设置（显示开关 + 字号）")
    else:
        print("!! 菜单挂载点未找到（设置项没进去）")
    # 气泡字号全局缩放：改 usageLineFontPx（气泡内容字号的唯一计算处）
    FONT_FROM = """function usageLineFontPx(level) {
  var n = Math.max(1, Math.min(50, Math.round(Number(level) || 7)))
  return Math.min(40, Math.round(12 + (n - 1) * 0.8))
}"""
    FONT_TO = """function usageLineFontPx(level) {
  var n = Math.max(1, Math.min(50, Math.round(Number(level) || 7)))
  // —— 本地补丁：全局气泡缩放（☰ 菜单「气泡字号」，存 dshw-bubble-scale）——
  var __base = 12 + (n - 1) * 0.8
  var __sc = 1
  try { var __v = Number(localStorage.getItem('dshw-bubble-scale')); if (isFinite(__v) && __v > 0) __sc = __v } catch (e) {}
  return Math.max(8, Math.min(72, Math.round(__base * __sc)))
}"""
    if FONT_FROM in c:
        c = c.replace(FONT_FROM, FONT_TO, 1)
        print("client: 提醒弹窗字号已接入全局缩放")
    else:
        print("!! 提醒弹窗字号锚点未找到")
    # 主气泡字号：row.style.fontSize = calc(var(--dshw-u) * bubbleModuleFontU(fSize))
    BU_FROM = """function bubbleModuleFontU(level) {
  var n = Number(level) || 6
  n = Math.max(1, Math.min(50, Math.round(n)))
  return Math.round(40 + (n - 1) * 200 / 49)
}"""
    BU_TO = """function bubbleModuleFontU(level) {
  var n = Number(level) || 6
  n = Math.max(1, Math.min(50, Math.round(n)))
  // —— 本地补丁：主气泡全局缩放（☰ 菜单「气泡字号」，存 dshw-bubble-scale）——
  var __base = 40 + (n - 1) * 200 / 49
  var __sc = 1
  try { var __v = Number(localStorage.getItem('dshw-bubble-scale')); if (isFinite(__v) && __v > 0) __sc = __v } catch (e) {}
  return Math.round(__base * __sc)
}"""
    # 泡泡整体缩放：.dshwv-pop 加 transform:scale(var(--dshw-bscale))
    POP_FROM = "'.dshwv-pop{position:absolute;left:0;top:0;width:100%;aspect-ratio:1026/700;"
    POP_TO = ("'.dshwv-pop{position:absolute;left:0;top:0;width:100%;aspect-ratio:1026/700;"
              "transform:translate(var(--dshw-px,0px),var(--dshw-py,0px)) "
              "scale(var(--dshw-bscale,1));transform-origin:right bottom;")
    if POP_FROM in c:
        c = c.replace(POP_FROM, POP_TO, 1)
        print("client: 泡泡整体缩放已接入（.dshwv-pop transform:scale）")
    else:
        print("!! 泡泡容器锚点未找到")
    if BU_FROM in c:
        c = c.replace(BU_FROM, BU_TO, 1)
        print("client: 主气泡字号已接入全局缩放（这才是你看的那张卡）")
    else:
        print("!! 主气泡字号锚点未找到")
    # 把角色往上抬 42px，腾出脚下那条给余额框，避免框挡住她
    IMG_FROM = ".dshwv-img{position:absolute;right:0;bottom:0;width:59.45%"
    IMG_TO = ".dshwv-img{position:absolute;right:0;bottom:42px;width:59.45%"
    if IMG_FROM in c:
        c = c.replace(IMG_FROM, IMG_TO, 1)
        print("client: 角色已上抬 42px（脚下留出余额框）")
    else:
        print("!! 角色位置锚点未找到（余额框可能仍压住她）")
    print("client: 已建脚下余额框（可拖动/拉伸/调字号/隐藏），并把更新挂到余额刷新路径")

# 4.5) 前端：没配 DEEPSEEK_API_KEY 时改走 DSH 账号登录态
ACCOUNT_HELPER = """    // —— 本地补丁：没配 DEEPSEEK_API_KEY 时，改走 DSH 账号登录态取余额 ——
    //（等价于上游 0.3.14 才有的账号态路径，这里回填到 0.3.12）
    let __dshAccountTag = null
    async function fetchBalanceViaDshAccount() {
      try {
        const account = typeof ctx.get === 'function' ? ctx.get('deepseekAccount') : undefined
        if (!account || typeof account.getBalance !== 'function') return null
        const res = await account.getBalance({
          version: '0.1.7',
          locale: 'zh-CN',
          timezoneOffsetSeconds: -new Date().getTimezoneOffset() * 60,
        })
        if (!res || res.status !== 'ready') return null
        const wallets = Array.isArray(res.value) ? res.value : []
        const bonuses = Array.isArray(res.bonusWallets) ? res.bonusWallets : []
        const cur = (wallets[0] && wallets[0].currency) || (bonuses[0] && bonuses[0].currency) || 'CNY'
        const sum = (list) => list.filter((w) => w && w.currency === cur)
          .reduce((acc, w) => acc + (Number(w.balance) || 0), 0)
        const total = sum(wallets) + sum(bonuses)
        if (!Number.isFinite(total)) return null
        if (!__dshAccountTag) __dshAccountTag = createHash('sha256').update('dsh-account:' + cur).digest('hex').slice(0, 24)
        return { ok: true, totalBalance: total, accountTag: __dshAccountTag, currency: cur, updatedAt: new Date().toISOString() }
      } catch (err) { return null }
    }
"""
ACCOUNT_ANCHOR = "    async function fetchBalance() {"
ACCOUNT_NO_KEY = """      if (!cred) {
        return { ok: false, code: 'NO_KEY', error: '未配置 DEEPSEEK_API_KEY' }
      }"""
ACCOUNT_NO_KEY_NEW = """      if (!cred) {
        const viaAccount = await fetchBalanceViaDshAccount()
        if (viaAccount) return viaAccount
        return { ok: false, code: 'NO_KEY', error: '未配置 DEEPSEEK_API_KEY' }
      }"""

if "fetchBalanceViaDshAccount" in open(HOST, encoding="utf-8").read():
    print("host  : 账号态余额桥已存在，跳过")
else:
    h = open(HOST, encoding="utf-8").read()
    if ACCOUNT_ANCHOR not in h:
        print("!! 账号态桥锚点未找到（宿主）")
    elif ACCOUNT_NO_KEY not in h:
        print("!! 账号态桥 NO_KEY 分支未找到（宿主）")
    else:
        h = h.replace(ACCOUNT_ANCHOR, ACCOUNT_HELPER.rstrip("\n") + "\n\n" + ACCOUNT_ANCHOR, 1)
        h = h.replace(ACCOUNT_NO_KEY, ACCOUNT_NO_KEY_NEW, 1)
        open(HOST, "w", encoding="utf-8", newline="").write(h)
        print("host  : 已注入 DSH 账号态余额桥（无 key 时自动启用）")

# 已改为气泡方案：不再追加独立的余额条/更新器模块（前端保持原版 + 轮询间隔调整）
print("client: 跳过独立余额条模块（余额改由挂件气泡显示）")

open(CLIENT, "w", encoding="utf-8", newline="").write(c)

# 5) 语法检查
for src, tmp, kind in ((HOST, "chk-host.mjs", "宿主 ESM"), (CLIENT, "chk-client.cjs", "前端经典脚本")):
    dst = os.path.join(tempfile.gettempdir(), tmp)
    shutil.copy2(src, dst)
    if not NODE:
        print("syntax %-12s 跳过（未找到 node，不影响补丁生效）" % kind)
        continue
    try:
        r = subprocess.run([NODE, "--check", dst], capture_output=True, text=True)
        print("syntax %-12s exit=%d %s" % (kind, r.returncode, (r.stderr or "").strip()[:200]))
        if r.returncode:
            raise SystemExit("JavaScript 语法检查失败: " + kind)
    except Exception as err:
        raise SystemExit("JavaScript 语法检查无法执行: %s" % err)

# 6) 留痕
note = os.path.join(PKG, "LOCAL-PATCH.md")
open(note, "w", encoding="utf-8").write(
    "# 本地改动（非原作者内容）\n\n"
    "- 宿主 `lib/index.js`：余额缓存缩短、账号态余额兜底、余额框设置落盘路由。需重启 DSH 生效。\n"
    "- 前端 `assets/whale-widget.js`：刷新间隔缩短，注入脚下余额框、扣费飘字和菜单设置。\n"
    "- 复现脚本：本仓库 `payload/patch_whale_widget.py`；原文件备份位于安装包的"
    " `payload/whale-widget-backup-0.3.12/`。\n"
    "- 插件升级后这些改动会被覆盖；仅在本仓库支持该版本后重新打补丁。\n"
)
print("note ->", note)
