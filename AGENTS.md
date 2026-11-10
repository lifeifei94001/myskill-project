# Agent Instructions & Guidelines

## Skill Discovery & Recommendation Priority

When searching for, recommending, or installing agent skills (via `/find-skills` or general user requests for tools/workflows/capabilities):

1. **Top Priority**: Always search the curated repository **[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** first.
   - Local clone path: `d:\APP\development_projects\awesome-agent-skills`
   - Fast local search command:
     ```bash
     python d:\APP\development_projects\awesome-agent-skills\search.py <keywords...>
     ```
2. **Community Prompt & Skill Registry (`f/prompts.chat`)**: Also search **[prompts.chat](https://prompts.chat/skills)** (`f/prompts.chat`) for community Agent Skills and reusable AI prompts:
   - Via MCP (`prompts.chat` -> `https://prompts.chat/api/mcp`): `search_skills` / `get_skill` (and `search_prompts` / `get_prompt`)
   - Via local CLI helper (works anytime & installs directly to `.agents/skills/<slug>`):
     ```bash
     python d:\APP\development_projects\.agents\scripts\prompts_chat.py search-skills <keywords...>
     python d:\APP\development_projects\.agents\scripts\prompts_chat.py install-skill <id_or_slug>
     ```
   - **Workspace Target Path**: When installing a skill from `prompts.chat` (including via `skill-lookup`), always write its files to `d:\APP\development_projects\.agents\skills\<slug>\` (NOT `.claude/skills/<slug>/`).
3. **Fallback**: If no matching or suitable skill is found above, fall back to searching the broader ecosystem:
   ```bash
   npx skills find <query>
   ```

## Upstream Skills Auto-Update & Maintenance (技能上游自动更新与版本维护)

当用户提出“检查技能更新”、“更新技能”、“有最新版本吗”、“有些技能版本比较落后”、“从 GitHub 仓库同步最新技能”时：

1. **快速状态检测 (Check Only)**:
   ```bash
   python d:\APP\development_projects\myskill-project\update_skills.py --check
   ```
   极速检测上游各大 GitHub 官方与开源社区仓库（`obra/superpowers`, `mattpocock/skills`, `f/prompts.chat`, `github/spec-kit`, `vercel-labs/agent-browser` 等）的最新 commit SHA 与可用更新。

2. **一键执行安全更新 (Update & Sync)**:
   ```bash
   python d:\APP\development_projects\myskill-project\update_skills.py --update --all --sync
   ```
   - **自动快照备份**：在覆盖任何技能目录前，会在 `myskill-project/.backup/pre_update_<timestamp>/` 自动创建完整快照；
   - **严格保护本地定制**：受保护的本地业务技能（如 `golden-photo-retouch` 带专属防换脸 Prompt 与 `.learnings` 铁律、`aihuishou-pricing` 爱回收估价爬虫、`huishoubao-pricing` 回收宝官方估价爬虫、`samsung-tradein-pricing`、`laptop-specs-collector`、`data-code-expert` 等）已在 `upstream_registry.json` 中锁定保护，绝不会被上游覆盖；
   - **自动同步与文档生成**：更新完成后会自动调用 `sync.py` 增量同步至 `myskill-project/skills`，并自动重新生成最新的中文版 `README.md`。

3. **单个指定技能更新**:
   ```bash
   python d:\APP\development_projects\myskill-project\update_skills.py --update --skill <skill_name> --sync
   ```

4. **定时/不定时自动巡检**:
   用户可借助 Antigravity 的 `/schedule` 机制（如设置每周一上午 9 点巡检）或 Windows 任务计划程序定期运行 `python update_skills.py --check`，一旦发现落后版本即时向用户汇报并提供一键更新入口。

## Golden Combination: `data-code-expert` + `deploy-to-vercel`

When developing full-stack Web workbenches or applications that involve deploying to Vercel:
- **`data-code-expert`** handles full-stack code architecture (Vue 3 + FastAPI + Turso + Cloudflare R2), complying with the *Nine Cloud Rules for Vercel Serverless* (<25MB dependencies, /tmp path protection, pure Python Turso HTTP driver, `vercel.json` routes, and Awwwards-grade 7-dimension UI/micro-interaction self-check).
- **`deploy-to-vercel`** is automatically triggered as the deployment partner upon code completion to inspect git/CLI state, bind team scope, trigger preview/prod deployments, and return the live deployment URL directly to the user.
