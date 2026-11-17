/**
 * 爱回收批量查价脚本（纯底价 / 过保完美）
 * 运行环境：爱回收已打开的网页上下文（首选 Chrome，其次 Edge）
 * 传入参数：
 *   - items: [{ name, model, capacity, channel, color }]
 *   - skuCache: 静态参数缓存 { "机型|容量|渠道|颜色": { productId, matchedProductName, ppvIds } }
 *   - options: { minIntervalMs?: number, maxItems?: number (默认 4；传 0 表示不限制), skipKeys?: string[], allowZoomMismatch?: boolean }
 */
function preflightCheckAHS() {
  const block = document.getElementById("waf_nc_block");
  const wafBlocked = !!block && getComputedStyle(block).display !== "none";
  const hasWebpack = Array.isArray(window.webpackChunkneom);
  const zoomedOut = window.outerWidth > 0 && window.innerWidth > window.outerWidth;
  const zoomRatioEstimate = window.innerWidth > 0 && window.outerWidth > 0
    ? Number((window.outerWidth / window.innerWidth).toFixed(2))
    : 1;
  const blockReasons = [];
  if (!hasWebpack) blockReasons.push("NO_WEBPACK_CONTEXT");
  if (wafBlocked) blockReasons.push("WAF_BLOCKED");
  if (zoomedOut) blockReasons.push("ZOOM_NOT_100_PERCENT");

  return {
    url: location.href,
    hasWebpack,
    webdriver: !!navigator.webdriver,
    wafBlocked,
    wafText: wafBlocked ? block.innerText : "",
    innerSize: [window.innerWidth, window.innerHeight],
    outerSize: [window.outerWidth, window.outerHeight],
    devicePixelRatio: window.devicePixelRatio || 1,
    zoomRatioEstimate,
    zoomedOut,
    ready: blockReasons.length === 0,
    blockReasons
  };
}

