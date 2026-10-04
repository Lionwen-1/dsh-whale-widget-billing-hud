// —— 本地补丁：脚下常驻余额框（挂件自己的节点；可拖动、可拉伸、厚度可调、字号可调、可隐藏）——
// 数据由挂件自身的余额刷新路径写入（见 checkUsageAlerts 调用点后注入的 dshwUpdateBalBox）
var DSHW_BALBOX_W_KEY = 'dshw-balance-box-w'      // 宽度（% of 挂件盒）
var DSHW_BALBOX_X_KEY = 'dshw-balance-box-x'      // 左边距（%）
var DSHW_BALBOX_Y_KEY = 'dshw-balance-box-y'      // 距挂件盒底（px）—— 上下自由移动
var DSHW_BALBOX_PAD_KEY = 'dshw-balance-box-pad'  // 上下内边距（px）= 厚度
var DSHW_BALBOX_FS_KEY = 'dshw-balance-box-fs'    // 第一行字号（px）
var DSHW_BALBOX_HIDE_KEY = 'dshw-balance-box-hidden'
var DSHW_HIT_KEY = 'dshw-hit-enabled'             // '1' = 扣费时播放本挂件的受击动作；默认关闭
var DSHW_BALBOX_W_DEFAULT = 62
var DSHW_BALBOX_X_DEFAULT = 39
var DSHW_BALBOX_Y_DEFAULT = 5
var DSHW_BALBOX_PAD_DEFAULT = 3
var DSHW_BALBOX_FS_DEFAULT = 12.5

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
  + '<div class="dshw-bal-grip-y" title="上下拖动 = 改厚度（双击恢复默认）" style="position:absolute;left:0;right:0;top:-4px;height:12px;cursor:ns-resize"></div>'

function dshwBalBoxLs(key) {
  try { return localStorage.getItem(key) } catch (e) { return null }
}
function dshwBalBoxLsSet(key, val) {
  try { if (val === null) localStorage.removeItem(key); else localStorage.setItem(key, val) } catch (e) {}
}
function dshwBalBoxNum(key, dflt, min, max) {
  var v = Number(dshwBalBoxLs(key))
  if (!isFinite(v)) v = dflt
  if (v < min) v = min
  if (v > max) v = max
  return v
}

