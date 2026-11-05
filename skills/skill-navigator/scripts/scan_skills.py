import os
import sys
import re
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

SKILLS_DIR = r"d:\APP\development_projects\.agents\skills"
PLUGINS_DIR = r"C:\Users\亲爱的爸爸妈妈别再叫我小傻瓜\.gemini\config\plugins"

def scan_all():
    skills = []
    if os.path.exists(SKILLS_DIR):
        for folder in os.listdir(SKILLS_DIR):
            folder_path = os.path.join(SKILLS_DIR, folder)
            if not os.path.isdir(folder_path):
                continue
            skill_file = os.path.join(folder_path, "SKILL.md")
            if os.path.isfile(skill_file):
                name = folder
                desc = ""
                tags = ""
                try:
                    with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
                        header = f.read(3072)
                        m = re.search(r"^---\s*\n(.*?)\n---", header, re.DOTALL)
                        if m:
                            fm = m.group(1)
                            name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
                            if name_m: name = name_m.group(1).strip()
                            desc_m = re.search(r"^description:\s*(?:>-\s*|>\s*)?(.+?)(?=\n[a-zA-Z0-9_-]+:|\Z)", fm, re.DOTALL)
                            if desc_m:
                                desc = re.sub(r"\s+", " ", desc_m.group(1)).strip()
                            tags_m = re.search(r"^tags:\s*(.+)$", fm, re.MULTILINE)
                            if tags_m: tags = tags_m.group(1).strip()
                except Exception:
                    pass
                skills.append({
                    "name": name,
                    "folder": folder,
                    "desc": desc,
                    "tags": tags,
                    "path": skill_file
                })

    plugins = []
    if os.path.exists(PLUGINS_DIR):
        for p in os.listdir(PLUGINS_DIR):
            p_path = os.path.join(PLUGINS_DIR, p)
            if os.path.isdir(p_path):
                plugins.append({"name": p, "path": p_path})

    return skills, plugins

def search_skills(query, top_k=8):
    skills, plugins = scan_all()
    if not query:
        return skills[:top_k], plugins

    # Tokenize query
    terms = [t.lower() for t in re.split(r"[\s,，、/]+", query.strip()) if len(t) > 0]
    
    scored_skills = []
    for s in skills:
        text = f"{s['name']} {s['folder']} {s['desc']} {s['tags']}".lower()
        score = 0
        for t in terms:
            if t in s['name'].lower():
                score += 15
            elif t in s['folder'].lower():
                score += 10
            elif t in s['tags'].lower():
                score += 8
            elif t in text:
                score += 3
        if score > 0:
            scored_skills.append((score, s))

    scored_skills.sort(key=lambda x: x[0], reverse=True)
    matched_skills = [s for _, s in scored_skills[:top_k]]

    # Also match plugins
    matched_plugins = []
    for p in plugins:
        p_name = p['name'].lower()
        for t in terms:
            if t in p_name:
                matched_plugins.append(p)
                break

    return matched_skills, matched_plugins

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Real-time Skills & Plugins Scanner")
    parser.add_argument("query", nargs="*", help="Keywords for search")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    q = " ".join(args.query) if args.query else ""
    skills, plugins = search_skills(q) if q else scan_all()

    if args.json:
        print(json.dumps({"skills": skills, "plugins": plugins}, ensure_ascii=False, indent=2))
    else:
        print(f"=== 实时扫描结果 (Query: '{q}') ===")
        print(f"匹配到技能 ({len(skills)} 个):")
        for i, s in enumerate(skills, 1):
            print(f"  {i}. [{s['name']}] ({s['folder']}): {s['desc'][:70]}...")
        if plugins:
            print(f"\n匹配到插件 ({len(plugins)} 个):")
            for i, p in enumerate(plugins, 1):
                print(f"  {i}. {p['name']}")
