# 现代化 Web 工作台模式（生产级五层架构 + 获奖级视觉与微交互插件体系）

用于真正需要**浏览器访问、局域网/多人协同、或 Vercel + GitHub + Turso 云端零成本上线**的场景。单脚本临时局域网封装优先用 `local-to-flask-web` 技能；本模式专用于生产级、高颜值、可长期维护的现代 Web 工作台。

---

## 开场提问：输出「结构化点选确认卡」（必须执行）

```markdown
构建现代 Web 工作台前，请确认以下关键维度（带 `●` 为根据你需求预设的推荐默认项，直接回复 **“默认”** 或 **“1A 2B”** 即可）：

**1. 工作台核心定位与业务流**
- `●` **A. 数据清洗 / 多表比对 / 报价审核工作台（推荐默认）**：支持上传 Excel/CSV、自动对齐核验、在线筛选编辑与一键导出报表
- `○` **B. Python 脚本 / 任务调度管理平台**：可视化配置参数、执行脚本、查看日志与下载产物
- `○` **C. 多功能业务管理与看板系统（CRUD + 可视化大屏）**
- `○` **D. 其他自定义定位**（请一句话补充核心业务对象）

**2. 视觉风格与获奖级审美预设（对标 Awwwards / Webby / FWA 标准）**
- `●` **A. 🌌 星云毛玻璃（Nebula Dark，推荐默认）**：深邃蓝紫基底 + 电光紫/青蓝弥散光晕 + 全组件零白块高对比磨砂面板（自带🌸霞光浅色与🏛️先锋杂志风一键切换）
- `○` **B. 🌸 霞光毛玻璃（Aurora Light 默认）**：暖粉珊瑚至电光紫蓝流光浅色底 + 柔光暖白磨砂卡片
- `○` **C. 🏛️ 先锋实验性杂志风（Avant-Garde Editorial 默认）**：大胆非对称 Bento 便当盒构图、1px 瑞士网格线、强烈排版对比
- `○` **D. 极简克制纯色风**：默认关闭背景模糊，极致轻量

**3. 前端高阶微交互插件组合**
- `●` **A. 黄金轻量微交互套件（推荐默认）**：`@formkit/auto-animate`（列表增删筛选丝滑过渡）+ `@vueuse/core`（鼠标聚光灯卡片边框 + `⌘K` 快捷键 + 状态防丢失）+ KPI 数字缓动递增
- `○` **B. 全特效先锋交互套件**：在 A 基础上追加 `Apache ECharts`（透明玻璃微图表与点击联动）+ `GSAP / Lenis`（时间轴错落入场与平滑滚动）+ `vue-draggable-plus`（Excel 表头拖拽映射）
- `○` **C. 零额外前端插件**：仅使用 Vue 3 + Element Plus 原生过渡

**4. 部署形态、数据库与文件存储策略**
- `●` **A. 本地 SQLite WAL + 云端 Vercel & Turso 双模自适应，Excel 走 `BytesIO` 内存流即用即走（推荐默认，保护 5GB 免费库配额）**
- `○` **B. 双模数据库 + 启用 Cloudflare R2（`r2_storage.py`）**：业务上必须长期原样留存用户上传的原始 Excel/图片凭证（享 10GB 免费对象存储）
- `○` **C. 仅本机 / 局域网部署（SQLite WAL）**：不需要生成 Vercel 与云端配置

**5. 账号与权限体系**
- `●` **A. 轻量单身份 / 简易口令保护（推荐默认，内部团队开箱即用）**
- `○` **B. 多角色账号体系（管理员 / 审核员 / 普通成员权限隔离，含零闪烁登录态恢复）**
```

Confirm 业务逻辑后，**先按 `references/risk_premortem.md` 做完整版逆向推演风险评估并输出开发方案（含拍板点选卡）**；若选了云端双模，必须**追加读取 `references/web_cloud_vercel_turso.md`** 并逐条落实九条避坑铁律；生成前端页面前必须**读取 `references/web_ui_glassmorphism.md`** 并复制 `assets/glass-theme.css`。

---

## 五层架构规范（不可协商）