// —— 落盘同步：设置同时存到 ~/.dsh/.dshw-balbox.json（换浏览器/清缓存也不丢） ——
var DSHW_BALBOX_CFG_URL = '/dsh-whale-balbox.json'
var DSHW_BUBBLE_SCALE_KEY = 'dshw-bubble-scale'
var DSHW_BUBBLE_SCALE_DEFAULT = 1
var DSHW_POP_SCALE_KEY = 'dshw-pop-scale'      // 整个泡泡（那张卡）的大小
var DSHW_POP_SCALE_DEFAULT = 1
var DSHW_POP_X_KEY = 'dshw-pop-x'              // 泡泡自由位移（px）
var DSHW_POP_Y_KEY = 'dshw-pop-y'
var DSHW_POP_GRIP_KEY = 'dshw-pop-grip-hidden' // '1' = 隐藏拖动抓手
var dshwBalBoxPushTimer = null
function dshwBalBoxSnapshot() {
  return {
    x: dshwBalBoxNum(DSHW_BALBOX_X_KEY, DSHW_BALBOX_X_DEFAULT, 0, 100),
    y: dshwBalBoxNum(DSHW_BALBOX_Y_KEY, DSHW_BALBOX_Y_DEFAULT, 0, 5000),
    w: dshwBalBoxNum(DSHW_BALBOX_W_KEY, DSHW_BALBOX_W_DEFAULT, 30, 100),
    pad: dshwBalBoxNum(DSHW_BALBOX_PAD_KEY, DSHW_BALBOX_PAD_DEFAULT, 0, 20),
    fs: dshwBalBoxNum(DSHW_BALBOX_FS_KEY, DSHW_BALBOX_FS_DEFAULT, 8, 24),
    bscale: dshwBalBoxNum(DSHW_BUBBLE_SCALE_KEY, DSHW_BUBBLE_SCALE_DEFAULT, 0.4, 2.5),
    pscale: dshwBalBoxNum(DSHW_POP_SCALE_KEY, DSHW_POP_SCALE_DEFAULT, 0.4, 2.5),
    popx: dshwBalBoxNum(DSHW_POP_X_KEY, 0, -5000, 5000),
    popy: dshwBalBoxNum(DSHW_POP_Y_KEY, 0, -5000, 5000),
    pgrip: dshwBalBoxLs(DSHW_POP_GRIP_KEY) === '1',
    hidden: dshwBalBoxLs(DSHW_BALBOX_HIDE_KEY) === '1',
    hit: dshwBalBoxLs(DSHW_HIT_KEY) === '1',
  }
}
function dshwBalBoxPush() {
  try {
    if (dshwBalBoxPushTimer) clearTimeout(dshwBalBoxPushTimer)
    dshwBalBoxPushTimer = setTimeout(function () {
      try {
        fetch(DSHW_BALBOX_CFG_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dshwBalBoxSnapshot()),
        }).catch(function () {})
      } catch (e) {}
    }, 400)
  } catch (e) {}
}
function dshwBalBoxPull() {
  try {
    fetch(DSHW_BALBOX_CFG_URL, { cache: 'no-store' })
      .then(function (r) { return r.json() })
      .then(function (d) {
        var cfg = d && d.cfg
        if (!cfg || typeof cfg !== 'object') return
        if (isFinite(Number(cfg.x))) dshwBalBoxLsSet(DSHW_BALBOX_X_KEY, String(Number(cfg.x)))
        if (isFinite(Number(cfg.y))) dshwBalBoxLsSet(DSHW_BALBOX_Y_KEY, String(Number(cfg.y)))
        if (isFinite(Number(cfg.w))) dshwBalBoxLsSet(DSHW_BALBOX_W_KEY, String(Number(cfg.w)))
        if (isFinite(Number(cfg.pad))) dshwBalBoxLsSet(DSHW_BALBOX_PAD_KEY, String(Number(cfg.pad)))
        if (isFinite(Number(cfg.fs))) dshwBalBoxLsSet(DSHW_BALBOX_FS_KEY, String(Number(cfg.fs)))
        if (isFinite(Number(cfg.bscale))) dshwBalBoxLsSet(DSHW_BUBBLE_SCALE_KEY, String(Number(cfg.bscale)))
        if (isFinite(Number(cfg.pscale))) dshwBalBoxLsSet(DSHW_POP_SCALE_KEY, String(Number(cfg.pscale)))
        if (isFinite(Number(cfg.popx))) dshwBalBoxLsSet(DSHW_POP_X_KEY, String(Number(cfg.popx)))
        if (isFinite(Number(cfg.popy))) dshwBalBoxLsSet(DSHW_POP_Y_KEY, String(Number(cfg.popy)))
        if (typeof cfg.pgrip === 'boolean') dshwBalBoxLsSet(DSHW_POP_GRIP_KEY, cfg.pgrip ? null : '1')
        if (typeof cfg.hidden === 'boolean') dshwBalBoxLsSet(DSHW_BALBOX_HIDE_KEY, cfg.hidden ? '1' : null)
        if (typeof cfg.hit === 'boolean') dshwBalBoxLsSet(DSHW_HIT_KEY, cfg.hit ? '1' : null)
        dshwBalBoxApply()
        dshwApplyPopScale()
        try { dshwRepaintBubble() } catch (e) {}
      })
      .catch(function () {})
  } catch (e) {}
}

// 统一应用：显示/隐藏、左位置、宽度、厚度(内边距)、字号
function dshwBalBoxApply() {
  try {
    var el = document.getElementById('dshw-balance-box')
    if (!el) return
    el.style.display = dshwBalBoxLs(DSHW_BALBOX_HIDE_KEY) === '1' ? 'none' : 'block'
    var w = dshwBalBoxNum(DSHW_BALBOX_W_KEY, DSHW_BALBOX_W_DEFAULT, 30, 100)
    var x = dshwBalBoxNum(DSHW_BALBOX_X_KEY, DSHW_BALBOX_X_DEFAULT, 0, 100 - w)
    var pad = dshwBalBoxNum(DSHW_BALBOX_PAD_KEY, DSHW_BALBOX_PAD_DEFAULT, 0, 20)
    var fs = dshwBalBoxNum(DSHW_BALBOX_FS_KEY, DSHW_BALBOX_FS_DEFAULT, 8, 24)
    var yMax = (function () {
      var r = document.querySelector('.dshwv-root')
      var h = r ? r.getBoundingClientRect().height : 250
      return Math.max(0, Math.round((h || 250) - el.getBoundingClientRect().height))
    })()
    var y = dshwBalBoxNum(DSHW_BALBOX_Y_KEY, DSHW_BALBOX_Y_DEFAULT, 0, Math.max(yMax, DSHW_BALBOX_Y_DEFAULT))
    el.style.width = w + '%'
    el.style.left = x + '%'
    el.style.right = 'auto'
    el.style.marginLeft = '0'
    el.style.bottom = y + 'px'
    el.style.padding = pad + 'px 8px'
    el.setAttribute('data-dshw-w', String(w))
    el.setAttribute('data-dshw-x', String(x))
    el.setAttribute('data-dshw-y', String(y))
    var l1 = el.querySelector('.dshw-bal-l1')
    var l2 = el.querySelector('.dshw-bal-l2')
    if (l1) l1.style.fontSize = fs + 'px'
    if (l2) l2.style.fontSize = Math.max(8, Math.round(fs * 0.8 * 10) / 10) + 'px'
    dshwBalBoxPush()   // 任何一次应用都同步落盘（防抖 400ms）
  } catch (e) {}
}

