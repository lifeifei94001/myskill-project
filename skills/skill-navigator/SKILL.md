---
name: skill-navigator
description: >
  全局技能与插件动态调度中枢（Skill & Plugin Workflow Architect）。在你开始任何开发、设计、自动化、数据或业务任务前，
  自动实时扫描本地最新技能库、已安装插件/MCP 与 GitHub awesome-agent-skills 精选索引（~0.1s 联合检索），为你推荐最适合的技能流水线组合（Skill Recipe）与执行顺序。
  触发词："用什么技能", "推荐技能", "技能搭配", "工作流规划", "任务前问一下", "怎么组合技能", "技能导航", "/skill-navigator", "/nav".
---

# 全局技能与插件导航器 (Skill Navigator)

你手头拥有动态增长的本地技能库、官方生态插件，以及本地镜像的 `VoltAgent/awesome-agent-skills` GitHub 精选目录。
本导航器采用**零延迟联合探测 + 分层按需阅读**机制：既保留全生态视野，又避免推荐阶段陷入多轮重复读文件。

---

## 核心执行工作流

当用户提出任务或询问“用什么技能/怎么搭配”时，严格按以下 3 步执行：

### 步骤 1：一次联合探测（本地 + 插件 + GitHub 精选索引）
优先运行内置探测脚本，单次调用即可同时检索**本地技能库（含中英文同义扩展）**、**已安装插件及其子技能**、以及 **`VoltAgent/awesome-agent-skills` 本地索引**（多词 OR 加权排序，无需自己拼多次单关键词）：
```powershell
python "d:\APP\development_projects\.agents\skills\skill-navigator\scripts\scan_skills.py" "<用户任务核心词>"
```
- **按需追新与联网**：
  - 若输出提示 `awesome-agent-skills` 索引超过 24 小时未同步，且用户明确要追 GitHub 最新技能，可追加 `--refresh` 拉取最新目录后再查；
  - 若本地与 `awesome-agent-skills` 未充分覆盖，或用户想找社区现成技能/提示词，追加 `--remote` 联动检索 `prompts.chat` 在线库。
  - 若仅需离线极速查已装能力，可加 `--local-only`。

### 步骤 2：分层按需阅读（提速关键）
1. **推荐阶段只读主干**：从步骤 1 返回的摘要中锁定 **1~2 个核心主技能**，仅阅读它们的 `SKILL.md` 确认能力边界与硬性红线即可。
2. **禁止导航阶段过度深挖**：辅助/下游技能及 `references/`、`scripts/` 子文件**先不展开细读**，直接依据步骤 1 摘要中的子技能名和描述完成流水线装配；等用户回复“开始”执行具体阶段时，再按需深读对应文档。
3. **插件账户状态**：仅当配方强依赖外部已装插件（如 Canva、Figma、Notion、Google Workspace）时，调用一次 `list_plugin_accounts` 核验登录状态。

### 步骤 3：输出结构化流水线方案 (Skill Recipe)
按「需求澄清/诊断 → 核心实现 → 审查/质量防线 → 交付与跨界延伸」拆解阶段，用清晰 Markdown 输出：
- **🎯 推荐配方链条**：用 `A -> B -> C` 标明主线与可选延伸分支。
- **💡 职责分工与生态补强**：简述每个技能/插件产出的交付物，并明确区分**本地已就绪**与**GitHub / 社区可一键补装**的技能。
- **🚀 交互式下一步**：给出可一键确认的起步指令，用户回复后立即进入第一阶段执行。