| 层 | 技术选型 | 职责 |
|---|---|---|
| 视图层 | Vue 3（`<script setup>` + Composition API）+ Vite + TypeScript + `assets/glass-theme.css` | 页面布局、三套高定主题切换、`localStorage` + URL Hash 状态防丢失 |
| 交互与组件层 | Element Plus（全组件玻璃变量穿透）+ 按需轻量微交互插件 | 表格、表单、Bento 指标卡、`v-auto-animate`、聚光灯卡片、`⌘K` 命令栏 |
| 接口层 | FastAPI（Python 3.11/3.12+，`lifespan` 异步上下文管理器） | REST API，全局 `@app.exception_handler` 返回清晰中文 JSON 报错 |
| 数据层 | SQLModel（Pydantic + SQLAlchemy 合一） | ORM 模型定义（云端双模下时间字段强制用 `Optional[str]`，严禁存文件 BLOB） |
| 存储层 | 本地 `SQLite WAL`（含 `shm` 探针降级） / 云端 `Turso HTTP /v2/pipeline` + 按需 `Cloudflare R2` | 未配 `TURSO_DATABASE_URL` 走本地 SQLite WAL；配了自动切零编译 Turso 批量事务引擎 |

**核心解耦准则**：业务逻辑（校验、计算、匹配规则）写成不依赖 FastAPI 的纯函数，放在 `services/`，路由层只做参数解析和调用，方便单测。

---

## Vue 3 获奖级高质感交互插件选配矩阵

在保证后端 Serverless 极简（7 个核心 Python 包）的同时，前端可根据业务场景在 `package.json` 中按需组合以下成熟的轻量插件，彻底摆脱“后台管理系统模板感”：

| 插件名称 | 安装命令 | 典型落地位置与交互效果 | 60fps 性能守门红线 |
|---|---|---|---|
| **FormKit AutoAnimate** | `npm i @formkit/auto-animate` | 在 Bento 卡片网格、筛选标签栏、`<200` 行的列表容器上加 `v-auto-animate`，增删改与过滤自动产生丝滑位移过渡 | 单页 `>200` 行的大表严禁对 `<tbody>` 开启，改用分页或虚拟滚动 |
| **VueUse 组合式工具集** | `npm i @vueuse/core @vueuse/motion` | `useMouseInElement` 驱动 `.glass-spotlight` 卡片鼠标跟随流光边框；`useMagicKeys` 绑定 `⌘K / Ctrl+K` 唤起全局命令面板；`useStorage` 同步页面状态 | 聚光灯坐标通过 CSS 变量 `--spot-x / --spot-y` 更新，不触发 Vue 组件重渲染 |
| **GSAP + Lenis** | `npm i gsap lenis` | 首屏 Bento KPI 卡片按 `stagger: 0.06` 错落浮现，核心金额数字从 0 缓动滚动到目标值；门户/看板页惯性平滑滚动 | `.el-table__body-wrapper` 与弹窗滚动区必须加 `data-lenis-prevent`，防止劫持表格内部滚轮 |
| **Apache ECharts 6 + Vue ECharts** | `npm i echarts vue-echarts` | 顶部 Bento 卡片内嵌透明底色渐变微图表（Sparkline）与分布图；点击图表柱条/扇区直接联动过滤下方 `<el-table>` | 必须设置 `backgroundColor: 'transparent'`，文字与网格线颜色跟随主题变量 |
| **VueDraggablePlus** | `npm i vue-draggable-plus` | Excel 导入时的“源表头 ➔ 标准表头”拖拽映射对齐、多规则优先级拖拽排序 | 仅在含字段映射或看板拖拽需求时引入 |

---

## 前端交互防呆与状态持久化铁律（杜绝切页刷新回跳主界面）

1. **双写持久化（`localStorage` + `window.location.hash`）**：
   - `activeTab`（当前菜单页）、`selectedId`、搜索过滤条件、`glassTheme`（`nebula` / `aurora` / `editorial`）实时同步至 `localStorage` 与 URL Hash；
   - 切换浏览器标签页、最小化窗口或按 F5 刷新时，100% 恢复到离开前的子页面与选中状态，**绝不重置回首页**。
2. **零闪烁登录态恢复**：
   - 初始化时同步从 `localStorage` 读取用户快照立即渲染主工作台，后台静默请求 `/api/auth/me` 校验；仅当明确返回 `401` 时才清除缓存退回登录页。