// 整个泡泡（那张卡）的缩放 + 自由位移：写成 CSS 变量，由 .dshwv-pop 的 transform 消费
function dshwApplyPopScale() {
  try {
    var sc = dshwBalBoxNum(DSHW_POP_SCALE_KEY, DSHW_POP_SCALE_DEFAULT, 0.4, 2.5)
    var px = dshwBalBoxNum(DSHW_POP_X_KEY, 0, -5000, 5000)
    var py = dshwBalBoxNum(DSHW_POP_Y_KEY, 0, -5000, 5000)
    var rootEl = document.querySelector('.dshwv-root')
    var targets = [rootEl, document.documentElement]
    for (var i = 0; i < targets.length; i++) {
      var t = targets[i]
      if (!t || !t.style) continue
      t.style.setProperty('--dshw-bscale', String(sc))
      t.style.setProperty('--dshw-px', Math.round(px) + 'px')
      t.style.setProperty('--dshw-py', Math.round(py) + 'px')
    }
    dshwPopHandle()
  } catch (e) {}
}

// 泡泡拖动抓手（贴在泡泡顶边中间，悬停变清晰；双击复位）
var dshwPopDragging = false
function dshwPopHandle() {
  try {
    var rootEl = document.querySelector('.dshwv-root')
    if (!rootEl) return
    var gripHidden = dshwBalBoxLs(DSHW_POP_GRIP_KEY) === '1'
    var exist = document.getElementById('dshw-pop-grip')
    if (exist) {
      exist.style.display = gripHidden ? 'none' : 'flex'
      return
    }
    if (gripHidden) return
    var g = document.createElement('div')
    g.id = 'dshw-pop-grip'
    g.title = '按住拖动 = 移动泡泡位置（双击复位）'
    g.innerHTML = '<span style="display:block;width:26px;height:3px;border-radius:2px;background:rgba(32,49,112,.45)"></span>'
    g.style.cssText = 'position:absolute;left:50%;top:6px;margin-left:-26px;width:52px;height:16px;'
      + 'display:flex;align-items:center;justify-content:center;cursor:move;pointer-events:auto;z-index:8;'
      + 'background:rgba(255,255,255,.72);border:1px solid rgba(32,49,112,.22);border-radius:8px;'
      + 'opacity:.45;transition:opacity .15s;box-shadow:0 1px 4px rgba(15,30,72,.15)'
    rootEl.appendChild(g)
    g.addEventListener('mouseenter', function () { g.style.opacity = '1' })
    g.addEventListener('mouseleave', function () { if (!dshwPopDragging) g.style.opacity = '.45' })
    g.addEventListener('pointerdown', function (e) {
      e.preventDefault(); e.stopPropagation()
      dshwPopDragging = true
      g.style.opacity = '1'
      var sx = e.clientX, sy = e.clientY
      var x0 = dshwBalBoxNum(DSHW_POP_X_KEY, 0, -5000, 5000)
      var y0 = dshwBalBoxNum(DSHW_POP_Y_KEY, 0, -5000, 5000)
      function move(ev) {
        dshwBalBoxLsSet(DSHW_POP_X_KEY, String(Math.round(x0 + (ev.clientX - sx))))
        dshwBalBoxLsSet(DSHW_POP_Y_KEY, String(Math.round(y0 + (ev.clientY - sy))))
        dshwApplyPopScale()
      }
      function up() {
        dshwPopDragging = false
        g.style.opacity = '.45'
        dshwBalBoxPush()
        window.removeEventListener('pointermove', move)
        window.removeEventListener('pointerup', up)
      }
      window.addEventListener('pointermove', move)
      window.addEventListener('pointerup', up)
    })
    g.addEventListener('dblclick', function (e) {
      e.preventDefault(); e.stopPropagation()
      dshwBalBoxLsSet(DSHW_POP_X_KEY, null)
      dshwBalBoxLsSet(DSHW_POP_Y_KEY, null)
      dshwApplyPopScale()
      dshwBalBoxPush()
    })
  } catch (e) {}
}

