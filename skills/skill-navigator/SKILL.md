---
name: skill-navigator
description: >
  全局技能与插件调度中枢（Skill & Plugin Workflow Architect）。在你开始任何开发、设计、自动化、数据或业务任务前，
  分析任务目标并为你推荐最适合的本地技能组合配方（Skill Recipe）、插件搭配与阶段执行顺序。
  触发词："用什么技能", "推荐技能", "技能搭配", "工作流规划", "任务前问一下", "怎么组合技能", "技能导航", "/skill-navigator", "/nav".
---

# 全局技能与插件导航器 (Skill Navigator)

你手头拥有 **92+ 个深度定制的本地 Agent Skills** 与 **20 个官方生态插件**。
当面对一个具体任务时，往往不需要单打独斗，而是将多个技能以“流水线”形式组合成黄金配方（Skill Recipe）。

每当用户询问“这个任务该怎么做”、“用什么技能”、“推荐技能组合”时，按以下框架为用户拆解并推荐：

---

## 核心路由流程：五步任务导航法

### 步骤 1：明确任务画像 (Task Profiling)
分析任务的交付形态与特征：
1. **轻量一次性任务**（如写个单脚本、修个小 Bug、转个文件）：短链路直达。
2. **中型完整功能**（如做一个管理后台、写个微信小程序、搞个自动化视频）：标准 3~4 步流水线。
3. **高复杂度/迷雾大工程**（如全新业务系统、架构重构、多人协作规划）：先做决策地图与防腐规格。

### 步骤 2：输出阶段化技能与插件配方 (Skill & Plugin Recipe)
针对任务生命周期的各个阶段，列出最匹配的技能：

```text
[阶段 1: 需求澄清/设计]  --> 推荐技能 A + 对应插件
[阶段 2: 核心研发/编码]  --> 推荐技能 B + 对应插件
[阶段 3: 审查/测试防线]  --> 推荐技能 C
[阶段 4: 平台部署/交付]  --> 推荐技能 D
```

### 步骤 3：说明每个技能的具体职责与执行顺序
明确告诉用户：
- 为什么选这几个技能？
- 第一步先跑哪个，产物如何流转给下一步？
- 是否需要切换上下文（Context Hygiene）或启动 Subagent？

---

## 常用高频场景“黄金配方”速查库

### 配方 1：企业级现代化全栈后台系统 (SaaS / Dashboard)
- **阶段 1（需求与规格）**：`spec-kit`（或 `/to-spec`）先定好需求规格与数据模型边界。
- **阶段 2（前端与架构）**：
  - 若为 React + Tailwind 技术栈：调用 `shadcn-admin` 搭建现代高颜值后台；
  - 若为 Java 后端微服务 + 前端：调用 `ruoyi-shadcn-fullstack` 或 `yudao-vben-admin-builder`；
  - 若需极速前后端联动 Web 工作台：调用 `data-code-expert`（Vue3+FastAPI+Turso+Cloudflare R2）。
- **阶段 3（代码质量）**：执行 `tdd`（测试先行）+ `coderabbit`（PR 质量检查）。
- **阶段 4（云端交付）**：调用 `deploy-to-vercel` 自动检测凭证并完成上线发布。

### 配方 2：3C 二手数码回收与数据处理
- **阶段 1（参数收集）**：调用 `laptop-specs-collector` 联网提取中关村在线/京东核心参数，清洗为四维顿号格式。
- **阶段 2（清洗与导出）**：调用 `data-code-expert` 生成 Polars/FastExcel 极速脚本或 CustomTkinter 桌面工具。
- **阶段 3（报表流转）**：配合 `xlsx` 技能生成格式化 Excel，或通过 `gsheets` 插件写入 Google Sheets 协同表格。

### 配方 3：AI 自媒体与自动化短视频流水线
- **阶段 1（题材检索与文案策划）**：调用 `anysearch` 或 `tavily-search-pro` 检索时事热点与权威一手信源。
- **阶段 2（视频生成）**：调用 `moneyprinterturbo-video`，全自动完成文案脚本打磨、Edge TTS 拟真配音、Pexels 素材匹配与时间轴字幕对齐。
- **阶段 3（资产归档）**：使用 `gdrive` 插件将生成的 MP4 短视频归档到云盘或使用 `notion` 插件记录内容发布日历。

### 配方 4：桌面应用自动化与 RPA 控制 (Computer Use)
- **阶段 1（应用分析与元素嗅探）**：调用 `agent-desktop` + `agent-desktop-windows`，通过 UI Automation 读取窗口语义树（绝非盲点像素）。
- **阶段 2（混合交互）**：
  - 遇到桌面端软件（如微信、VS Code、Slack、本地客户端）：使用 `agent-desktop` 执行表单输入、按钮点击与弹窗处理；
  - 遇到浏览器内密集网页内容：串联 `agent-browser` 接管 CDP 端口交互。

### 配方 5：企业级语义推理、RAG 与 Text-to-SQL
- **阶段 1（本体建模）**：调用 `nvidia-ontology-management` 建立受控业务词汇与实体关联，杜绝 LLM 盲猜表结构。
- **阶段 2（服务部署）**：调用 `nvidia-ontology-setup` 启动 Auto Ontology 服务或接入 MCP。
- **阶段 3（查询校验）**：调用 `nvidia-ontology-query` 校验生成的 SQL 约束与度量，保证查询 100% 可解释与可验证。

### 配方 6：大型复杂需求或“大迷雾”项目攻坚
- **阶段 1（解雾与决策地图）**：调用 `/wayfinder`，在 Issue 追踪器上建立决策地图，逐个击破未决问题。
- **阶段 2（深度质询）**：调用 `/grill-with-docs` 展开苏格拉底式提问，在 `GLOSSARY.md` 和 ADR 中固化技术选型。
- **阶段 3（拆解与调度）**：`/to-spec` 固化规格 → `/to-tickets` 拆分为独立任务卡片 → `/implement-spec` 调度 Subagent 并发执行。
- **阶段 4（复盘提升）**：调用 `/retro` 提炼会话中的教训，反哺环境规则。

### 配方 7：偶发恶性 Bug 排查与故障修复
- **阶段 1（定位与建反馈环）**：调用 `diagnosing-bugs` 或 `systematic-debugging`，绝不盲目改代码，先用一条必现命令锁定最小可复现用例。
- **阶段 2（测试先行加固）**：使用 `test-driven-development` 编写回归测试（Red 变 Green）。
- **阶段 3（代码复审）**：调用 `receiving-code-review` 或 `code-review` 双轴比对（标准轴 + 规格轴）。

---

## 插件协同指南 (Plugin Synergy)

当任务涉及外部服务时，优先结合本地已授权的 20 个插件：
- **涉及文档编写/交接**：优先使用 `gdocs` / `notion`
- **涉及团队协作与日程**：优先使用 `gcalendar`
- **涉及设计稿还原**：优先使用 `figma`（搭配 `figma-code-connect` 技能）
- **涉及品牌视觉物料**：优先使用 `canva`
- **涉及网页抓取与前端分析**：优先使用 `chrome-devtools-plugin`
- **涉及云端发布与域名**：优先使用 `vercel-plugin`
- **涉及商业合同与签约**：优先使用 `pandadoc`
