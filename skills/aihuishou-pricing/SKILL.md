---
name: aihuishou-pricing
description: "Query recycled phone and device buyback prices from Aihuishou (爱回收, m.aihuishou.com). Use when the user wants to check recycle prices, base device valuations ('物品估价', 不加券价格), or batch quotes for smartphones (iPhone, Huawei, Xiaomi, etc.), especially for '过保' (out-of-warranty) and '完美' (flawless) conditions. Triggers on: '爱回收价格', '爱回收查价', '爱回收估价', '爬取爱回收', 'aihuishou pricing'."
---

# Aihuishou (爱回收) Device Pricing Skill

## 1. 概述 (Overview)

本技能用于通过爱回收（m.aihuishou.com）底层 API 对二手手机与数码设备进行高效率、精准的纯物品回收估价（不含加价券、新客券及会员补贴）。

### 核心优势与极速架构
1. **静态 SKU 参数缓存直连 (`scripts/sku_cache.json`)**：
   - 常用机型已持久化保存 `productId` 与完美过保 `ppvIds` 映射，**跳过前 3 步接口**（搜机型 `$P`、快速询价 `Rt`、SKU 属性 `Wf`），直接 1 步调用估价接口 `Ug`，请求量减少 70%+。
   - 若遇到未缓存的新机型，自动走完整 `$P -> Rt -> Wf -> Ug` 并支持自愈回退；若为华为/小米/三星等非苹果机型，自动按原名精准匹配 `matchedProductName`。
2. **自适应防风控节流**：
   - 爱回收网关（`dubai.aihuishou.com`）部署阿里云 WAF 校验（`antidom.js` / `decode__1903`），脚本内按单次实际耗时动态补齐 2 秒最小间隔（若 WAF 校验已耗时 >2 秒则零等待直接发下一条），兼顾防滑块风控与极限速度。
3. **图形验证码自动识别**：
   - 需保证后台运行本地 [`ocr_server.py`](../../../../ocr_server.py)（基于 `ddddocr`，监听 `127.0.0.1:18888`）。遇爱回收 3001/3002 图像验证码时毫秒级自动识别并带参重试。
4. **无需登录账号**：
   - 估价接口对匿名访客开放，保持 Edge/Chrome 打开任一 `https://m.aihuishou.com` 页面注入执行即可。

---

## 2. 接口定义 (Reverse-Engineered Endpoints)

- **搜索机型 (`mod39221.$P`)**：
  `POST https://dubai.aihuishou.com/dubai-gateway/recycle-products/search-v11`
  参数：`{ keyword, cityId: 103, bizTypes: [1], categoryIds: [], brandIds: [] }`
- **获取机型问卷与 SKU 列表 (`mod13035.Rt` & `mod13035.Wf`)**：
  `GET https://dubai.aihuishou.com/dubai-gateway/recycle-products/inquiry/{productId}?cityId=103&queryType=1`
  `GET https://dubai.aihuishou.com/dubai-gateway/recycle-products/inquiry-items?productId={productId}&quickInquiryItemId={quickId}&cityId=103`
- **获取精准底价 (`mod13035.Ug`)**：
  `POST https://dubai.aihuishou.com/dubai-gateway/inquiry/create-v3`
  参数：`{ productId, cityId: 103, ppvIds: [...], imgCaptcha?: '...' }`
  返回数据：`data.price`（即为页面红框展示的“纯物品估价”）

---

## 3. 执行流程 (Usage)

当用户发出查价指令时：
1. 检查本地 [`ocr_server.py`](../../../../ocr_server.py) 是否在后台运行；若未启动，先以守护进程启动 `python ocr_server.py`。
2. 通过 `edge-devtools`（或 `chrome-devtools`）检查或打开一个独立的 `https://m.aihuishou.com` 标签页（确保页面无 `#waf_nc_block` 滑块拦截；若触发滑块需由用户在浏览器完成滑动）。
3. 读取 [`scripts/sku_cache.json`](./scripts/sku_cache.json) 与 [`scripts/ahs_query.js`](./scripts/ahs_query.js)，通过 `evaluate_script` 传入 `(items, skuCache)` **单批执行**（常规 18 台缓存机型仅需 18 次 `Ug` 调用，可一次跑完）。
4. 若本次出现未命中的新机型，将返回结果中的 `resolvedSku` 追加写入 [`scripts/sku_cache.json`](./scripts/sku_cache.json) 以持久化加速。
5. 输出规整的 Markdown 对比价格表格；若用户要求表格文件，调用 `xlsx` 技能导出。
