/**
 * user/custom.js — 纯汉化保真模式 + 原生右键/三点菜单按需汉化 + 外框动态文案汉化
 * 1. 通过 media="not all" 禁用 #ag-custom-fonts 主题样式，完整保留 Antigravity 官方原版配色与字体。
 * 2. 仅在右键菜单或「更多选项 (⋮)」点击瞬间开启 80ms 按需拦截，平时 100% 保持原生 Array.prototype.map。
 * 3. 轻量汉化顶栏/侧栏动态时间戳与外框按钮提示，严格绕过对话正文、代码编辑器与终端。
 */
((ctx) => {
  // 1. 纯汉化保真模式：保留 #ag-custom-fonts 节点供 verify 校验，同时禁用其样式规则以维持原版外观
  const baseStyle = document.getElementById('ag-custom-fonts');
  if (baseStyle && baseStyle.getAttribute('media') !== 'not all') {
    baseStyle.setAttribute('media', 'not all');
  }

  // 2. 右键菜单与三点菜单按需瞬时拦截（80ms 窗口后自动还原原生 Array.prototype.map）
  if (window.__ag_orig_array_map) {
    Array.prototype.map = window.__ag_orig_array_map;
  } else {
    window.__ag_orig_array_map = Array.prototype.map;
  }
  const origArrayMap = window.__ag_orig_array_map;

  function translateMenuLabel(raw) {
    if (!raw || typeof raw !== 'string') return raw;
    const trimmed = raw.trim();
    if (!trimmed) return raw;
    const dict = (ctx && ctx.dict) || window.__ag_i18n_dict;
    if (dict && typeof dict[trimmed] === 'string') {
      return dict[trimmed];
    }
    if (trimmed.endsWith(' (Default)')) {
      const base = trimmed.slice(0, -10).trim();
      const baseZh = dict && typeof dict[base] === 'string' ? dict[base] : base;
      return `${baseZh}（默认）`;
    }
    if (trimmed.startsWith('Move to Group: ')) {
      return '移动到分组：' + trimmed.slice(15);
    }
    if (trimmed.startsWith('Close ')) {
      return '关闭 ' + trimmed.slice(6);
    }
    if (trimmed.startsWith('Open in ')) {
      return '在 ' + trimmed.slice(8) + ' 中打开';
    }
    return raw;
  }

  function translateMenuItemsInPlace(arr) {
    if (!Array.isArray(arr)) return;
    for (let i = 0; i < arr.length; i++) {
      const item = arr[i];
      if (!item || typeof item !== 'object') continue;
      if (typeof item.label === 'string') {
        item.label = translateMenuLabel(item.label);
      }
      if (Array.isArray(item.submenu)) {
        translateMenuItemsInPlace(item.submenu);
      }
      if (Array.isArray(item.items)) {
        translateMenuItemsInPlace(item.items);
      }
    }
  }

  let mapRestoreTimer = null;
  function enableTempMenuMapHook() {
    if (mapRestoreTimer) clearTimeout(mapRestoreTimer);
    Array.prototype.map = function (fn, thisArg) {
      const res = origArrayMap.call(this, fn, thisArg);
      if (res && res.length > 0 && res.length <= 60) {
        const first = res[0];
        if (
          first &&
          typeof first === 'object' &&
          !first.$$typeof &&
          (('label' in first && ('accelerator' in first || 'onClick' in first || 'type' in first)) ||
            first.type === 'separator')
        ) {
          translateMenuItemsInPlace(res);
        }
      }
      return res;
    };
    mapRestoreTimer = setTimeout(() => {
      Array.prototype.map = origArrayMap;
      mapRestoreTimer = null;
    }, 80);
  }

  const onContextMenu = () => enableTempMenuMapHook();
  const onMenuBtnTrigger = (e) => {
    const t = e.target;
    if (
      t &&
      t.closest &&
      t.closest('[data-testid="conversation-kebab"], [data-testid*="more"], [aria-haspopup="menu"], [aria-label="More options"], [aria-label="更多选项"]')
    ) {
      enableTempMenuMapHook();
    }
  };
  window.addEventListener('contextmenu', onContextMenu, true);
  window.addEventListener('pointerdown', onMenuBtnTrigger, true);

  // 3. 外框动态时间戳与无障碍提示汉化（严格跳过对话正文、代码与终端）
  const RE_UPDATED_AT = /^Updated\s+(.+)$/;
  const RE_TODAY_TIME = /\(Today\s+([^)]+)\)/g;
  const RE_YESTERDAY_TIME = /\(Yesterday\s+([^)]+)\)/g;
  const RE_TRAJECTORY_ID = /^Trajectory ID:\s*(.+)$/;
  const SKIP_CHROME_SELECTOR =
    '[data-testid="autoscroll-viewport"], [data-markdown-root], [data-testid="user-message-content"], .monaco-editor, .xterm, code, pre, textarea, input, [contenteditable="true"]';

  function localizeDynamicChromeStrings() {
    try {
      const dict = (ctx && ctx.dict) || window.__ag_i18n_dict || {};
      const containers = document.querySelectorAll(
        'header, aside, .bg-sidebar, [role="tablist"], [aria-label="Artifact Viewer"], [aria-label="产物预览器"], footer'
      );
      for (let i = 0; i < containers.length; i++) {
        const walker = document.createTreeWalker(containers[i], NodeFilter.SHOW_TEXT);
        let tn;
        while ((tn = walker.nextNode())) {
          const parent = tn.parentElement;
          if (parent && parent.closest && parent.closest(SKIP_CHROME_SELECTOR)) continue;
          const raw = tn.nodeValue;
          if (!raw || raw.length > 90) continue;
          const s = raw.trim();
          if (!s) continue;
          let next = null;
          if (dict[s]) {
            next = raw.replace(s, dict[s]);
          } else if (RE_UPDATED_AT.test(s)) {
            next = raw.replace(RE_UPDATED_AT, '更新于 $1');
          } else if (s.includes('(Today ')) {
            next = raw.replace(RE_TODAY_TIME, '（今天 $1）');
          } else if (s.includes('(Yesterday ')) {
            next = raw.replace(RE_YESTERDAY_TIME, '（昨天 $1）');
          } else if (RE_TRAJECTORY_ID.test(s)) {
            next = raw.replace(RE_TRAJECTORY_ID, '轨迹 ID：$1');
          }
          if (next && next !== raw) {
            tn.nodeValue = next;
          }
        }
      }

      const attrEls = document.querySelectorAll('button[aria-label], button[title], input[placeholder]');
      for (let j = 0; j < attrEls.length; j++) {
        const el = attrEls[j];
        if (el.closest && el.closest(SKIP_CHROME_SELECTOR)) continue;
        for (const attr of ['placeholder', 'title', 'aria-label']) {
          const val = el.getAttribute(attr);
          if (!val) continue;
          const trimmed = val.trim();
          if (dict[trimmed]) {
            el.setAttribute(attr, dict[trimmed]);
          } else if (trimmed.startsWith('Select model, current: ')) {
            el.setAttribute(attr, '选择模型（当前：' + trimmed.slice(23) + '）');
          } else if (trimmed.startsWith('Close ')) {
            el.setAttribute(attr, '关闭 ' + trimmed.slice(6).replace(RE_TODAY_TIME, '（今天 $1）'));
          }
        }
      }
    } catch (e) {}
  }

  const initTimer = setTimeout(localizeDynamicChromeStrings, 400);
  const chromeTimer = setInterval(() => {
    if (document.hidden) return;
    const s = document.getElementById('ag-custom-fonts');
    if (s && s.getAttribute('media') !== 'not all') {
      s.setAttribute('media', 'not all');
    }
    if (typeof window.requestIdleCallback === 'function') {
      window.requestIdleCallback(localizeDynamicChromeStrings, { timeout: 1500 });
    } else {
      localizeDynamicChromeStrings();
    }
  }, 2500);

  if (ctx && typeof ctx.onCleanup === 'function') {
    ctx.onCleanup(() => {
      clearTimeout(initTimer);
      clearInterval(chromeTimer);
      if (mapRestoreTimer) clearTimeout(mapRestoreTimer);
      Array.prototype.map = origArrayMap;
      window.removeEventListener('contextmenu', onContextMenu, true);
      window.removeEventListener('pointerdown', onMenuBtnTrigger, true);
      const s = document.getElementById('ag-custom-fonts');
      if (s) s.removeAttribute('media');
    });
  }
})(typeof ctx !== 'undefined' ? ctx : window.__AG_PATCH_CTX__);
