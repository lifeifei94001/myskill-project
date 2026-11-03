import os
import shutil
import re
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent
SKILLS_SRC = Path(r"d:\APP\development_projects\.agents\skills")
SKILLS_DEST = ROOT_DIR / "skills"
AGENTS_MD_SRC = Path(r"d:\APP\development_projects\AGENTS.md")
AGENTS_MD_DEST = ROOT_DIR / "AGENTS.md"

def sync_skills():
    print(f"[*] Syncing skills from {SKILLS_SRC} to {SKILLS_DEST}...")
    SKILLS_DEST.mkdir(parents=True, exist_ok=True)

    # 1. Copy AGENTS.md
    if AGENTS_MD_SRC.exists():
        shutil.copy2(AGENTS_MD_SRC, AGENTS_MD_DEST)
        print("  [+] Synced AGENTS.md")

    # 2. Iterate each skill folder
    skill_folders = [p for p in SKILLS_SRC.iterdir() if p.is_dir()]
    skills_meta = []

    ignore_patterns = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".DS_Store", "node_modules")

    for src_folder in sorted(skill_folders, key=lambda x: x.name.lower()):
        dest_folder = SKILLS_DEST / src_folder.name
        
        # Copy directory tree
        if dest_folder.exists():
            shutil.rmtree(dest_folder)
        shutil.copytree(src_folder, dest_folder, ignore=ignore_patterns)

        # Parse SKILL.md metadata
        skill_md = dest_folder / "SKILL.md"
        if not skill_md.exists():
            # some skills might have lowercase skill.md
            lower_md = dest_folder / "skill.md"
            if lower_md.exists():
                skill_md = lower_md

        name = src_folder.name
        desc = "No description provided."

        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding="utf-8")
                # Parse frontmatter
                fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm_text = fm_match.group(1)
                    # Extract name
                    m_name = re.search(r"^name:\s*(.*?)$", fm_text, re.MULTILINE)
                    if m_name:
                        name = m_name.group(1).strip().strip('"\'')
                    # Extract description
                    m_desc = re.search(r"^description:\s*(.*?)$", fm_text, re.MULTILINE)
                    if m_desc:
                        val = m_desc.group(1).strip()
                        if val in (">", ">-", "|", "|-"):
                            # multiline description
                            rest = fm_text.split(m_desc.group(0))[1]
                            lines = []
                            for line in rest.splitlines():
                                if line.startswith("  "):
                                    lines.append(line.strip())
                                else:
                                    break
                            desc = " ".join(lines)
                        else:
                            desc = val.strip('"\'')
            except Exception as e:
                print(f"  [!] Failed to parse {skill_md}: {e}")

        skills_meta.append({
            "folder": src_folder.name,
            "name": name,
            "desc": desc.replace("\n", " ").strip()
        })

    print(f"[*] Successfully copied {len(skills_meta)} skills.")

    # 3. Generate README.md
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content = f"""# 个人用技能库集合 (myskill-project)

> 本仓库由本地 Agent 自动备份同步，用于集中管理个人所有 Agent Skills。  
> 换电脑时只需一键拉取或运行恢复脚本，即可立即在 Antigravity、Claude Code、Cursor、Codex 等 Agent 中使用全部技能。

- **技能总数**：`{len(skills_meta)}` 个技能
- **最后同步时间**：`{now_str}`
- **备份来源**：`d:\\APP\\development_projects\\.agents\\skills`

---

## 换电脑快速恢复指南 (Quick Start on New PC)

当你更换电脑或在新的项目环境中使用这些技能时，有以下几种简便方式：

### 方式 1：一键恢复脚本（推荐）
克隆本仓库后，运行仓库内的恢复脚本，自动将所有技能部署到当前环境或全局环境：

**Windows (PowerShell)**:
```powershell
.\\restore.ps1
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
.\\backup.ps1
```
脚本会自动同步最新的 `.agents/skills`，重新生成本目录列表，并自动提交推送至 GitHub。

---

## 已备份技能清单目录 (Skills Catalog: {len(skills_meta)})

| # | 技能名称 | 目录 | 功能与触发说明 |
|---|---|---|---|
"""
    for i, item in enumerate(skills_meta, 1):
        # Truncate overly long descriptions for table formatting
        short_desc = item['desc']
        if len(short_desc) > 150:
            short_desc = short_desc[:147] + "..."
        # Escape pipe symbols in markdown table
        short_desc = short_desc.replace("|", "&#124;")
        folder_link = f"[{item['folder']}](./skills/{item['folder']})"
        readme_content += f"| {i} | **{item['name']}** | {folder_link} | {short_desc} |\n"

    readme_path = ROOT_DIR / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    print("  [+] Generated README.md with full catalog.")

if __name__ == "__main__":
    sync_skills()
