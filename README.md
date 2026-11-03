# 个人用技能库集合 (myskill-project)

> **个人专属 Agent 技能库备份与跨设备同步中心**  
> 本项目集中归档了本地使用的全部 **74 个 Agent Skills**。  
> 无论是日常开发中的自动备份，还是换电脑时的一键恢复，都能确保 Antigravity、Claude Code、Cursor、Codex 等 AI 编程助手拥有完全一致的专家级能力。

- **技能总数**：`74` 个技能
- **最后更新时间**：`2026-11-03 14:14:21`
- **代码仓库**：[lifeifei94001/myskill-project](https://github.com/lifeifei94001/myskill-project)

---

## 换电脑快速恢复指南 (Quick Start on New PC)

当你更换了新电脑或在全新的工作区中工作时，只需通过以下任一方式，即可瞬间激活所有 94+ 个专家技能：

### 方式 1：一键运行恢复脚本（最简单，推荐）

首先克隆本仓库到你的电脑：
```bash
git clone https://github.com/lifeifei94001/myskill-project.git
cd myskill-project
```

- **Windows 用户**：直接双击运行 [`restore.bat`](./restore.bat)（或在 PowerShell 中执行 `.\restore.ps1`）。
- **执行效果**：脚本会自动将 `skills/` 下的全部技能以及全局指令规则 [`AGENTS.md`](./AGENTS.md) 完整还原至当前项目的 `.agents/skills` 目录。
- **全局安装选项**：如果希望全局电脑上所有项目都能使用，可在 PowerShell 中加参数执行：
  ```powershell
  .\restore.ps1 -Global
  ```

---

### 方式 2：使用官方 Skills CLI 按需安装单个技能

如果你只想在新电脑上安装其中的某一个特定技能（例如全栈开发工作台）：
```bash
npx skills add lifeifei94001/myskill-project --skill data-code-expert -g -y
```

---

## 日常备份使用方式 (Daily Backup)

日常开发中，只要你新增了技能、调试了现有技能或调整了配置，可以随时一键备份到 GitHub：

1. **方式 1（双击运行）**：直接双击运行仓库目录下的 [`backup.bat`](./backup.bat)；
2. **方式 2（命令行）**：在 PowerShell 中执行 `.\backup.ps1`；
3. **方式 3（对 Agent 说一句）**：在 Antigravity 中直接对我说 **“帮我备份一下技能”**，Agent 会自动同步本地增量、重构目录说明并推送到 GitHub！

---

## 技能全景目录与中文详细作用说明

本仓库包含的所有技能已按功能场景细化归类，以下为每个技能的详细职责与触发说明：

### 🌐 网络、搜索与外部工具 (共 10 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 1 | **专为 AI Agent 优化的无头浏览器自动化 CLI**<br/>`agent-browser` | [agent-browser](./skills/agent-browser) | 轻量极速的浏览器自动化工具。能够为网页生成紧凑的可访问性语义树快照（A11y Tree），通过短引用标签精准定位并点击、输入元素，极大节约 Agent Token。 |
| 2 | **Google Antigravity 中国大陆网络连接加速方案**<br/>`antigravity-china-access` | [antigravity-china-access](./skills/antigravity-china-access) | 针对中国大陆网络环境量身定制。提供进程级精准代理配置与无黑框静默启动，彻底解决 Antigravity 登录异常、模型超时、Agent 频繁断连与 Language Server 拉取失败，无需开启全局代理或 TUN 模式。 |
| 3 | **多引擎实时垂直领域搜索与正文提取器**<br/>`anysearch` | [anysearch](./skills/anysearch) | 支持全网实时检索、学术/科技垂直领域聚合搜索、多任务并行批量搜索以及指定网页的完整结构化正文清洗提取。 |
| 4 | **Maton 外部第三方 SaaS API 网关**<br/>`API Gateway` | [API Gateway](./skills/API Gateway) | 一键连通 50+ 知名外部云服务（如 GitHub、Slack、Notion、Airtable、Linear、Zoom、Stripe 等）。遵循只读先查、统一鉴权与规范化接口调用。 |
| 5 | **Browserbase 云浏览器持久会话与反爬验证码突破**<br/>`Browserbase Persist with captcha` | [Browserbase Persist with captcha](./skills/Browserbase Persist with captcha) | 创建并管理持久化的 Browserbase 云端无头浏览器实例。具备登录态长期保持、验证码（Captcha）自动识别解算、会话录制、长轮询防掉线与全量截图能力。 |
| 6 | **Docker 安全虚拟沙箱环境管理器**<br/>`docker-sandbox` | [docker-sandbox](./skills/docker-sandbox) | 为 Agent 运行未知代码、测试未审计第三方库或进行安全攻防实验提供轻量级 Docker 隔离沙盒容器，支持网络代理调控与环境秒级销毁。 |
| 7 | **GitHub 仓库深度管理助手**<br/>`OpenClaw GitHub Assistant` | [OpenClaw GitHub Assistant](./skills/OpenClaw GitHub Assistant) | 直接在终端中交互管理 GitHub：查询仓库信息、追踪 GitHub Actions CI/CD 流水线状态、新建/关闭 Issue、全局检索代码库与监控活跃动态。 |
| 8 | **Tavily AI 智能专业搜索引擎**<br/>`tavily-search-pro` | [tavily-search-pro](./skills/tavily-search-pro) | 集成 Tavily AI 五大检索模式：实时网页/新闻/金融精准搜索、URL 原文深度提炼、整站结构化爬取（Crawl）、Sitemap 地图发现以及带权威文献引用的深度调研。 |
| 9 | **Git 提交历史协作模式与代码质量分析器**<br/>`Who Is Actor` | [Who Is Actor](./skills/Who Is Actor) | 纯本地只读分析 Git 仓库提交历史：计算提交节奏、代码变更返工率（Churn/Rework）、约定式提交规范遵循度以及单点维护风险（Bus-Factor），脱敏汇总协作模式指标。 |
| 10 | **交互式 Bash 向导脚本生成器**<br/>`wizard` | [wizard](./skills/wizard) | 当需要开通外部云设施、配置复杂密钥环境变量或走网页控制台操作时，自动生成一步一确认的交互式终端向导，带领用户轻松完成仅限人工的操作。 |

### 🤖 Agent 自我进化与管理 (共 15 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 11 | **AI Agent 集体记忆与知识网络**<br/>`agent-overflow` | [agent-overflow](./skills/agent-overflow) | 连接 AI Agent 的共享记忆中枢。在遇到复杂报错时搜索社区其他 Agent 的成功解决记录，并共享本地沉淀的优质解法。 |
| 12 | **幕僚长长周期多 Agent 编排调度器**<br/>`chief-of-staff` | [chief-of-staff](./skills/chief-of-staff) | 在单一长会话中担任“幕僚长”，调度多路并行子 Agent、管理日程计划，持之以恒地追踪推进宏大目标的达成。 |
| 13 | **极速与安全 Agent Skill 包管理器**<br/>`cocoloop` | [cocoloop](./skills/cocoloop) | 专用于安装、管理、更新和卸载各类 Agent Skills。支持通过 URL、名称、GitHub 极速检索与定位技能，并内置 BSS 安全认证与风险扫描。 |
| 14 | **Superpowers 会话翻车诊断与复盘工具**<br/>`diagnosing-superpowers` | [diagnosing-superpowers](./skills/diagnosing-superpowers) | 当一次 Agent 研发会话不顺（如重复做无用功、偏离计划、耗时过长、效果不佳）时，专项诊断问题根源并生成排障分析报告。 |
| 15 | **并行子 Agent 独立任务派发器**<br/>`dispatching-parallel-agents` | [dispatching-parallel-agents](./skills/dispatching-parallel-agents) | 当面对 2 个及以上没有相互依赖、无需共享状态的独立任务时，自动将其拆解并并行派发给不同的子 Agent 极速执行。 |
| 16 | **技能生态智能发现与推荐器**<br/>`find-skills` | [find-skills](./skills/find-skills) | 已全面升级：第一优先级检索本地 `VoltAgent/awesome-agent-skills`（1497+精选技能），未命中时回退到 Skills CLI 生态，提供一键安装指令。 |
| 17 | **会话紧凑快照交接工具**<br/>`handoff` | [handoff](./skills/handoff) | 在上下文窗口即将满额时，将当前会话成果压缩成高密度的交接摘要，方便新会话加载。 |
| 18 | **编程会话复盘与环境优化建议**<br/>`retro` | [retro](./skills/retro) | 在完成一次完整开发后执行会话复盘，分析环境配置、提示词和技能链路中的阻碍，针对性优化未来运行效率。 |
| 19 | **Agent 经验学习与持续进化系统**<br/>`self-improvement` | [self-improvement](./skills/self-improvement) | 在遇到意外失败、用户纠偏（如“不，你错了…”）、外部工具更新或发现更优解法时，自动提炼经验教训并持久化，实现越用越聪明。 |
| 20 | **Agent Skill 专家级创建与优化工具**<br/>`skill-creator` | [skill-creator](./skills/skill-creator) | 用于创建新技能、规范 SKILL.md 编写格式、调优 Frontmatter 触发词与描述，确保技能在用户提出相关问题时能被模型 100% 精准唤醒。 |
| 21 | **子 Agent 驱动计划执行器**<br/>`subagent-driven-development` | [subagent-driven-development](./skills/subagent-driven-development) | 根据既定实施计划，将每一步骤交由专属子 Agent 隔离执行并验收，主 Agent 负责全局质量把控。 |
| 22 | **Superpowers 实战软件工程方法论框架**<br/>`superpowers` | [superpowers](./skills/superpowers) | 一套经实战检验的 Agent 软件开发工程化方法论，将 TDD、系统化排错、代码审查与思维风暴融为一体。 |
| 23 | **Superpowers 会话初始路由与规范初始化**<br/>`using-superpowers` | [using-superpowers](./skills/using-superpowers) | 在任何复杂会话开始时规范工具检索路径，强制先检索并调用对应技能再回答用户，确保开发流程严密。 |
| 24 | **面向 AI Agent 的提示词与指令工程**<br/>`writing-for-agents` | [writing-for-agents](./skills/writing-for-agents) | 指导编写专供 AI 消费的文档（如 SKILL.md、AGENTS.md、CLAUDE.md、系统级规约），注重上下文密度与指令无二义性。 |
| 25 | **高质量技能文档编写规范 (Writing Skills)**<br/>`writing-skills` | [writing-skills](./skills/writing-skills) | 将 TDD 思想应用于过程文档编写。指导如何编写出经得起子 Agent 执行检验的技能文档与流程控制逻辑。 |

### ✍️ 写作、逆向与综合辅助 (共 10 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 26 | **个人技能智能推荐与路由器**<br/>`ask-matt` | [ask-matt](./skills/ask-matt) | 当你不知道当前难题该用哪个技能解决时，随时向它询问，它会根据你的具体情境智能匹配最佳技能路线。 |
| 27 | **网络迷踪级照片地理与时间多源推断器**<br/>`geo-sleuth` | [geo-sleuth](./skills/geo-sleuth) | 给定一张照片，通过 OCR 文本、反向识图（百度/Yandex）、地区车牌与电话区号库、OpenStreetMap 建筑几何、DEM 高程天际线拟合与太阳阴影夹角，严谨推断出拍照机位与拍摄时刻。 |
| 28 | **高性价比人生决策指南**<br/>`life-decision-guide` | [life-decision-guide](./skills/life-decision-guide) | 基于 GitHub 热门项目《高性价比人生指南》正文，结合金钱/时间/毅力成本与收益证据等级，为日常生活、职场跳槽、维权理财抉择提供高性价比参考。 |
| 29 | **权威一手信源深度研究与调研报告**<br/>`research` | [research](./skills/research) | 针对开发者提出的技术难题，主动深挖权威一手信源（官方文档、源码、RFC 规范），并在本地生成结构化的调研 Markdown 报告。 |
| 30 | **全平台逆向工程通用分析专家 (REA)**<br/>`reverse-engineer-anything` | [reverse-engineer-anything](./skills/reverse-engineer-anything) | 逆向分析 Native 原生二进制、托管代码（.NET/Java）、Electron/JavaScript 打包程序、固件与 Web 应用，基于可信运行时证据指导功能还原与反编译。 |
| 31 | **互动编程题库与教程脚手架构建器**<br/>`scaffold-exercises` | [scaffold-exercises](./skills/scaffold-exercises) | 快速脚手架化生成包含章节、题目、解答方案、原理讲解与 Lint 检查的标准化互动编程学习题库。 |
| 32 | **交互式苏格拉底教学教练**<br/>`teach` | [teach](./skills/teach) | 以任务为导向，通过启发式提问引导开发者动手掌握新技术栈，并在过程中生成学习记录与任务卡片。 |
| 33 | **节拍化叙事编排器 (Writing Beats)**<br/>`writing-beats` | [writing-beats](./skills/writing-beats) | 将复杂材料编织成如同乐谱节拍般的旅程，确保每一个术语在被依赖前都已做好铺垫，读感丝滑自然。 |
| 34 | **发散性写作素材与灵感碎片收集器**<br/>`writing-fragments` | [writing-fragments](./skills/writing-fragments) | 写作探索期专用：不预设条条框框，广泛发掘和记录原始灵感碎片、论点和事实素材，放大思考空间。 |
| 35 | **文章结构与段落骨架塑形器**<br/>`writing-shape` | [writing-shape](./skills/writing-shape) | 写作收敛期专用：将零散的素材碎片按段落塑形为结构紧凑、层层递进的长篇文章框架。 |

### 🧠 需求澄清、推演与架构规划 (共 14 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 36 | **新功能与创意思考风暴 (头脑风暴)**<br/>`brainstorming` | [brainstorming](./skills/brainstorming) | 在开始敲代码或做设计前必须调用的创意思考工具。通过多角度探索、用户故事分析、边界条件拷问，快速将模糊的想法打磨成具备可行性的设计思路。 |
| 37 | **领域模型构建与统一术语表维护**<br/>`domain-modeling` | [domain-modeling](./skills/domain-modeling) | 帮助项目梳理业务领域模型，定义实体、值对象与边界，并在整个生命周期中维护权威的 `GLOSSARY.md`，杜绝术语混乱。 |
| 38 | **实施计划严格执行器**<br/>`executing-plans` | [executing-plans](./skills/executing-plans) | 以写好的实施计划为蓝图在当前会话中由浅入深执行，每完成一步均执行自测并记录验证结果，杜绝计划与执行脱节。 |
| 39 | **方案与思路极限压力测试 (无情盘问)**<br/>`grilling` | [grilling](./skills/grilling) | 扮演严苛的架构审查官，针对用户的想法、技术选型或架构计划进行步步紧逼的无情提问，提前把潜在的翻车点和设计盲区彻底逼问出来。 |
| 40 | **基于规范的任务实现落地器**<br/>`implement` | [implement](./skills/implement) | 根据拍板的规范与任务单，逐步落地具体工程代码，聚焦于高保真还原设计。 |
| 41 | **自动化工作流规格提炼器**<br/>`loop-me` | [loop-me](./skills/loop-me) | 专门针对开发者想要构建的自动化工作流（Workflow）展开定向追问，澄清触发源、输入输出边界、重试策略与异常处理分支。 |
| 42 | **抛弃型快速交互原型构建器**<br/>`prototype` | [prototype](./skills/prototype) | 以最小成本快速构建 throwaway 原型，快速验证核心状态流或前端视觉布局是否顺手，验证完毕后按需吸收或重构。 |
| 43 | **需求澄清问卷生成器**<br/>`to-questionnaire` | [to-questionnaire](./skills/to-questionnaire) | 将复杂的业务疑问整理成结构化、带推荐项的选择型问卷，极大降低用户提供业务细节的认知负担。 |
| 44 | **对话与想法转结构化技术规范 (Spec)**<br/>`to-spec` | [to-spec](./skills/to-spec) | 将当前的头脑风暴、聊天记录或初步讨论提炼为结构化、无二义性、供工程团队直接开发落地的完整技术规范文档。 |
| 45 | **技术规范转示踪弹任务卡 (Tickets)**<br/>`to-tickets` | [to-tickets](./skills/to-tickets) | 将技术规范切分为一组带明确依赖图和前置阻塞关系的示踪弹开发卡片（Tracer-bullet Tickets），可直接发布到 Issue 追踪系统中。 |
| 46 | **Issue 与 PR 分流状态机**<br/>`triage` | [triage](./skills/triage) | 对项目收到的 Issue 和外部贡献 PR 进行状态机式快速分级、真伪复现、缺失信息追问与编写 Agent 易读的任务简报。 |
| 47 | **沟通对齐与简明认知重置**<br/>`wait-what` | [wait-what](./skills/wait-what) | 当 Agent 理解发生偏差或聊得过于发散时，强制暂停并以极简航空工业级自然语言（ASD-STE100）重述背景、意图与当前阶段。 |
| 48 | **大型超长工程宏观导航路线图**<br/>`wayfinder` | [wayfinder](./skills/wayfinder) | 面对超出单个 Agent 会话上下文的超大型项目，将整体目标绘制成决策票据网络图，指引团队按图索骥逐步推进直到通关。 |
| 49 | **多步骤实施实施计划撰写蓝图**<br/>`writing-plans` | [writing-plans](./skills/writing-plans) | 在动手编写代码前，将业务需求转化为详尽的实施计划。假定执行者完全没看过当前代码，将任务拆解为高内聚、带验证步骤、具备独立提交断点的工程序列。 |

### 🛠️ 软件工程与代码质量规范 (共 15 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 50 | **双轴严格代码审查专家**<br/>`code-review` | [code-review](./skills/code-review) | 沿双轴执行并行审查：①编码规范轴（Standards：是否符合本仓库架构与编码风格）；②需求规格轴（Spec：是否 100% 实现了初始 Issue/需求且未引入未定义行为）。使用双子 Agent 并行审查并排版输出。 |
| 51 | **深模块架构设计规范 (Deep Modules)**<br/>`codebase-design` | [codebase-design](./skills/codebase-design) | 指导设计具备“接口极其简单、底层实现极其强大且深厚”的深模块（Deep Modules）。识别浅模块弊端，找到系统解耦与加深缝隙（Seam），让代码更具抗脆弱性、更易单元测试与更易被 AI 理解。 |
| 52 | **特性开发分支完结与交付决策**<br/>`finishing-a-development-branch` | [finishing-a-development-branch](./skills/finishing-a-development-branch) | 当功能代码开发完成且所有测试均通过后，辅助开发者评估如何集成：创建 PR、变基合并、生成变更摘要与清理无用临时工作区。 |
| 53 | **Claude Code / Agent Git 高危操作拦截守门员**<br/>`git-guardrails-claude-code` | [git-guardrails-claude-code](./skills/git-guardrails-claude-code) | 通过 Hook 机制实时拦截 AI 执行危险的破坏性 Git 操作（如 git push --force、git reset --hard、git clean -fd、git branch -D 等），为自动化编程筑牢安全防线。 |
| 54 | **代码库架构摩擦扫描与可视化审查报告**<br/>`improve-codebase-architecture` | [improve-codebase-architecture](./skills/improve-codebase-architecture) | 深度扫描代码库中的架构摩擦点、浅模块与过度耦合问题，自动生成交互式可视化 HTML 架构体检报告，并引导开发者逐个攻克重构方案。 |
| 55 | **Matt Pocock 资深工程师实战工作流全集**<br/>`mattpocock-skills` | [mattpocock-skills](./skills/mattpocock-skills) | 汇聚知名 TypeScript 专家 Matt Pocock 的实战工程师技能库，涵盖 TypeScript 高级类型体操、TDD 测试策略、深模块代码设计与高难度架构重构。 |
| 56 | **测试代码 as 类型断言安全迁移**<br/>`migrate-to-shoehorn` | [migrate-to-shoehorn](./skills/migrate-to-shoehorn) | 将测试文件中脆弱、容易隐藏类型 Bug 的 `as unknown as Type` 强制类型断言，平滑无损地迁移至 `@total-typescript/shoehorn` 库，提升单测类型安全性。 |
| 57 | **高质量 Pull Request 撰写器**<br/>`pr` | [pr](./skills/pr) | 根据 Git 提交记录与改动 Diff，自动生成符合顶级开源项目规范的 PR 描述（包含改动动机、核心架构变更、测试覆盖情况与回滚预案）。 |
| 58 | **代码审查意见严谨处理流程**<br/>`receiving-code-review` | [receiving-code-review](./skills/receiving-code-review) | 接收代码审查反馈时的执行准则：拒绝盲目附和或敷衍修改，坚持从技术严谨性出发，对合理建议写出针对性测试验证，对存疑反馈通过代码事实探讨。 |
| 59 | **代码审查发起前自检流程**<br/>`requesting-code-review` | [requesting-code-review](./skills/requesting-code-review) | 在提交 PR 或合并代码前执行的强制自检，核验所有变更是否符合需求清单、是否有新增测试覆盖、是否缺少错误边界处理。 |
| 60 | **前端 Pre-commit 规范守门员自动化配置**<br/>`setup-pre-commit` | [setup-pre-commit](./skills/setup-pre-commit) | 一键在当前代码库中配置 Husky + lint-staged，整合 Prettier 代码美化、TypeScript 类型自检（tsc）与核心单元测试，确保违规代码绝不会被提交进 Git。 |
| 61 | **系统化疑难 Bug 诊断流程**<br/>`systematic-debugging` | [systematic-debugging](./skills/systematic-debugging) | 针对偶发 Bug、内存泄漏与复杂故障的科学排查法：建立可重现的最小复现用例、二分隔离受污染范围、根因追踪与防御性修复，杜绝“改到能跑为止”的侥幸心态。 |
| 62 | **测试驱动开发执行标准 (TDD)**<br/>`test-driven-development` | [test-driven-development](./skills/test-driven-development) | 严格执行测试驱动开发准则：在编写任何业务实现代码前，必须先写出能够重现失败的单元测试用例（红），再以最简代码使其通过（绿），最后进行重构。 |
| 63 | **Git Worktrees 独立工作区安全隔离流**<br/>`using-git-worktrees` | [using-git-worktrees](./skills/using-git-worktrees) | 在启动多分支并行开发或实施大改动前，自动使用 Git Worktree 检出独立工作区，避免修改正在运行的当前工作目录或污染现有代码现场。 |
| 64 | **交付前证据验证门禁 (Evidence Before Assertions)**<br/>`verification-before-completion` | [verification-before-completion](./skills/verification-before-completion) | 铁律闸门：在声明任务完成、代码修复或全部通过前，必须在终端中实际运行验证命令（测试、构建、Lint），并依据命令的真实输出作为证据，严禁在未见证据前做出主观承诺。 |

### 🌟 全栈开发与 Web 工作台 (共 7 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 65 | **高性能数据处理与获奖级全栈工作台代码专家**<br/>`data-code-expert` | [data-code-expert](./skills/data-code-expert) | 覆盖四种交付形态：①一次性极速数据清洗脚本（Polars+FastExcel+xlsxwriter）；②CustomTkinter 原生桌面小工具（带 WPS/Excel 容错解耦）；③Vue3 + FastAPI + Turso + Cloudflare R2 生产级前后端 Web 工作台（严守《九条云端避坑铁律》与 Awwwards 七维视觉微交互自检）；④开源优先系统调研落地。 |
| 66 | **Vercel 自动化部署与平台交付官**<br/>`deploy-to-vercel` | [deploy-to-vercel](./skills/deploy-to-vercel) | 与 data-code-expert 构成黄金搭档。专职负责项目的云端交付：自动探测 Git 远端与本地凭证、智能绑定团队 Scope、安全触发 Git Push 或 CLI 预览部署，并实时拉取回传线上可直接访问的 Preview / Production 官方链接。 |
| 67 | **二手笔记本回收参数收集与顿号格式化专家**<br/>`laptop-specs-collector` | [laptop-specs-collector](./skills/laptop-specs-collector) | 专为爱回收/转转类 3C 二手回收业务打造。根据笔记本机型名称，自动联网检索中关村在线 (ZOL)、京东及官方参数库，精准提取并清洗为四维顿号格式（发布时间、CPU、显卡、固态、机械硬盘），可直接一键复制到机型排列组合系统。 |
| 68 | **若依后端 + Shadcn Admin 前端全栈脚手架**<br/>`ruoyi-shadcn-fullstack` | [ruoyi-shadcn-fullstack](./skills/ruoyi-shadcn-fullstack) | 将经典的若依 Java 后端企业级标准（Spring Boot、MyBatis-Plus、MySQL、Redis、JWT/RBAC）与现代化 Shadcn Admin 前端标准（Vite、React 19、TypeScript、Tailwind CSS v4、TanStack Router & Table）无缝融合，生成高颜值全栈管理系统。 |
| 69 | **Shadcn Admin 现代化后台管理系统构建专家**<br/>`shadcn-admin` | [shadcn-admin](./skills/shadcn-admin) | 专用于基于 shadcn-admin 模板脚手架搭建企业级仪表盘与管理后台。基于 Vite + React + TypeScript + Tailwind CSS v4 + Shadcn UI + TanStack Router，具备极高质量的暗黑模式、权限路由与响应式布局。 |
| 70 | **微信小程序全栈专家**<br/>`wechat-miniprogram-expert` | [wechat-miniprogram-expert](./skills/wechat-miniprogram-expert) | 覆盖原生微信小程序从 0 到 1 开发。支持微信云开发（CloudBase）与本地 Storage 模拟双模自适应适配、微信 OAuth 登录、并发高危业务原子防超卖事务设计、100% 纯 SVG 矢量 UI（严禁 Emoji）与合规发布交付 SOP。 |
| 71 | **芋道源码 + Vben 5 企业级中后台构建专家**<br/>`yudao-vben-admin-builder` | [yudao-vben-admin-builder](./skills/yudao-vben-admin-builder) | 专注于基于 Yudao（ruoyi-vue-pro / yudao-boot-mini）Java 企业级架构与 Vben 5 / Vue3 Element Plus 前端进行企业 SaaS、多租户中后台、复杂 RBAC 与 BPM 工作流的设计、代码生成与扩展定制。 |

### 📄 办公文档与演示文稿 (Office & Documents) (共 2 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 72 | **Word 专业文档与排版生成专家 (DOCX)**<br/>`docx` | [docx](./skills/docx) | Anthropic 官方出品。全功能读写与精细化编辑 .docx 与 .dotx Word 文档：生成带专业多级目录、页眉页脚、统一标题规范与表格样式的正式报告、公文、备忘录与合同，支持高保真内容提取与修订跟踪。 |
| 73 | **PowerPoint 演示文稿全能处理专家 (PPTX)**<br/>`pptx` | [pptx](./skills/pptx) | Anthropic 官方出品。全功能处理 .pptx 与 .potx 幻灯片：支持从零创建高颜值演讲 PPT、Pitch Deck，解析提取幻灯片文本，深度修改已有 PPT 内容版式，合并/拆分页面，以及处理母版、版式布局、演讲者备注与批注。 |

### 🎨 3D 资产与多媒体创作 (共 1 个)

| # | 技能名称 | 目录链接 | 核心作用与能力详解 |
|---|---|---|---|
| 74 | **单图生成 3D 沉浸式世界与立体网格全能引擎**<br/>`image-blaster` | [image-blaster](./skills/image-blaster) | 仅需一张图片，依托 FAL 与 World Labs 模型生成完整 3D 环境空间、立体道具网格（Meshes）以及空间物理拟声音效。 |
