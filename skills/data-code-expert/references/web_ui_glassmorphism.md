# Web 前端视觉与微交互规范：获奖级玻璃拟态与先锋排版系统

**品质标杆**：以 **Awwwards、The Webby Awards、The FWA 获奖级网站**为审美与交互标准，将企业级数据工作台的“严密生产力”与先锋数字产品的“呼吸感、秩序感、微交互高级感”融为一体。

**适用范围**：现代化 Web 工作台模式（含 Vercel + Turso 云端双模）及所有浏览器前端页面。默认启用，仅当用户明确要求“朴素默认样式”时跳过。

---

## 一、三套高定主题矩阵（纯 CSS 变量驱动，零运行时开销）

直接将本技能的 `assets/glass-theme.css` 复制到前端项目 `src/styles/glass.css`，並在 `main.ts` **最后一行**引入：

```typescript
import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css";
import "./styles/glass.css"; // 必须放最后，彻底穿透覆盖 Element Plus 默认白底
```

内置三套一键切换主题（通过 `<html>` 的 class 与 `data-glass-theme` 驱动）+ 一键性能降级开关（`html.no-glass`）：

| 主题代号 | 视觉气质与适用场景 | 背景与材质构造 | 字体对比度规范 |
|---|---|---|---|
| **🌌 星云毛玻璃**<br>`nebula` (`html.dark`，默认) | 深邃科技、高密度数据审核台、夜间长时间办公不刺眼 | 宇宙蓝紫基底 `#080B18` → `#0D1226` + 青蓝/电光紫/暖玫红三色星云弥散光晕；面板 `rgba(17, 23, 46, 0.74)` + `1px` 顶部镜面内高光 | 主标题/核心数字纯亮冰白 `#F8FAFC`（字重 `600~800`），次级正文 `#CBD5E1`，辅助 `#94A3B8` |
| **🌸 霞光毛玻璃**<br>`aurora` (`:root` 浅色) | 温润通透、财务报表、日常团队协同、明亮现代 SaaS | 暖粉珊瑚至电光紫蓝多重径向流光渐变 + 柔光暖白磨砂卡片 `rgba(255, 248, 252, 0.82)` | 主文字深邃石板蓝黑 `#0F172A`，次级正文 `#334155`，辅助 `#64748B` |
| **🏛️ 先锋杂志风**<br>`editorial` (`html.editorial`) | Awwwards 实验性先锋风、Bento 看板、数据故事展示 | 暖米白宣纸底 `#F7F6F2` + 暴露式 `1px` 瑞士建筑网格线 `#18181B1F` + 零模糊高锐度卡片 + 曜石黑高对比色块 | 标题字距紧缩 `-0.03em`、极高黑白对比度（`#09090B`），强调结构感与留白 |

---

## 二、布局与微交互组件范式（App.vue + 聚光灯 Bento 卡片）

### 1. 主题与 URL Hash 状态双写持久化 (`src/composables/useTheme.ts`)

```typescript
import { ref, watchEffect } from "vue";

export type ThemeMode = "nebula" | "aurora" | "editorial";

const theme = ref<ThemeMode>((localStorage.getItem("shub_glass_theme") as ThemeMode) || "nebula");
const glass = ref<boolean>(localStorage.getItem("shub_glass_enabled") !== "off");
const activeTab = ref<string>(
  window.location.hash.replace("#/", "").split("?")[0] ||
  localStorage.getItem("shub_active_tab") ||
  "dashboard"
);

watchEffect(() => {
  const el = document.documentElement;
  el.setAttribute("data-glass-theme", theme.value);
  el.classList.toggle("dark", theme.value === "nebula");
  el.classList.toggle("editorial", theme.value === "editorial");
  el.classList.toggle("no-glass", !glass.value || theme.value === "editorial");
  localStorage.setItem("shub_glass_theme", theme.value);
  localStorage.setItem("shub_glass_enabled", glass.value ? "on" : "off");
});

watchEffect(() => {
  localStorage.setItem("shub_active_tab", activeTab.value);
  if (window.location.hash !== `#/${activeTab.value}`) {
    window.history.replaceState(null, "", `#/${activeTab.value}`);
  }
});