// 拖动：右边缘=宽度，上边缘=厚度，框身=左右移动；双击=该项复位
;(function () {
  try {
    var rootEl = function () { return document.querySelector('.dshwv-root') }
    var rootW = function () { var r = rootEl(); return (r ? r.getBoundingClientRect().width : 250) || 250 }

    var gripX = balBox.querySelector('.dshw-bal-grip')
    if (gripX) {
      gripX.addEventListener('mouseenter', function () { gripX.style.background = 'rgba(32,49,112,.12)' })
      gripX.addEventListener('mouseleave', function () { gripX.style.background = '' })
      gripX.addEventListener('pointerdown', function (e) {
        e.preventDefault(); e.stopPropagation()
        try { gripX.setPointerCapture(e.pointerId) } catch (err) {}
        var sx = e.clientX, sw = balBox.getBoundingClientRect().width
        function move(ev) {
          var pct = Math.round((sw + (ev.clientX - sx)) / rootW() * 100)
          if (pct < 30) pct = 30
          if (pct > 100) pct = 100
          dshwBalBoxLsSet(DSHW_BALBOX_W_KEY, String(pct))
          dshwBalBoxApply()
        }
        function up() { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up) }
        window.addEventListener('pointermove', move); window.addEventListener('pointerup', up)
      })
      gripX.addEventListener('dblclick', function (e) {
        e.preventDefault(); e.stopPropagation()
        dshwBalBoxLsSet(DSHW_BALBOX_W_KEY, null); dshwBalBoxApply()
      })
    }

    var gripY = balBox.querySelector('.dshw-bal-grip-y')
    if (gripY) {
      gripY.addEventListener('mouseenter', function () { gripY.style.background = 'rgba(32,49,112,.12)'; gripY.style.borderRadius = '8px 8px 0 0' })
      gripY.addEventListener('mouseleave', function () { gripY.style.background = '' })
      gripY.addEventListener('pointerdown', function (e) {
        e.preventDefault(); e.stopPropagation()
        try { gripY.setPointerCapture(e.pointerId) } catch (err) {}
        var sy = e.clientY
        var pad0 = dshwBalBoxNum(DSHW_BALBOX_PAD_KEY, DSHW_BALBOX_PAD_DEFAULT, 0, 20)
        function move(ev) {
          var pad = Math.round((pad0 - (ev.clientY - sy) / 2) * 10) / 10   // 往上拖 = 变厚
          if (pad < 0) pad = 0
          if (pad > 20) pad = 20
          dshwBalBoxLsSet(DSHW_BALBOX_PAD_KEY, String(pad))
          dshwBalBoxApply()
        }
        function up() { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up) }
        window.addEventListener('pointermove', move); window.addEventListener('pointerup', up)
      })
      gripY.addEventListener('dblclick', function (e) {
        e.preventDefault(); e.stopPropagation()
        dshwBalBoxLsSet(DSHW_BALBOX_PAD_KEY, null); dshwBalBoxApply()
      })
    }

    balBox.addEventListener('pointerdown', function (e) {
      e.preventDefault(); e.stopPropagation()
      var sx = e.clientX, sy = e.clientY
      var x0 = Number(balBox.getAttribute('data-dshw-x'))
      var y0 = Number(balBox.getAttribute('data-dshw-y'))
      var w = Number(balBox.getAttribute('data-dshw-w'))
      if (!isFinite(x0)) x0 = DSHW_BALBOX_X_DEFAULT
      if (!isFinite(y0)) y0 = DSHW_BALBOX_Y_DEFAULT
      if (!isFinite(w)) w = DSHW_BALBOX_W_DEFAULT
      var r = rootEl()
      var rootH = (r ? r.getBoundingClientRect().height : 250) || 250
      var boxH = balBox.getBoundingClientRect().height || 30
      var yMax = Math.max(0, Math.round(rootH - boxH))
      balBox.style.cursor = 'grabbing'
      function move(ev) {
        var nx = x0 + (ev.clientX - sx) / rootW() * 100
        if (nx < 0) nx = 0
        if (nx > 100 - w) nx = 100 - w
        balBox.style.left = nx + '%'
        balBox.setAttribute('data-dshw-x', String(nx))
        var ny = y0 + (sy - ev.clientY)          // 往上拖 = 升高
        if (ny < 0) ny = 0
        if (ny > yMax) ny = yMax
        balBox.style.bottom = ny + 'px'
        balBox.setAttribute('data-dshw-y', String(ny))
      }
      function up() {
        balBox.style.cursor = 'move'
        dshwBalBoxLsSet(DSHW_BALBOX_X_KEY, String(Math.round(Number(balBox.getAttribute('data-dshw-x')))))
        dshwBalBoxLsSet(DSHW_BALBOX_Y_KEY, String(Math.round(Number(balBox.getAttribute('data-dshw-y')))))
        window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up)
      }
      window.addEventListener('pointermove', move); window.addEventListener('pointerup', up)
    })
    balBox.addEventListener('dblclick', function (e) {
      e.preventDefault(); e.stopPropagation()
      dshwBalBoxLsSet(DSHW_BALBOX_X_KEY, null)
      dshwBalBoxLsSet(DSHW_BALBOX_Y_KEY, null)
      dshwBalBoxApply()
    })
  } catch (e) {}
})()

