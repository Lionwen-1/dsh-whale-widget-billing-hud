# 机制说明与踩坑记录

给想改代码或排查问题的人。全部结论来自 Windows + DSH `0.1.7-rc.2` 的实测。

---

## 一、为什么"余额实时扣"这条路这么绕

DSH 桌面版默认走**账号登录态**（provider = `deepseek-account`），不配 `DEEPSEEK_API_KEY`。
而两个社区插件都假设你配了 API Key：

| 插件 | 它原本的假设 | 结果 |
|---|---|---|
| `dsh-whale-widget` | `credentialRef("DEEPSEEK_API_KEY")` → `api.deepseek.com/user/balance` | 拿不到 Key → 余额区一直空 |
| `dsh-damage-pulse` | 同上，**并且**要求 `provider === "deepseek-official"` 才计费 | 一次调用都不记账 → 没有红字、没有卡片 |

**关键坑**：`dsh-damage-pulse` 里写死了一行

```js
/** DSH 内 DeepSeek 官方供应商的稳定 ID；只有该供应商具备计费资格。 */
const OFFICIAL_PROVIDER_ID = "deepseek-official";
```

而 DSH 账号态的 provider 是 `deepseek-account`。于是：

- 宿主 `resolvePricingEligibility()` 每次返回 `undefined` → `UsageStorage` 拒绝入库
- 客户端 `isRouteEligible()` 第一句 `if (pricing.provider !== "deepseek-official") return false` → 连渲染都不进

**所以补丁要同时放开两处**，并且让宿主**返回真实的 provider**，客户端的
`current.provider === pricing.provider` 比对才能通过：

```js
// 宿主
if ((provider !== "deepseek-official" && provider !== "deepseek-account") || typeof model !== "string") return void 0;
...
return { provider: provider, model, matchedModel: matched[0], price: matched[1] };
// 客户端
if (pricing.provider !== "deepseek-official" && pricing.provider !== "deepseek-account") return false;
const __okProv = ["deepseek-official", "deepseek-account"];
return __okProv.indexOf(current.provider) >= 0 && __okProv.indexOf(pricing.provider) >= 0 && ...
```

放开之后，账本立刻开始写：`~/.dsh/data/dsh-token-monitor/usage.jsonl`，
每行形如 `{provider:"deepseek-account", model:"deepseek-flash", costInput, costCacheRead, costOutput, cost}`。

### 余额怎么拿

两个插件都注入了同一个兜底：如果取不到 API Key，就调 DSH 的服务

```js
const account = ctx.get("deepseekAccount");
const res = await account.getBalance({ version, locale, timezoneOffsetSeconds });
// res.status === "ready" → { value: AccountWallet[], bonusWallets: AccountWallet[] }
// 每个 wallet: { currency, balance: "12.34" }
```

把充值钱包 + 赠金钱包按币种求和，映射成插件内部形状
`{currency,totalBalance,grantedBalance,toppedUpBalance}` 即可。

### 余额卡住不显示的一个真坑

`damage-pulse` 的 `BalanceService.start()` **一开机就查一次**，那时 `deepseekAccount`
服务还没就绪 → 拿不到 → 而重试间隔是 **60 秒**，卡片会长时间停在
「未配置 API Key 或查询失败」。补丁做了两件事：启动后 **2.5s × 12 次快速重试**，轮询 60s → 15s。

---

## 二、前端脚本的缓存与生效时机

| 事实 | 结论 |
|---|---|
| 插件的前端 JS 由宿主按 **mtime** 判断是否重读，且响应头 `no-store` | 改前端文件后**理论上硬刷新即可** |
| 但桌面壳（Electron）里 `Ctrl+R` **不会重新加载注入脚本** | 实测必须**整只重启 DSH** |
| 新插件的 `<script>` 注入行是 DSH **启动时收集**的 | 新增插件一定要重启 |

另外：宿主对插件文件有内存缓存，但按 mtime 失效；如果改了文件却没生效，
先确认你没有把 mtime 改回去（例如从备份复制时保留了旧时间戳）。

---

## 三、余额框（脚下那条）是怎么接上数据的

**不要自己 fetch 余额**（试过，失败原因难查）。正确做法是**挂在挂件自己的刷新路径上**：

```js
// whale-widget 的余额刷新函数里，这一行每次都会执行（气泡也走这里）
checkUsageAlerts(nb, state.todayUsage)
// 补丁：紧跟其后写入脚下框
try { dshwUpdateBalBox(nb, state.todayUsage, state.isPeak) } catch (err) {}
```

`nb` = 最新余额数字，`state.todayUsage` = 今日已用，`state.isPeak` = 峰谷状态。

**累计扣减的实时感**：脚下框除了真实余额，还维护一个本地累加 `dshwLocalDelta`，
每收到一条扣费事件就减一次并立即重绘；下一次真实余额到达时把 delta 归零校正。

---

