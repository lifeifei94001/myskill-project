# 个人用技能库集合 (myskill-project)

> 本仓库由本地 Agent 自动备份同步，用于集中管理个人所有 Agent Skills。  
> 换电脑时只需一键拉取或运行恢复脚本，即可立即在 Antigravity、Claude Code、Cursor、Codex 等 Agent 中使用全部技能。

- **技能总数**：`94` 个技能
- **最后同步时间**：`2026-11-03 10:23:42`
- **备份来源**：`d:\APP\development_projects\.agents\skills`

---

## 换电脑快速恢复指南 (Quick Start on New PC)

当你更换电脑或在新的项目环境中使用这些技能时，有以下几种简便方式：

### 方式 1：一键恢复脚本（推荐）
克隆本仓库后，运行仓库内的恢复脚本，自动将所有技能部署到当前环境或全局环境：

**Windows (PowerShell)**:
```powershell
.\restore.ps1
```

**Windows (CMD)**:
```cmd
restore.bat
```

*(支持自动检测当前项目的 `.agents/skills` 或全局用户技能目录)*

---

### 方式 2：直接克隆到项目工作区
在你的新项目根目录下直接执行：
```bash
git clone https://github.com/lifeifei94001/myskill-project.git .agents-repo
# 将技能目录链接或复制到项目的 .agents/skills
mkdir -p .agents
cp -r .agents-repo/skills .agents/skills
cp .agents-repo/AGENTS.md ./AGENTS.md
```

---

### 方式 3：通过 Skills CLI 安装单个技能
```bash
npx skills add lifeifei94001/myskill-project --skill <技能名称> -g -y
```

---

## 本地日常备份使用方式

在本地完成技能开发、安装新技能或调整后，可直接在仓库目录执行：
```cmd
backup.bat
```
或运行：
```powershell
.\backup.ps1
```
脚本会自动同步最新的 `.agents/skills`，重新生成本目录列表，并自动提交推送至 GitHub。

---

## 已备份技能清单目录 (Skills Catalog: 94)