// —— ☰ 菜单里的设置项：显示开关 + 字号（布局复用挂件原生行 .dshwv-menu-row / .dshwv-range / .dshwv-number）——
function dshwBalSettingsMount(parent) {
  try {
    if (!parent || parent.querySelector('.dshw-bal-settings')) return

    var rowShow = menuRow()
    rowShow.className = 'dshwv-menu-row dshw-bal-settings'
    rowShow.appendChild(menuLabel('显示余额框'))
    var chk = document.createElement('input')
    chk.type = 'checkbox'
    chk.className = 'dshwv-check'
    chk.style.marginLeft = 'auto'
    chk.checked = dshwBalBoxLs(DSHW_BALBOX_HIDE_KEY) !== '1'
    chk.title = '取消勾选即隐藏她脚下的余额框（数据仍在后台刷新）'
    chk.addEventListener('change', function () {
      dshwBalBoxLsSet(DSHW_BALBOX_HIDE_KEY, chk.checked ? null : '1')
      dshwBalBoxApply()
    })
    rowShow.appendChild(chk)
    parent.appendChild(rowShow)

    var rowFs = menuRow()
    rowFs.appendChild(menuLabel('余额框字号'))
    var slider = document.createElement('input')
    slider.type = 'range'
    slider.className = 'dshwv-range'
    slider.min = '8'; slider.max = '24'; slider.step = '0.5'
    slider.value = String(dshwBalBoxNum(DSHW_BALBOX_FS_KEY, DSHW_BALBOX_FS_DEFAULT, 8, 24))
    slider.title = '拖动调整框内字号（8~24px）'
    var num = document.createElement('input')
    num.type = 'number'
    num.className = 'dshwv-number'
    num.min = '8'; num.max = '24'; num.step = '0.5'
    num.value = slider.value
    num.title = '也可以直接填数字'
    function put(v) {
      var fs = Number(v)
      if (!isFinite(fs)) fs = DSHW_BALBOX_FS_DEFAULT
      if (fs < 8) fs = 8
      if (fs > 24) fs = 24
      dshwBalBoxLsSet(DSHW_BALBOX_FS_KEY, String(fs))
      dshwBalBoxApply()
      slider.value = String(fs)
      num.value = String(fs)
    }
    slider.addEventListener('input', function () { put(slider.value) })
    num.addEventListener('change', function () { put(num.value) })
    rowFs.appendChild(slider)
    rowFs.appendChild(num)
    parent.appendChild(rowFs)

    // —— 气泡字号（整张余额卡的气泡文字统一缩放）——
    var rowBs = menuRow()
    rowBs.appendChild(menuLabel('气泡字号'))
    var bs = document.createElement('input')
    bs.type = 'range'
    bs.className = 'dshwv-range'
    bs.min = '0.5'; bs.max = '2'; bs.step = '0.05'
    bs.value = String(dshwBalBoxNum(DSHW_BUBBLE_SCALE_KEY, DSHW_BUBBLE_SCALE_DEFAULT, 0.4, 2.5))
    bs.title = '整张余额气泡的字号倍数（0.5~2.0，1=默认）'
    var bsNum = document.createElement('input')
    bsNum.type = 'number'
    bsNum.className = 'dshwv-number'
    bsNum.min = '0.5'; bsNum.max = '2'; bsNum.step = '0.05'
    bsNum.value = bs.value
    bsNum.title = '也可以直接填倍数'
    function putScale(v) {
      var sc = Number(v)
      if (!isFinite(sc)) sc = DSHW_BUBBLE_SCALE_DEFAULT
      if (sc < 0.5) sc = 0.5
      if (sc > 2) sc = 2
      dshwBalBoxLsSet(DSHW_BUBBLE_SCALE_KEY, String(sc))
      bs.value = String(sc)
      bsNum.value = String(sc)
      dshwRepaintBubble()          // 立刻重绘一次，直接看到大小变化
      dshwBalBoxPush()             // 一并落盘
    }
    bs.addEventListener('input', function () { putScale(bs.value) })
    bsNum.addEventListener('change', function () { putScale(bsNum.value) })
    rowBs.appendChild(bs)
    rowBs.appendChild(bsNum)
    parent.appendChild(rowBs)

    // —— 泡泡大小（整张卡的尺寸：形状 + 文字一起缩放）——
    var rowPs = menuRow()
    rowPs.appendChild(menuLabel('泡泡大小'))
    var ps = document.createElement('input')
    ps.type = 'range'
    ps.className = 'dshwv-range'
    ps.min = '0.5'; ps.max = '2'; ps.step = '0.05'
    ps.value = String(dshwBalBoxNum(DSHW_POP_SCALE_KEY, DSHW_POP_SCALE_DEFAULT, 0.4, 2.5))
    ps.title = '整张卡的大小倍数（0.5~2.0，1=默认，随挂件「大小」一起放大缩小）'
    var psNum = document.createElement('input')
    psNum.type = 'number'
    psNum.className = 'dshwv-number'
    psNum.min = '0.5'; psNum.max = '2'; psNum.step = '0.05'
    psNum.value = ps.value
    psNum.title = '也可以直接填倍数'
    function putPop(v) {
      var sc = Number(v)
      if (!isFinite(sc)) sc = DSHW_POP_SCALE_DEFAULT
      if (sc < 0.5) sc = 0.5
      if (sc > 2) sc = 2
      dshwBalBoxLsSet(DSHW_POP_SCALE_KEY, String(sc))
      ps.value = String(sc)
      psNum.value = String(sc)
      dshwApplyPopScale()
      dshwRepaintBubble()
      dshwBalBoxPush()
    }
    ps.addEventListener('input', function () { putPop(ps.value) })
    psNum.addEventListener('change', function () { putPop(psNum.value) })
    rowPs.appendChild(ps)
    rowPs.appendChild(psNum)
    parent.appendChild(rowPs)

    // —— 泡泡位置：复位按钮（拖动方式见泡泡顶边的抓手）——
    var rowPp = menuRow()
    rowPp.appendChild(menuLabel('泡泡位置'))
    var ppReset = document.createElement('button')
    ppReset.type = 'button'
    ppReset.textContent = '复位'
    ppReset.title = '把泡泡移回原位（也可以双击泡泡顶边的抓手）'
    ppReset.style.cssText = 'flex:0 0 auto;margin-left:auto;border:1px dashed rgba(32,49,112,.5);'
      + 'border-radius:6px;background:transparent;color:#203170;font-size:12px;padding:2px 10px;cursor:pointer'
    ppReset.addEventListener('click', function (e) {
      e.stopPropagation()
      dshwBalBoxLsSet(DSHW_POP_X_KEY, null)
      dshwBalBoxLsSet(DSHW_POP_Y_KEY, null)
      dshwApplyPopScale()
      dshwBalBoxPush()
    })
    rowPp.appendChild(ppReset)
    parent.appendChild(rowPp)

    // —— 泡泡抓手：显示 / 隐藏（藏起来后仍可在菜单里再打开）——
    var rowGrip = menuRow()
    rowGrip.appendChild(menuLabel('泡泡抓手'))
    var gripChk = document.createElement('input')
    gripChk.type = 'checkbox'
    gripChk.className = 'dshwv-check'
    gripChk.style.marginLeft = 'auto'
    gripChk.checked = dshwBalBoxLs(DSHW_POP_GRIP_KEY) !== '1'
    gripChk.title = '取消勾选即隐藏泡泡顶边那条拖动抓手（想再拖动就回来重新勾选）'
    gripChk.addEventListener('change', function () {
      dshwBalBoxLsSet(DSHW_POP_GRIP_KEY, gripChk.checked ? null : '1')
      dshwPopHandle()
      dshwBalBoxPush()
    })
    rowGrip.appendChild(gripChk)
    parent.appendChild(rowGrip)

    var rowHit = menuRow()
    rowHit.appendChild(menuLabel('受击动作'))
    var hitChk = document.createElement('input')
    hitChk.type = 'checkbox'
    hitChk.className = 'dshwv-check'
    hitChk.style.marginLeft = 'auto'
    hitChk.checked = dshwBalBoxLs(DSHW_HIT_KEY) === '1'
    hitChk.title = '开启后每次扣费让当前黑鲸角色轻微受击；关闭后仍显示扣费飘字'
    hitChk.addEventListener('change', function () {
      dshwBalBoxLsSet(DSHW_HIT_KEY, hitChk.checked ? '1' : null)
      dshwBalBoxPush()
    })
    rowHit.appendChild(hitChk)
    parent.appendChild(rowHit)
  } catch (e) {}
}

