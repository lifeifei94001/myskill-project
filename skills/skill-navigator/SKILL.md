---
name: skill-navigator
description: >
  全局技能与插件动态调度中枢（Skill & Plugin Workflow Architect）。在你开始任何开发、设计、自动化、数据或业务任务前，
  自动实时扫描本地最新技能库与插件（15ms 即时动态探测，永不过期），为你推荐最适合的技能流水线组合（Skill Recipe）与执行顺序。
  触发词："用什么技能", "推荐技能", "技能搭配", "工作流规划", "任务前问一下", "怎么组合技能", "技能导航", "/skill-navigator", "/nav".
---

# 全局技能与插件导航器 (Skill Navigator)

你手头拥有不断动态增长的本地技能库（93+ 技能）与 20 个官方生态插件。
为了彻底消除“技能太多记不住、新增技能难同步”的负担，本导航器采用**运行时实时嗅探机制**，杜绝静态过时。

---

## 核心执行工作流

当用户提出任务或询问“用什么技能/怎么搭配”时，执行以下步骤：

### 步骤 1：实时动态探测 (Zero-Stale Scanning)
在推荐前，优先运行内置的实时探测脚本，毫秒级提取本地最新的技能与插件元数据：
```powershell
python "d:\APP\development_projects\.agents\skills\skill-navigator\scripts\scan_skills.py" "<用户任务的核心关键词>"
```
- **绝对实时**：无论刚刚通过 `cocoloop`、`npx skills add` 还是手动新增的技能，均会在 15ms 内被识别。
- **免记名称**：提取关键词对应的候选技能列表及其最新描述。

### 步骤 2：意图分类与生命周期装配
结合实时扫描到的技能与 20 个插件，将任务拆解为标准阶段，输出**技能组合配方 (Skill Recipe)**：
1. **阶段 1：需求澄清与规格约束**（如 `spec-kit`、`/to-spec`、`/grill-with-docs`）
2. **阶段 2：业务实现与核心架构**（如 `data-code-expert`、`shadcn-admin`、`agent-desktop`、`moneyprinterturbo-video` 等）
3. **阶段 3：测试防线与代码复审**（如 `tdd`、`diagnosing-bugs`、`coderabbit`）
4. **阶段 4：平台交付与协同文档**（如 `deploy-to-vercel`、Google Workspace、Notion）

### 步骤 3：输出结构化流水线方案
以极度清晰的 Markdown 形式呈现给用户：
- **🎯 推荐配方链条**：用 `A -> B -> C` 标明先后顺序。
- **💡 推荐理由与各自职责**：简明扼要说明为什么选它、它负责产出什么。
- **🚀 交互式下一步**：直接给出一个可一键确认的起步指令，用户只需回复“开始”即可直接激活第一阶段。
