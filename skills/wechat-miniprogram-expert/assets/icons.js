// assets/icons.js
// 统一风格的极简轻量级矢量 SVG 图标库（Base64 / Data URI，无外部字体或 Emoji 依赖）

const svgToDataUri = (svg) => {
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
};

const COLOR_PRIMARY = '#0284c7'; // cyan-600
const COLOR_SLATE = '#64748b';   // slate-500
const COLOR_MUTED = '#94a3b8';   // slate-400

const icons = {
  // 日历
  calendar: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="3" ry="3"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
  `),

  // 时钟
  clock: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12 6 12 12 16 14"></polyline>
    </svg>
  `),

  // 地点
  location: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
      <circle cx="12" cy="10" r="3"></circle>
    </svg>
  `),

  // 人群/用户
  user: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
  `),

  // 群组
  users: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-3-3.87"></path>
      <path d="M9 21v-2a4 4 0 0 1 3-3.87"></path>
      <circle cx="9" cy="7" r="4"></circle>
    </svg>
  `),

  // 手机
  phone: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="5" y="2" width="14" height="20" rx="3" ry="3"></rect>
      <line x1="12" y1="18" x2="12.01" y2="18"></line>
    </svg>
  `),

  // 门票/凭证
  ticket: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M2 9a3 3 0 0 1 0 6v3a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-3a3 3 0 0 1 0-6V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v3z"></path>
      <line x1="9" y1="4" x2="9" y2="20" stroke-dasharray="2 2"></line>
    </svg>
  `),

  // 勾选成功
  checkCircle: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
  `),

  // 盾牌安全
  shieldCheck: svgToDataUri(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${COLOR_PRIMARY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
      <polyline points="9 12 11 14 15 10"></polyline>
    </svg>
  `)
};

module.exports = icons;