// 立刻重绘当前气泡（改字号后立即生效；未显示时顺带弹出来当预览）
function dshwRepaintBubble() {
  try {
    if (typeof showUsagePopup !== 'function' || !usageSet || !usageSet.alert || !usageSet.alert.on) return
    var a = usageSet.alert
    showUsagePopup('余额预警', usageRemindLinesOf(a, true), Number(a.below) || 0, null, 2, a)
  } catch (e) {}
}

// 由挂件自己的余额刷新路径直接写入（见 checkUsageAlerts 调用点后的注入）
var dshwLastBal = null        // 最近一次真实余额
var dshwLocalDelta = 0        // 本地逐笔扣减累计（真实余额到达时归零校正）
var DSHW_BAL_DECIMALS = 4     // 余额显示小数位

function dshwRenderBalance() {
  try {
    var el = document.getElementById('dshw-balance-box')
    if (!el) return
    var l1 = el.querySelector('.dshw-bal-l1')
    if (!l1) return
    var shown = (dshwLastBal === null) ? null : (dshwLastBal - dshwLocalDelta)
    l1.innerHTML = '余额 ¥' + (shown === null ? '--' : Number(shown).toFixed(DSHW_BAL_DECIMALS))
    el.title = '余额 ¥' + (shown === null ? '--' : Number(shown).toFixed(DSHW_BAL_DECIMALS))
      + '（拖框身移动 / 右边缘改宽 / 上边缘改厚 / 双击复位）'
  } catch (e) {}
}

