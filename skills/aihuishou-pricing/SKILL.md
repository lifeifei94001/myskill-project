---
name: aihuishou-pricing
description: "Query recycled phone and device buyback prices from Aihuishou (爱回收, m.aihuishou.com). Use when the user wants to check recycle prices, base device valuations ('物品估价', 不加券价格), or batch quotes for smartphones (iPhone, Huawei, Xiaomi, etc.), especially for '过保' (out-of-warranty) and '完美' (flawless) conditions. Triggers on: '爱回收价格', '爱回收查价', '爱回收估价', '爬取爱回收', 'aihuishou pricing'."
---

# Aihuishou (爱回收) Device Pricing Skill

## 1. 概述 (Overview)

本技能用于通过爱回收（`m.aihuishou.com`）页面上下文对二手手机与数码设备进行纯物品回收估价（**过保 + 完美，不含加价券、新客券及会员补贴**）。

### 核心架构与最新升级
1. **Chrome 优先连接（`chrome-devtools` 首选）**：
   - 优先使用常规启动的 **Google Chrome**（在 `chrome://inspect/#remote-debugging` 开启远程调试）接入 `chrome-devtools` MCP，并在无“自动测试软件控制”横幅、100% 缩放且未拦截第三方存储的页面执行。
   - 若使用 Edge（`edge-devtools`），需关闭对 `aihuishou.com` 的跟踪防护、保持 100% 缩放（`Ctrl+0`），且避免带自动化测试控制横幅的窗口触发阿里云验证码 2.0 `F001`。
2. **静态 SKU 参数缓存直连 ([`scripts/sku_cache.json`](./scripts/sku_cache.json))**：
   - 常用机型已持久化 `productId` 与完美过保 `ppvIds` 映射，直接调用 `Ug` 获取纯底价；未命中缓存的新机型自动回退完整 `$P -> Rt -> Wf -> Ug` 并可回写缓存。
3. **每日标准机型清单与断点续查账本 ([`scripts/daily_devices.json`](./scripts/daily_devices.json) & [`scripts/daily_progress.py`](./scripts/daily_progress.py))**：
   - 默认维护每日必查 18 台机型清单，每批结果按日期落盘至 `data/quotes_YYYY-MM-DD.json`。
   - 遇到 `#waf_nc_block` 或 `CAPTCHA_REQUIRED` 时立即停机并保存已有结果，下次执行自动跳过当天已查完机型，不浪费前序请求额度。

---

## 2. 接口定义 (Endpoints)

- **搜索机型 (`mod39221.$P`)**：
  `POST https://dubai.aihuishou.com/dubai-gateway/recycle-products/search-v11`
  参数：`{ keyword, cityId: 103, bizTypes: [1], categoryIds: [], brandIds: [] }`
- **获取机型问卷与 SKU 列表 (`mod13035.Rt` & `mod13035.Wf`)**：
  `GET https://dubai.aihuishou.com/dubai-gateway/recycle-products/inquiry/{productId}?cityId=103&queryType=1`
  `GET https://dubai.aihuishou.com/dubai-gateway/recycle-products/inquiry-items?productId={productId}&quickInquiryItemId={quickId}&cityId=103`
- **获取精准底价 (`mod13035.Ug`)**：
  `POST https://dubai.aihuishou.com/dubai-gateway/inquiry/create-v3`
  参数：`{ productId, cityId: 103, ppvIds: [...] }`
  返回数据：`data.price`（页面红框展示的“纯物品估价”）

---

## 3. 执行流程 (Usage)

当用户发出查价指令时：

1. **查看当日剩余待查机型（断点续查）**：
   ```powershell
   python d:\APP\development_projects\.agents\skills\aihuishou-pricing\scripts\daily_progress.py --date <YYYY-MM-DD> pending
   ```
   若用户未指定机型列表，默认直接使用 [`scripts/daily_devices.json`](./scripts/daily_devices.json) 的 18 台标准机型，并自动过滤当天已查结果。

2. **连接浏览器并执行环境预检**：
   - 优先调用 `chrome-devtools` 的 `list_pages`（不可用时回退 `edge-devtools`），找到或打开 `https://m.aihuishou.com` 标签页。
   - 调用 [`scripts/ahs_query.js`](./scripts/ahs_query.js) 中的 `preflightCheckAHS()` 确认：`ready: true`（`hasWebpack: true`、`wafBlocked: false`、`zoomedOut: false`）。
   - **100% 缩放硬门禁**：若 `zoomedOut: true`（或 `batchQueryAHS` 返回 `ZOOM_NOT_100_PERCENT`），**禁止继续查价**，先切至前台（`select_page(..., bringToFront: true)`）提示用户在浏览器按 `Ctrl+0` 恢复 100% 缩放后再执行（避免后续触发滑块时因缩放坐标偏移导致首次滑动即判 `F001`）。
   - **合规铁律**：若检测到 `#waf_nc_block` 或弹窗验证码，**严禁**任何形式的脚本自动绕过或破解，必须切至前台（`select_page(..., bringToFront: true)`）并请用户在浏览器界面手动完成验证。

3. **分批安全查询与落盘合并（默认每批 `maxItems: 4`）**：
   - [`scripts/ahs_query.js`](./scripts/ahs_query.js) 默认配置为 `{ maxItems: 4, minIntervalMs: 3000 }`（即每次最多连续查 4 条，匹配实测单窗口免验证阈值；如需一次性全量或测试更大间隔，可显式传入 `maxItems: 0` 或更高 `minIntervalMs`）。
   - 读取 [`scripts/sku_cache.json`](./scripts/sku_cache.json) 与 [`scripts/ahs_query.js`](./scripts/ahs_query.js)，通过 `evaluate_script` 传入 `(pendingItems, skuCache, { maxItems: 4, minIntervalMs: 3000 })`。
   - 将返回的成功项写入临时 JSON 后立即合并入当日账本（同时自动回写新机型 SKU）：
     ```powershell
     python d:\APP\development_projects\.agents\skills\aihuishou-pricing\scripts\daily_progress.py --date <YYYY-MM-DD> merge --input <results.json>
     ```
   - 每日 18 台机型建议分批完成（如每批 4 台后冷却，或使用 `/schedule` 命令错峰分批续查）；若中途因 `WAF_BLOCKED` / `CAPTCHA_REQUIRED` 停止，先保存已取得的成果、向用户汇报当前进度（如 `12/18`）与剩余待查机型，待用户完成页面验证或冷却后再继续。

4. **输出对比价格表**：
   ```powershell
   python d:\APP\development_projects\.agents\skills\aihuishou-pricing\scripts\daily_progress.py --date <YYYY-MM-DD> report --compare <PREV_YYYY-MM-DD>
   ```
   按标准顺序输出完整 Markdown 对比表格；若用户需要 Excel 文件，调用 `xlsx` 技能导出。