async function batchQueryAHS(items, skuCache = {}, options = {}) {
  const preflight = preflightCheckAHS();
  if (!preflight.hasWebpack) {
    return [{ error: "NO_WEBPACK_CONTEXT", preflight }];
  }
  if (preflight.wafBlocked) {
    return [{ error: "WAF_BLOCKED", wafBlocked: true, preflight }];
  }
  if (preflight.zoomedOut && !options.allowZoomMismatch) {
    return [{
      error: "ZOOM_NOT_100_PERCENT",
      message: "检测到页面存在缩小缩放（innerWidth > outerWidth），请先在浏览器按 Ctrl+0 恢复 100% 缩放后再执行。",
      preflight
    }];
  }

  let webpackRequire;
  window.webpackChunkneom.push([
    [Symbol()],
    {},
    (req) => { webpackRequire = req; }
  ]);
  const mod13035 = webpackRequire("13035");
  const mod39221 = webpackRequire("39221");

  window.__ahsProductCache = window.__ahsProductCache || {};
  const productCache = window.__ahsProductCache;

  const MIN_INTERVAL_MS = Number(options.minIntervalMs) > 0 ? Number(options.minIntervalMs) : 3000;
  const MAX_ITEMS = options.maxItems === undefined ? 4 : Number(options.maxItems);
  const skipSet = new Set(Array.isArray(options.skipKeys) ? options.skipKeys : []);

  function buildCacheKey(item) {
    const channel = item.channel || "国行";
    const color = item.color || "标准色";
    return `${item.name}|${item.capacity}|${channel}|${color}`;
  }

  let targetItems = items.filter((item) => !skipSet.has(buildCacheKey(item)));
  if (MAX_ITEMS > 0) {
    targetItems = targetItems.slice(0, MAX_ITEMS);
  }

  function withTimeout(promise, ms, label) {
    return Promise.race([
      promise,
      new Promise((_, reject) => setTimeout(() => reject(new Error("TIMEOUT:" + label)), ms))
    ]);
  }

  function isWafBlocked() {
    const block = document.getElementById("waf_nc_block");
    return !!block && getComputedStyle(block).display !== "none";
  }

  async function safeUg(productId, cityId, ppvIds) {
    if (isWafBlocked()) throw new Error("WAF_BLOCKED");
    try {
      return await withTimeout(
        mod13035.Ug({ productId, cityId, ppvIds }),
        15000,
        "Ug"
      );
    } catch (err) {
      if (isWafBlocked()) throw new Error("WAF_BLOCKED");
      if ((err?.code === 3001 || err?.code === 3002) && err?.data?.captchaUrl) {
        throw new Error("CAPTCHA_REQUIRED");
      }
      throw err;
    }
  }

  function normalizeName(s) {
    return String(s || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  function isLikelyApple(name) {
    return /^(iphone|ipad|macbook|mac|watch|airpods|apple)/i.test(name.trim());
  }

  async function getProductInfo(keyword) {
    if (productCache[keyword]) return productCache[keyword];
    const searchRes = await withTimeout(
      mod39221.$P({
        keyword: keyword,
        cityId: 103,
        bizTypes: [1],
        categoryIds: [],
        brandIds: []
      }),
      12000,
      "search"
    );
    const products = searchRes.data.products || [];
    if (!products.length) throw new Error("Product not found: " + keyword);

    const kwNorm = normalizeName(keyword);
    const appleNorm = isLikelyApple(keyword) ? normalizeName(`苹果 ${keyword}`) : kwNorm;
    const product =
      products.find(p => normalizeName(p.name) === appleNorm) ||
      products.find(p => normalizeName(p.name) === kwNorm) ||
      products.find(p => normalizeName(p.name).includes(kwNorm)) ||
      products[0];

    const rtRes = await withTimeout(mod13035.Rt({ productId: product.id, cityId: 103 }), 12000, "Rt");
    const quickItem = rtRes.data.quickInquiry.items.find(i => i.name.includes("进入桌面")) || rtRes.data.quickInquiry.items[0];
    const quickPpvs = quickItem.ppvs.map(p => p.id);

    const wfRes = await withTimeout(mod13035.Wf({ productId: product.id, quickInquiryItemId: quickItem.id, cityId: 103 }), 12000, "Wf");

    productCache[keyword] = {
      product,
      quickPpvs,
      skus: wfRes.data.skus,
      propNames: wfRes.data.propertyNames
    };
    return productCache[keyword];
  }

  async function resolvePpvIds(item) {
    const { product, quickPpvs, skus, propNames } = await getProductInfo(item.name);

    const capacityProp = propNames.find(p => p.name === '存储容量');
    const capItem = capacityProp && capacityProp.items.find(i => i.name.toLowerCase() === item.capacity.toLowerCase());
    if (!capItem) throw new Error("Capacity not found: " + item.capacity);
    const capPpvId = capItem.ppvIds[0];

    const channelProp = propNames.find(p => p.name === '购买渠道');
    const channelTarget = item.channel || '国行';
    const channelItem = channelProp ? channelProp.items.find(i => i.name.includes(channelTarget)) : null;
    const channelPpvId = channelItem ? channelItem.ppvIds[0] : 2014;

    const colorProp = propNames.find(p => p.name === '机身颜色');
    let colorPpvId = null;
    if (colorProp) {
      const cItem = colorProp.items.find(i => i.name.includes(item.color)) ||
                    colorProp.items.find(i => i.name === '官方标准色') ||
                    colorProp.items[0];
      if (cItem) colorPpvId = cItem.ppvIds[0];
    }

    let candidateSkus = skus.filter(sku => sku.includes(channelPpvId) && sku.includes(capPpvId));
    if (!candidateSkus.length) candidateSkus = skus.filter(sku => sku.includes(capPpvId));
    if (colorPpvId && candidateSkus.some(s => s.includes(colorPpvId))) {
      candidateSkus = candidateSkus.filter(s => s.includes(colorPpvId));
    }
    if (candidateSkus.some(s => s.includes(2075))) {
      candidateSkus = candidateSkus.filter(s => s.includes(2075));
    }
    const matchedSku = candidateSkus[0] || skus[0];

    const nonSkuPpvIds = [];
    for (const prop of propNames) {
      if (prop.isSkuProperty) continue;
      const pref = prop.items.find(i => i.isPreferred) || prop.items[0];
      if (pref) nonSkuPpvIds.push(...pref.ppvIds);
    }

    const fullPpvIds = Array.from(new Set([
      ...matchedSku,
      ...quickPpvs,
      ...nonSkuPpvIds
    ]));

    return {
      productId: product.id,
      matchedProductName: product.name,
      ppvIds: fullPpvIds
    };
  }

  async function querySingle(item) {
    const channel = item.channel || "国行";
    const color = item.color || "标准色";
    const cacheKey = buildCacheKey(item);
    const cached = skuCache[cacheKey];

    let resolved = cached;
    let fromCache = !!cached;

    if (!resolved) {
      resolved = await resolvePpvIds(item);
    }

    let quote;
    try {
      quote = await safeUg(resolved.productId, 103, resolved.ppvIds);
    } catch (err) {
      // Self-heal if cached ppvIds ever go stale, but do not retry quota/WAF/captcha/timeout errors
      const isQuotaOrBlock =
        err?.code === 12624008 ||
        err?.message === "WAF_BLOCKED" ||
        err?.message === "CAPTCHA_REQUIRED" ||
        String(err?.message).startsWith("TIMEOUT:");
      if (fromCache && !isQuotaOrBlock) {
        fromCache = false;
        resolved = await resolvePpvIds(item);
        quote = await safeUg(resolved.productId, 103, resolved.ppvIds);
      } else {
        throw err;
      }
    }

    return {
      name: item.name,
      model: item.model || "",
      capacity: item.capacity,
      channel,
      color,
      matchedProductName: resolved.matchedProductName,
      price: quote.data.price,
      inquiryKey: quote.data.inquiryKey,
      fromCache,
      resolvedSku: fromCache ? undefined : resolved
    };
  }

  const results = [];
  for (let i = 0; i < targetItems.length; i++) {
    const tStart = Date.now();
    try {
      results.push(await querySingle(targetItems[i]));
    } catch (e) {
      const errMsg = e?.message || e?.resultMessage || e?.msg || String(e);
      results.push({ ...targetItems[i], error: errMsg, errorCode: e?.code, wafBlocked: isWafBlocked() });
      break;
    }
    const elapsed = Date.now() - tStart;
    if (i < targetItems.length - 1 && elapsed < MIN_INTERVAL_MS) {
      await new Promise(r => setTimeout(r, MIN_INTERVAL_MS - elapsed));
    }
  }
  return results;
}