function dshwUpdateBalBox(bal, today, isPeak) {
  try {
    var el = document.getElementById('dshw-balance-box')
    if (!el) return
    var l2 = el.querySelector('.dshw-bal-l2')
    if (!l2) return
    if (isFinite(Number(bal))) { dshwLastBal = Number(bal); dshwLocalDelta = 0 }
    var t = (today === null || today === undefined) ? '--' : Number(today).toFixed(2)
    var pk = (isPeak === undefined || isPeak === null) ? ''
      : (isPeak ? ' · <b style="color:#c0392b">峰</b>' : ' · <b style="color:#1f8a4c">谷</b>')
    dshwRenderBalance()
    l2.innerHTML = '今日 ¥' + t + pk
    el.setAttribute('data-dshw-state', 'ready')
  } catch (err) {}
}

// ============================================================================
// 扣费飘字（从 dsh-damage-pulse 搬进挂件）
// 数据源：GET /api/token-monitor/charge-events?since=<seq>
//   → { streamId, seq, firstSeq, dropped, events:[{ seq, id, kind?, cost,
//        breakdown:{ cacheHit:{cost}, cacheMiss:{cost}, output:{cost} } }] }
// 效果：每次模型调用在她旁边飘出红色数字（命中 / 未命中 / 输出），
//       同时把脚下余额框**逐笔实时扣减**；下一次真实余额到达时自动校正。
// ============================================================================
var DSHW_CHARGE_URL = '/api/token-monitor/charge-events'
var DSHW_CHARGE_MS = 1000
var dshwChargeSeq = null
var dshwChargeStream
var dshwChargeSeeded = false
var dshwLastHitAt = 0

// 灵感：dsh-damage-pulse (MIT) 的「事件驱动受击反馈」；动画与设置实现均为本项目原创。
// 仅作用于当前已选中的挂件 <img>，不携带或切换任何第三方角色素材。
function dshwPlayHit() {
  try {
    if (dshwBalBoxLs(DSHW_HIT_KEY) !== '1') return
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    var now = Date.now()
    if (now - dshwLastHitAt < 800) return
    var target = document.querySelector('.dshwv-root .dshwv-img')
    if (!target || typeof target.animate !== 'function') return
    dshwLastHitAt = now
    target.animate([
      { transform: 'translateX(0) rotate(0deg)', filter: 'brightness(1)' },
      { transform: 'translateX(-4px) rotate(-3deg)', filter: 'brightness(1.28)', offset: 0.22 },
      { transform: 'translateX(4px) rotate(2deg)', filter: 'brightness(1.12)', offset: 0.48 },
      { transform: 'translateX(-2px) rotate(-1deg)', filter: 'brightness(1.04)', offset: 0.74 },
      { transform: 'translateX(0) rotate(0deg)', filter: 'brightness(1)' },
    ], { duration: 560, easing: 'ease-out' })
  } catch (e) {}
}

function dshwDamageLayer() {
  try {
    var layer = document.getElementById('dshw-damage-layer')
    if (layer) return layer
    var rootEl = document.querySelector('.dshwv-root')
    if (!rootEl) return null
    layer = document.createElement('div')
    layer.id = 'dshw-damage-layer'
    // 位置：与 ☰ 菜单按钮同一水平线（挂件盒 top: calc(40.55% + 4px)），红字从这条线**往上叠**
    layer.style.cssText = 'position:absolute;right:6px;bottom:59.45%;width:auto;max-width:80%;'
      + 'text-align:right;z-index:6;pointer-events:none'
    rootEl.appendChild(layer)
    return layer
  } catch (e) { return null }
}

