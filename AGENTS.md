# Agent Instructions & Guidelines

## Skill Discovery & Recommendation Priority

When searching for, recommending, or installing agent skills (via `/find-skills` or general user requests for tools/workflows/capabilities):

1. **Top Priority**: Always search the curated repository **[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** first.
   - Local clone path: `d:\APP\development_projects\awesome-agent-skills`
   - Fast local search command:
     ```bash
     python d:\APP\development_projects\awesome-agent-skills\search.py <keywords...>
     ```
2. **Fallback**: If no matching or suitable skill is found in `awesome-agent-skills`, fall back to searching the broader ecosystem:
   ```bash
   npx skills find <query>
   ```

## Golden Combination: `data-code-expert` + `deploy-to-vercel`

When developing full-stack Web workbenches or applications that involve deploying to Vercel:
- **`data-code-expert`** handles full-stack code architecture (Vue 3 + FastAPI + Turso + Cloudflare R2), complying with the *Nine Cloud Rules for Vercel Serverless* (<25MB dependencies, /tmp path protection, pure Python Turso HTTP driver, `vercel.json` routes, and Awwwards-grade 7-dimension UI/micro-interaction self-check).
- **`deploy-to-vercel`** is automatically triggered as the deployment partner upon code completion to inspect git/CLI state, bind team scope, trigger preview/prod deployments, and return the live deployment URL directly to the user.