| # | 技能名称 | 目录 | 功能与触发说明 |
|---|---|---|---|
| 1 | **agent-browser** | [agent-browser](./skills/agent-browser) | Headless browser automation CLI optimized for AI agents with accessibility tree snapshots and ref-based element selection |
| 2 | **agent-overflow** | [agent-overflow](./skills/agent-overflow) | No description provided. |
| 3 | **antigravity-china-access** | [antigravity-china-access](./skills/antigravity-china-access) | Google Antigravity 中国大陆网络连接解决方案。为 Google Antigravity 提供进程级局部代理配置与无黑框快捷启动，用于解决中国大陆网络环境下 Antigravity 无法登录、模型超时、Agent 连接中断、Language Server 无法拉取等问题，无需开... |
| 4 | **anysearch** | [anysearch](./skills/anysearch) | Real-time search engine supporting web search, vertical domain search, parallel batch search, and URL content extraction. |
| 5 | **anysearch** | [anysearch-skill](./skills/anysearch-skill) | Real-time search engine supporting web search, vertical domain search, parallel batch search, and URL content extraction. |
| 6 | **api-gateway** | [API Gateway](./skills/API Gateway) |  |
| 7 | **ask-matt** | [ask-matt](./skills/ask-matt) | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| 8 | **brainstorming** | [brainstorming](./skills/brainstorming) | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything... |
| 9 | **Browserbase Persist with captcha** | [Browserbase Persist with captcha](./skills/Browserbase Persist with captcha) | Create and manage persistent Browserbase cloud browser sessions with authentication persistence. Use when the user needs to automate browsers, main... |
| 10 | **chief-of-staff** | [chief-of-staff](./skills/chief-of-staff) | Pursue a long-running goal in a single session by co-ordinating subagents. |
| 11 | **claude-handoff** | [claude-handoff](./skills/claude-handoff) | Hand the current conversation off to a fresh background agent that picks up the work immediately. |
| 12 | **cocoloop** | [cocoloop](./skills/cocoloop) | 一个更快速、更安全的 Skill 管理器，用于安装、管理、更新和卸载 Skills。优先使用当用户需要安装 skill、更新 skill、卸载 skill、管理 skills 或进行 skill 安全检查时。支持通过 URL、名称搜索、GitHub 等多种方式定位并安装 skills，集成 B... |
| 13 | **code-review** | [code-review](./skills/code-review) | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented ... |
| 14 | **codebase-design** | [codebase-design](./skills/codebase-design) | Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, deci... |
| 15 | **data-code-expert** | [data-code-expert](./skills/data-code-expert) | 高性能表格数据处理与获奖级全栈工作台专家，覆盖四种场景：①一次性脚本处理（汇总/清洗/合并/去重/透视/TopN，固定用 polars+fastexcel+xlsxwriter，产出.py或.ipynb）；②桌面小工具（默认CustomTkinter原生GUI，可打包exe；多表联动采用“Py... |
| 16 | **deploy-to-vercel** | [deploy-to-vercel](./skills/deploy-to-vercel) | Deploy applications and websites to Vercel. Use when the user requests deployment actions like "deploy my app", "deploy and give me the link", "pus... |
| 17 | **diagnosing-bugs** | [diagnosing-bugs](./skills/diagnosing-bugs) | Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/fail... |
| 18 | **diagnosing-superpowers** | [diagnosing-superpowers](./skills/diagnosing-superpowers) | Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill ... |
| 19 | **dispatching-parallel-agents** | [dispatching-parallel-agents](./skills/dispatching-parallel-agents) | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| 20 | **docker-sandbox** | [docker-sandbox](./skills/docker-sandbox) | Create and manage Docker sandboxed VM environments for safe agent execution. Use when running untrusted code, exploring packages, or isolating agen... |
| 21 | **domain-modeling** | [domain-modeling](./skills/domain-modeling) | Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ... |
| 22 | **executing-plans** | [executing-plans](./skills/executing-plans) | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no sub... |
| 23 | **find-skills** | [find-skills](./skills/find-skills) | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", o... |
| 24 | **finishing-a-development-branch** | [finishing-a-development-branch](./skills/finishing-a-development-branch) | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| 25 | **geo-sleuth** | [geo-sleuth](./skills/geo-sleuth) | Geolocate or chronolocate a photo with tool-verified reasoning (where was this taken / when was it taken / photo geolocation / geo-guessing). Given... |
| 26 | **git-guardrails-claude-code** | [git-guardrails-claude-code](./skills/git-guardrails-claude-code) | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to p... |
| 27 | **grill-me** | [grill-me](./skills/grill-me) | A relentless interview to sharpen a plan or design. |
| 28 | **grill-with-docs** | [grill-with-docs](./skills/grill-with-docs) | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| 29 | **grilling** | [grilling](./skills/grilling) | Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phr... |
| 30 | **handoff** | [handoff](./skills/handoff) | Compact the current conversation into a handoff document for another agent to pick up. |
| 31 | **image-blast-3d** | [image-blast-3d](./skills/image-blast-3d) | Generate one specified atomic 3D object. Use when the user names exactly one object instance to make, or provides one image plus the object name/de... |
| 32 | **image-blast-image-edit** | [image-blast-image-edit](./skills/image-blast-image-edit) | Generate one image edit from explicit input images and a prompt. Use for source cleanup, clean plates, object removal, or other FAL-backed image ed... |
| 33 | **image-blast-plate** | [image-blast-plate](./skills/image-blast-plate) | Generate one clean plate/source cleanup image for an IMAGE-BLASTER world. Use after confirmed objects exist, when removing foreground objects or ot... |
| 34 | **image-blast-project** | [image-blast-project](./skills/image-blast-project) | Create, inspect, and manage an IMAGE-BLAST project envelope under worlds/<slug>. Use before other image-blast skills (image-blast-uncover, image-bl... |
| 35 | **image-blast-sfx** | [image-blast-sfx](./skills/image-blast-sfx) | Generate and post-process a clean sound effect, object impact, or ambient loop. |
| 36 | **image-blast-uncover** | [image-blast-uncover](./skills/image-blast-uncover) | Main image analysis skill, object generation, plate decisionmaking, and initial scene description. Use this skill when user wants to create objects... |
| 37 | **image-blast-wildcard** | [image-blast-wildcard](./skills/image-blast-wildcard) | Discover and run any FAL API model or operation the user requests. Use this as a generic FAL escape hatch when the user wants to generate something... |
| 38 | **image-blast-world** | [image-blast-world](./skills/image-blast-world) | Generate the 3D static environment of a world from a source or plate image. |
| 39 | **image-blaster** | [image-blaster](./skills/image-blaster) | Creates 3D environments, SFX, and meshes from a single image using Claude skills, World Labs, and FAL. |
| 40 | **implement** | [implement](./skills/implement) | Implement a piece of work based on a spec or set of tickets. |
| 41 | **implement-spec** | [implement-spec](./skills/implement-spec) | Implement the result of /to-spec and /to-tickets in code. |
| 42 | **improve-codebase-architecture** | [improve-codebase-architecture](./skills/improve-codebase-architecture) | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| 43 | **life-decision-guide** | [life-decision-guide](./skills/life-decision-guide) | 用《高性价比人生指南》(github.com/eternity4719/HowToLiveBetter) 的正文回答具体的人生决策：该不该做、值不值、怎么选、出事了先做什么、能领哪笔钱、这么干犯不犯法。先把相关条目查出来再答，按成本（钱/时间/毅力）、收益量级和证据等级 A/B/C 排序，每条... |
| 44 | **loop-me** | [loop-me](./skills/loop-me) | Grill me about specs for the workflows I want to build, within this workspace. |
| 45 | **mattpocock-skills** | [mattpocock-skills](./skills/mattpocock-skills) | No description provided. |
| 46 | **migrate-to-shoehorn** | [migrate-to-shoehorn](./skills/migrate-to-shoehorn) | Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or nee... |
| 47 | **OpenClaw GitHub Assistant** | [OpenClaw GitHub Assistant](./skills/OpenClaw GitHub Assistant) | Query and manage GitHub repositories - list repos, check CI status, create issues, search repos, and view recent activity. |
| 48 | **pr** | [pr](./skills/pr) | Use when writing a PR body. |
| 49 | **prototype** | [prototype](./skills/prototype) | Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or exp... |
| 50 | **reverse-engineer-anything** | [rea](./skills/rea) | Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. Use shipped-artifact or requested runtime ... |
| 51 | **rea-analysis-optimization** | [rea-analysis-optimization](./skills/rea-analysis-optimization) | Optimize REA providers and shared analysis workflows for agent context, latency, CPU, and memory while preserving correctness and Evidence. Use for... |
| 52 | **rea-changelog-update** | [rea-changelog-update](./skills/rea-changelog-update) | Prepare or rewrite REA release changelogs and GitHub release notes from pinned Git history, with verified contributor thanks and Release Please syn... |
| 53 | **rea-ci-tests-audit** | [rea-ci-tests-audit](./skills/rea-ci-tests-audit) | Audit REA CI and test suites for correctness, fixture drift, false passes, and measured performance; use for suite or workflow investigations and e... |
| 54 | **rea-tool-design** | [rea-tool-design](./skills/rea-tool-design) | Design or change REA investigation tools, CLI/MCP contracts, provider capabilities, and Evidence semantics. |
| 55 | **receiving-code-review** | [receiving-code-review](./skills/receiving-code-review) | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requir... |
| 56 | **requesting-code-review** | [requesting-code-review](./skills/requesting-code-review) | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| 57 | **research** | [research](./skills/research) | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic ... |
| 58 | **retro** | [retro](./skills/retro) | Conduct a retrospective on a coding session. |
| 59 | **reverse-engineer-anything** | [reverse-engineer-anything](./skills/reverse-engineer-anything) | Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. Use shipped-artifact or requested runtime ... |
| 60 | **ruoyi-shadcn-fullstack** | [ruoyi-shadcn-fullstack](./skills/ruoyi-shadcn-fullstack) | Use when designing, scaffolding, or generating full-stack admin applications combining RuoYi backend standards (Spring Boot, MyBatis-Plus, MySQL, R... |
| 61 | **scaffold-exercises** | [scaffold-exercises](./skills/scaffold-exercises) | Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercise... |
| 62 | **self-improvement** | [self-improvement](./skills/self-improvement) | Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User cor... |
| 63 | **Self-Improving Agent** | [Self-Improving Agent](./skills/Self-Improving Agent) | Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User cor... |
| 64 | **setup-matt-pocock-skills** | [setup-matt-pocock-skills](./skills/setup-matt-pocock-skills) | Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use... |
| 65 | **setup-pre-commit** | [setup-pre-commit](./skills/setup-pre-commit) | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hook... |
| 66 | **setup-ts-deep-modules** | [setup-ts-deep-modules](./skills/setup-ts-deep-modules) | Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only throug... |
| 67 | **shadcn-admin** | [shadcn-admin](./skills/shadcn-admin) | Use when scaffolding, building, or customizing admin dashboard projects based on the shadcn-admin template (Vite + React + TypeScript + Tailwind CS... |
| 68 | **skill-creator** | [skill-creator](./skills/skill-creator) | Use when the user wants to create a new skill, update or improve an existing skill, scaffold SKILL.md templates, optimize frontmatter trigger descr... |
| 69 | **subagent-driven-development** | [subagent-driven-development](./skills/subagent-driven-development) | Use when executing implementation plans with independent tasks in the current session |
| 70 | **superpowers** | [superpowers](./skills/superpowers) | No description provided. |
| 71 | **systematic-debugging** | [systematic-debugging](./skills/systematic-debugging) | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| 72 | **tavily-search-pro** | [tavily-search-pro](./skills/tavily-search-pro) |  |
| 73 | **tdd** | [tdd](./skills/tdd) | Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests. |
| 74 | **teach** | [teach](./skills/teach) | Teach the user a new skill or concept, within this workspace. |
| 75 | **test-driven-development** | [test-driven-development](./skills/test-driven-development) | Use when implementing any feature or bugfix, before writing implementation code |
| 76 | **to-questionnaire** | [to-questionnaire](./skills/to-questionnaire) | Turn a decision you can't fully answer into a questionnaire for someone else to fill in. |
| 77 | **to-spec** | [to-spec](./skills/to-spec) | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed. |
| 78 | **to-tickets** | [to-tickets](./skills/to-tickets) | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured... |
| 79 | **triage** | [triage](./skills/triage) | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs. |
| 80 | **using-git-worktrees** | [using-git-worktrees](./skills/using-git-worktrees) | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace... |
| 81 | **using-superpowers** | [using-superpowers](./skills/using-superpowers) | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying qu... |
| 82 | **verification-before-completion** | [verification-before-completion](./skills/verification-before-completion) | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirm... |
| 83 | **wait-what** | [wait-what](./skills/wait-what) | Stop. That last message did not land: re-pitch it. |
| 84 | **wayfinder** | [wayfinder](./skills/wayfinder) | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at... |
| 85 | **wechat-miniprogram-expert** | [wechat-miniprogram-expert](./skills/wechat-miniprogram-expert) | Use when the user wants to develop, debug, scaffold, or deploy a WeChat Mini Program (微信小程序). Covers native WeChat Mini Program development, cloud ... |
| 86 | **Who Is Actor** | [Who Is Actor](./skills/Who Is Actor) |  |
| 87 | **wizard** | [wizard](./skills/wizard) | Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up creden... |
| 88 | **writing-beats** | [writing-beats](./skills/writing-beats) | Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it. |
| 89 | **writing-for-agents** | [writing-for-agents](./skills/writing-for-agents) | Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md. |
| 90 | **writing-fragments** | [writing-fragments](./skills/writing-fragments) | Writing, explore: mine raw fragments, no structure yet. |
| 91 | **writing-plans** | [writing-plans](./skills/writing-plans) | Use when you have a spec or requirements for a multi-step task, before touching code |
| 92 | **writing-shape** | [writing-shape](./skills/writing-shape) | Writing, exploit: shape raw material into an article, paragraph by paragraph. |
| 93 | **writing-skills** | [writing-skills](./skills/writing-skills) | Use when creating new skills, editing existing skills, or verifying skills work before deployment |
| 94 | **yudao-vben-admin-builder** | [yudao-vben-admin-builder](./skills/yudao-vben-admin-builder) | Use when building or extending Java enterprise management systems with Yudao (ruoyi-vue-pro / yudao-boot-mini) and Vben 5 or Vue3 Element Plus fron... |