function dshwSpawnDamage(label, cost, offsetPx, delayMs) {
  try {
    var layer = dshwDamageLayer()
    if (!layer) return
    var negative = cost < 0                       // 负数 = 退款/加费
    var el = document.createElement('div')
    el.textContent = label + ' ' + (negative ? '+' : '-') + Math.abs(cost).toFixed(4) + '¥'
    el.style.cssText = 'position:absolute;right:0;bottom:' + offsetPx + 'px;text-align:right;'
      + 'font:700 13px/1.3 "Microsoft YaHei",sans-serif;white-space:nowrap;color:'
      + (negative ? '#30a46c' : '#ff3b30') + ';text-shadow:0 0 6px '
      + (negative ? 'rgba(48,164,108,.9),0 0 14px rgba(48,164,108,.5)' : 'rgba(255,59,48,.9),0 0 14px rgba(255,59,48,.5)')
    layer.appendChild(el)
    var anim = el.animate(
      [
        { opacity: 0, transform: 'translate3d(0,8px,0) scale(.94)' },
        { opacity: 1, transform: 'translate3d(0,0,0) scale(1)', offset: 0.22 },
        { opacity: 1, transform: 'translate3d(0,-10px,0) scale(1)', offset: 0.62 },
        { opacity: 0, transform: 'translate3d(0,-26px,0) scale(1)' },
      ],
      { duration: 3000, delay: delayMs || 0, easing: 'cubic-bezier(.25,.46,.45,.94)', fill: 'forwards' }
    )
    anim.onfinish = function () { try { el.remove() } catch (e) {} }
    setTimeout(function () { try { el.remove() } catch (e) {} }, (delayMs || 0) + 3600)
  } catch (e) {}
}

function dshwDamageParts(ev) {
  var out = []
  var kind = ev && ev.kind
  if (typeof kind === 'string') {
    var label = kind === 'miss' ? '未命中' : (kind === 'output' ? '输出' : '命中')
    out.push({ label: label, cost: Number(ev.cost) || 0 })
    return out
  }
  var b = (ev && ev.breakdown) || {}
  var hit = Number(b.cacheHit && b.cacheHit.cost) || 0
  var miss = Number(b.cacheMiss && b.cacheMiss.cost) || 0
  var put = Number(b.output && b.output.cost) || 0
  if (hit) out.push({ label: '命中', cost: hit })
  if (miss) out.push({ label: '未命中', cost: miss })
  if (put) out.push({ label: '输出', cost: put })
  return out
}

function dshwChargePoll() {
  try {
    if (document.hidden) return
    var url = DSHW_CHARGE_URL + (dshwChargeSeq === null ? '' : '?since=' + dshwChargeSeq)
    fetch(url, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null })
      .then(function (d) {
        if (!d || !Array.isArray(d.events)) return
        if (!dshwChargeSeeded || (dshwChargeStream !== undefined && d.streamId !== dshwChargeStream)) {
          // 首次进入 / 事件流换了：只对齐序号，不补飘历史
          dshwChargeSeeded = true
          dshwChargeStream = d.streamId
          dshwChargeSeq = Number(d.seq) || 0
          return
        }
        dshwChargeStream = d.streamId
        var fresh = d.events
          .filter(function (e) { return Number.isFinite(e.seq) && e.seq > dshwChargeSeq })
          .sort(function (a, b) { return a.seq - b.seq })
        if (!fresh.length) return
        var slot = 0
        for (var i = 0; i < fresh.length; i++) {
          var ev = fresh[i]
          dshwChargeSeq = Math.max(dshwChargeSeq, Number(ev.seq) || 0)
          var parts = dshwDamageParts(ev)
          var total = 0
          for (var k = 0; k < parts.length; k++) total += parts[k].cost
          if (!parts.length) { total = Number(ev.cost) || 0; parts = [{ label: '扣费', cost: total }] }
          if (total > 0) dshwPlayHit()
          for (var p = 0; p < parts.length; p++) {
            // 一条一条跳：每条间隔 900ms，纵向每 22px 一行，从上往下排（最多 5 行循环）
            dshwSpawnDamage(parts[p].label, parts[p].cost, 4 + (slot % 5) * 22, (slot % 5) * 900)
            slot++
          }
          // 逐笔实时扣减（真实余额到达时会被校正回 0）
          if (isFinite(total) && total !== 0) {
            dshwLocalDelta += total
            dshwRenderBalance()
          }
        }
      })
      .catch(function () {})
  } catch (e) {}
}

;(function () {
  try {
    setInterval(dshwChargePoll, DSHW_CHARGE_MS)
    setTimeout(dshwChargePoll, 1200)
  } catch (e) {}
})()