3. **全量数据与筛选视图隔离**：
   - 全量列表（如 `allItems`）与局部搜索计算属性 `filteredItems` 严格分离，避免在列表页搜索后污染其他页面的下拉选项。

---

## Mono-Repo 目录结构

> 注：纯局域网项目可用 `server/` + `web/` 或 `backend/` + `frontend/`；若需支持 Vercel + Turso 云端双模，统一使用 `backend/` + `frontend/` 以对齐 `vercel.json`（详见 `references/web_cloud_vercel_turso.md`）。

```
项目根/
├── backend/                      # FastAPI 后端（局域网项目亦可用 server/app/）
│   ├── main.py                   # FastAPI 入口：lifespan 幂等自检、CORS、全局 JSON 异常拦截
│   ├── models.py                 # SQLModel 表模型（时间字段用 Optional[str]，禁存文件 BLOB）
│   ├── database.py               # 本地 SQLite WAL（含探针降级）+ 云端 Turso 双模引擎
│   ├── r2_storage.py             # [按需生成] 仅在需永久归档原始文件时生成（零依赖 Cloudflare R2）
│   ├── routers/                  # 路由层
│   ├── services/                 # 纯业务逻辑函数，不 import FastAPI
│   └── requirements.txt
├── frontend/                     # Vue 3 + Vite + TS 前端
│   ├── src/
│   │   ├── main.ts               # 引入 Element Plus、dark/css-vars.css、最后引入 styles/glass.css
│   │   ├── App.vue               # Bento 玻璃工作台骨架 + 主题切换 + 状态双写持久化
│   │   ├── styles/glass.css      # 直接复制自本技能 assets/glass-theme.css
│   │   ├── composables/useTheme.ts # 星云/霞光/杂志风三主题 + no-glass 降级 + URL Hash 同步
│   │   ├── api/                  # axios 封装，统一 baseURL: '/api' 与错误拦截
│   │   ├── views/                # 页面级组件
│   │   └── components/           # 复用组件（如聚光灯 Bento 卡片、命令面板）
│   ├── vite.config.ts            # 本地开发配置 /api 代理到 http://127.0.0.1:8000
│   └── package.json              # "build": "vite build"
├── vercel.json                   # [上云必配] Vercel 全栈路由与函数超时配置
└── README.md
```

---

## 核心代码骨架（本地标准版；上云双模版见 `web_cloud_vercel_turso.md`）

### `backend/main.py` — 使用现代 `lifespan` 上下文管理器 + 全局 JSON 异常拦截

> **修复说明**：彻底摒弃已弃用的 `@app.on_event("startup")`，统一采用 FastAPI 官方推荐的 `@asynccontextmanager async def lifespan(app: FastAPI):`，并内置全局异常拦截器返回清晰中文 JSON。

```python
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import ensure_db_ready
from routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_db_ready()
    yield


app = FastAPI(title="现代化数据工作台", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 局域网工具可放开；公网生产可按需收紧
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"服务器处理异常：{exc}",
            "message": str(exc),
            "path": request.url.path,
        },
    )


app.include_router(items.router)
```

---

## 输出格式与交付闭环

**① 依赖清单** — 后端 `requirements.txt` + 前端 `package.json`（含选定的轻量交互插件）
**② 需求确认与逆向推演防翻车落地总结** — 含 `R1~Rn` 在各层的具体落点
**③ 完整工程文件** — 按 `backend/database.py → (按需 r2_storage.py) → models.py → services/ → routers/ → main.py → frontend/vite.config.ts → frontend/src/styles/glass.css → frontend/src/composables/useTheme.ts → frontend/src/App.vue → frontend/src/views/ → (按需 vercel.json)` 顺序给出
**④ Awwwards 七维视觉与交互自检清单** — 对照 `references/web_ui_glassmorphism.md` 第六节，逐项输出排版、留白、视觉层级色彩、动效、微交互、响应式和原创性的自检优化结果
**⑤ 本地启动与云端上线交付（黄金搭档）** — 本地前后端启动说明；若选了云端双模，自动联动 `deploy-to-vercel` 技能执行环境状态探测、团队 Scope 绑定、触发 Preview/Prod 构建并回传可即刻访问的 Vercel 线上网址，完成从开发到上线的全流程闭环。