export const useTheme = () => ({ theme, glass, activeTab });
```

### 2. 鼠标跟随聚光灯微交互卡片（Spotlight Glass Card）

在顶部 Bento 指标卡或功能入口卡片上绑定轻量鼠标坐标变量，配合 `glass.css` 中的 `.glass-spotlight` 类即可实现 Awwwards 获奖站标志性的**边缘流光追踪效果**：

```vue
<template>
  <div
    class="glass glass-spotlight bento-card"
    @mousemove="onSpotMove"
  >
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value num-tabular">{{ formattedValue }}</div>
    <span class="gem-pill pill-emerald">{{ badge }}</span>
  </div>
</template>

<script setup lang="ts">
function onSpotMove(e: MouseEvent) {
  const el = e.currentTarget as HTMLElement;
  const rect = el.getBoundingClientRect();
  el.style.setProperty("--spot-x", `${e.clientX - rect.left}px`);
  el.style.setProperty("--spot-y", `${e.clientY - rect.top}px`);
}
</script>
```

---

## 三、八条视觉与工程设计铁律（不可协商）

1. **严禁“深色毛玻璃夹杂刺眼白块”**：所有 Element Plus 内部组件（`.el-table`、`.el-input__wrapper`、`.el-select__wrapper`、`.el-textarea__inner`、`.el-dialog`、`.el-drawer`、`.el-popper`、`.el-empty`、`.el-pagination`）背景色、边框色与文字色必须 100% 绑定至当前主题令牌，在星云深色模式下**全页面零白块**。
2. **玻璃滤镜只加在“外层容器层”**：仅侧栏、顶栏、Bento 卡片、弹窗、表格外层容器（`.glass-strong`）启用 `backdrop-filter`，表格 `<tr>/<td>`、输入框内部、按钮严禁叠加模糊滤镜，且**严禁嵌套模糊**。
3. **数字列强制等宽排版（`.num-tabular`）**：所有金额、库存、百分比、行数、时间戳列必须应用 `font-variant-numeric: tabular-nums` 与 `'JetBrains Mono'` 等宽字体栈，确保上下行小数点与千分位严丝合缝对齐。
4. **Bento 便当盒非对称网格取代“满屏死板大表”**：工作台首屏必须采用 `.bento-grid` 组合呈现「核心 KPI 缓动数字卡 + 迷你趋势微图表 / 状态分布胶囊 + 快捷过滤命令栏」，下方再承载 `.glass-strong` 主数据表。
5. **高饱和电光胶囊与半透宝石徽标**：主激活态采用电光紫蓝渐变 `linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)` 配弥散光晕；分类计数与状态标签采用 5 色半透宝石胶囊（`pill-emerald`、`pill-sky`、`pill-gold`、`pill-violet`、`pill-coral`）。
6. **成对前缀 + 无障碍与旧浏览器降级**：`-webkit-backdrop-filter` 与 `backdrop-filter` 成对出现；内置 `@supports not`、`prefers-reduced-transparency`、`prefers-reduced-motion` 及 `html.no-glass` 手动降级开关。
7. **微交互克制流畅，严禁持续高耗能背景动画**：背景星云光晕保持静态固定（省 GPU）；动效集中在用户操作反馈（`v-auto-animate` 列表过渡、`0.2s cubic-bezier(0.22, 1, 0.36, 1)` 悬浮微抬升、鼠标聚光灯边框、KPI 首次加载数字递增）。
8. **美观服务于业务**：绝不因为追求视觉效果删减业务字段、破坏导出格式或阻断键盘可访问性。

---

## 四、性能预算（60fps 铁律）

| 指标维度 | 预算上限 | 工程保障措施 |
|---|---|---|
| 同屏 `backdrop-filter` 容器数 | ≤ 6 个 | 侧栏 + 顶栏 + 3~4 个 Bento 卡片/表格外层容器；卡片内部子元素不再加模糊 |
| 模糊半径 `--glass-blur` | `16px ~ 22px` | 兼顾磨砂通透度与核显/远程桌面帧率 |
| 单页直接渲染表格行数 | ≤ 200 行 | 超过 200 行必须开启分页或使用 `el-table-v2` 虚拟滚动，且大表禁用 `v-auto-animate` |
| 性能逃生口 | 顶栏必配 | 顶栏提供「主题切换（星云/霞光/杂志）」与「毛玻璃开关（`no-glass`）」 |

---

## 五、翻车点对照表（供 `risk_premortem.md` 直接引用）

| 翻车场景 | 代码级应对方案 | 验证方式 |
|---|---|---|
| 深色模式下表头、斑马纹、输入框或下拉弹窗漏出刺眼纯白方块 | `glass.css` 放在 `main.ts` 最后引入；全面覆盖 `--el-fill-color-blank`、`--el-bg-color-overlay` 与 `.el-table / .el-popper` | 切换到「🌌 星云毛玻璃」，逐一打开弹窗、下拉框、空状态、分页器检查零白块 |
| 切换浏览器标签页或按 F5 刷新后跳回首页、筛选条件丢失 | `useTheme.ts` 将 `activeTab`、筛选条件、主题偏好同步写入 `localStorage` 与 `window.location.hash` | 在子页面筛选数据后按 F5 刷新，确认停留在原页面且筛选保持 |
| 大表滚动掉帧、远程桌面/老旧工位电脑卡顿 | 模糊仅限外层容器；单页 ≤200 行；顶栏提供 `no-glass` 开关并持久化 | 开启 Chrome Performance 面板滚动 200 行表格，验证帧率稳定 |
| `backdrop-filter` 容器导致内部自定义 `position: fixed` 弹窗定位偏移 | `el-dialog` / `el-drawer` / `el-select` 保持 `append-to-body` | 在带毛玻璃侧栏页面打开弹窗与下拉菜单，检查居中与对齐 |

---

## 六、🏆 Awwwards / Webby / FWA 获奖级「七维自检与持续优化闭环」（交付前强制执行）

在完成前端代码编写后、正式向用户交付前，必须以获奖级评委视角从以下 **7 个维度**逐项自检；若发现任何一维存在短板，立即在代码中打磨优化，直到没有明显可提升之处，并在交付说明末尾输出这份自检报告：

1. **排版（Typography）**：
   - [ ] 标题（`600~800` 字重，紧字距 `-0.02em`）、正文、辅助说明层级分明；所有金额、行数、百分比、编号 100% 启用 `.num-tabular`（`tabular-nums` + `JetBrains Mono`）对齐。
2. **留白与构图（Whitespace & Bento Grid）**：
   - [ ] 采用 `.bento-grid` 非对称便当盒卡片布局，页面外边距 `20px~28px`、卡片间距 `16px~20px`、内边距 `20px~24px`，呼吸感充沛，无拥挤贴边或死板满屏表格。
3. **视觉层级与色彩（Visual Hierarchy & Color）**：
   - [ ] 星云深色 / 霞光浅色 / 先锋杂志三套主题色彩和谐，正文对比度 ≥ 4.5:1、核心 KPI 数字对比度 ≥ 7:1；Element Plus 全组件穿透彻底，暗色模式下**零纯白残留块**。
4. **动效（Choreographed Motion）**：
   - [ ] 列表筛选/增删改接入 `v-auto-animate` 丝滑过渡（或平滑 CSS `cubic-bezier(0.22, 1, 0.36, 1)` 过渡），KPI 核心指标具备平滑数字递增动效，且遵循 `prefers-reduced-motion` 无障碍规范。
5. **微交互（Micro-interactions）**：
   - [ ] 卡片具备 `.glass-spotlight` 鼠标跟随流光边框与悬浮微抬升；主按钮具备弥散光晕反馈；耗时请求具备防抖 loading / 骨架屏提示；支持快捷键（如 `⌘K` / `Esc`）直达核心操作。
6. **响应式（Responsive & Adaptive）**：
   - [ ] 标题字号采用 `clamp()` 流体缩放；`< 1024px` 平板与移动端下 Bento 网格自动折行、侧边导航平滑收起；宽表格支持首尾列固定与自定义细滚动条横向滑动。
7. **原创性（Originality & Domain Craft）**：
   - [ ] 跳出千篇一律的后台模板：结合具体业务领域设计了专属的顶部 Bento 状态总览卡、半透宝石色胶囊标签、可视化的差异对比高亮或拖拽交互细节。

---

## 七、桌面 GUI 的限制说明

CustomTkinter / Tkinter 没有原生背景高斯模糊能力，**无法实现真正的 CSS 毛玻璃**。若用户在桌面工具模式要求毛玻璃：
1. 如实说明限制，采用深邃星云蓝紫配色（`#0B0F19` 基底 + `#161F33` 卡片 + `#6366F1` 电光紫高亮按钮 + `corner_radius=14`）模拟同款视觉层级；
2. 若用户坚持要真毛玻璃与获奖级网页动效，引导切换至**现代化 Web 工作台模式**。