## 四、飘字数据从哪来

`dsh-damage-pulse` 的宿主开了一条只读接口：

```
GET /api/token-monitor/charge-events?since=<seq>
→ { streamId, seq, firstSeq, dropped, events: [ { seq, id, kind?, cost,
      breakdown: { cacheHit:{cost}, cacheMiss:{cost}, output:{cost} } } ] }
```

协议要点（照它客户端的做法）：

1. **首次**只对齐 `streamId` + `seq`，**不补飘历史**（否则一进页面炸出一堆旧数字）
2. `streamId` 变了、`seq` 回退、`dropped === true` → 视为断流，重新对齐
3. 只处理 `seq > 上次` 的事件，按 `seq` 升序
4. 事件自带 `kind` 时用它的标签（`miss`→未命中、`output`→输出、其余→命中）；
   否则从 `breakdown` 里取三种费用各飘一条

飘字本身用 Web Animations API，不注入 CSS，容器挂在挂件根节点里（跟着角色一起被缩放/移动）。

---

## 五、气泡字号 / 大小 / 位置分别改哪里

| 想改什么 | 改哪个 | 为什么 |
|---|---|---|
| 气泡**文字**大小 | `bubbleModuleFontU(level)` | 主气泡每行的 `font-size: calc(var(--dshw-u) * bubbleModuleFontU(size))`；改这里所有模块一起缩放，相对比例不变 |
| 气泡**整体**大小 + 位置 | CSS 规则 `.dshwv-pop` 的 `transform` | 它原本没有任何 transform，加 `translate(var(--dshw-px),var(--dshw-py)) scale(var(--dshw-bscale))` 最安全；两个变量由 JS 写在挂件根节点上 |
| 提醒弹窗字号 | `usageLineFontPx(level)` | 它只管 `showUsagePopup` 那条路径，**不是**你看的那张常驻卡（第一版就是改错这里，白改） |
| 角色上抬（给脚下框腾位置） | CSS `.dshwv-img` 的 `bottom` | 默认 `0`，补丁改成 `42px` |

---

## 六、踩过的坑清单（照抄省时间）

1. **`.dshwv-usage-more` 类不能当按钮用**：它的 CSS 是 `width:100%`，放进菜单行会把整行撑爆。
   菜单行要复刻原生写法：`menuRow()` + `menuLabel()` + `.dshwv-range`（`flex:1`）/ `.dshwv-number`（`width:44px`）/ `.dshwv-check`。
2. **`checkUsageAlerts` 里的 `usageAlertBelowFired` 只触发一次**：`below` 设成很大的数（如 999999）
   再配 `autoClose:false`，卡片就会"出现后永不自动关闭"。
3. **余额气泡内容可以整段照抄**：`BUBBLE_DEFAULT_ITEMS[0].modules` 就是出厂默认那 5 个模块
   （文本 + 大字余额 + 今日已用 + 峰谷徽章 + 倒计时），比手搓模板稳。
4. **持久化别只信 localStorage**：加一对宿主路由把设置写进 `~/.dsh/.dshw-balbox.json`
   （`registerRoute` + `readBody` + `JSON_HEADERS` 都是插件宿主里现成的工具），跨浏览器/清缓存都不丢。
5. **补丁脚本必须"先还原备份再打"**：否则第二次运行会在已有补丁上再叠一层，越改越乱。
6. **HTML 里不能自建会被覆盖的节点**：挂件的菜单/泡泡会重建 DOM，自己 append 进去的东西会消失；
   要么挂进它自己的创建流程，要么每次重建后再挂（`MutationObserver`）。
7. **跨插件数据用 HTTP 接口，不要读别人的内存**：`/api/token-monitor/charge-events` 就是这种接口。
8. **改完一定要 `node --check`**：注入的代码混在被注入的文件里，语法错了整段脚本都不会执行（表现是"什么都没发生"，很难查）。

---

## 七、想继续调参，改这些数

| 位置 | 变量 | 含义 |
|---|---|---|
| `payload/balbox_patch.js` | `DSHW_BAL_DECIMALS` | 余额小数位（默认 4） |
| 同上 | `DSHW_BALBOX_X_DEFAULT` / `_Y_DEFAULT` | 脚下框默认位置（39% / 5px） |
| 同上 | `duration: 3000` | 飘字单条时长（毫秒） |
| 同上 | `(slot % 5) * 900` | 多条飘字之间的间隔（毫秒） |
| 同上 | `bottom:59.45%` | 飘字整块锚点（与 ☰ 按钮同高） |
| `payload/patch_whale_widget.py` | `IMG_TO` | 角色上抬像素 |
| 同上 | `BALBOX_HOST` | 落盘路由的字段白名单 |
| `payload/patch_damage_pulse.py` | `START_TO` / `POLL_TO` | 余额快速重试与轮询间隔 |

改完重跑 `python install.py`，再重启 DSH。
