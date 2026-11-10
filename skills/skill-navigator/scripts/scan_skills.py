import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKILLS_DIR = Path(r"d:\APP\development_projects\.agents\skills")
PLUGINS_DIR = Path(r"C:\Users\亲爱的爸爸妈妈别再叫我小傻瓜\.gemini\config\plugins")
MCP_CONFIG_PATH = Path(r"C:\Users\亲爱的爸爸妈妈别再叫我小傻瓜\.gemini\config\mcp_config.json")
CHINESE_META_PATH = Path(r"d:\APP\development_projects\myskill-project\generate_chinese_readme.py")
AWESOME_DIR = Path(r"d:\APP\development_projects\awesome-agent-skills")
AWESOME_README = AWESOME_DIR / "README.md"
PROMPTS_CHAT_SCRIPT = Path(r"d:\APP\development_projects\.agents\scripts\prompts_chat.py")

AWESOME_STALE_HOURS = 24.0
AWESOME_ENTRY_RE = re.compile(r"-\s+\*\*\[(.*?)\]\((.*?)\)\*\*\s+-\s+(.*)")
CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]{4,}")
ASCII_TERM_RE = re.compile(r"^[a-z0-9][a-z0-9._+-]*$")

CN_FILLER_RE = re.compile(
    r"(帮我|请问|想要|需要|怎么|如何|可以|能否|查找|搜索|寻找|找一下|找个|查一下|推荐|安装|获取|使用|用什么|弄成|变成|搞成|找|查|一个|的|把|感觉)"
)
CN_SYNONYMS = {
    "提示词": ["prompt", "prompts.chat"],
    "模板": ["template", "prompt"],
    "技能": ["skill", "skills"],
    "社区": ["prompts.chat", "community"],
    "审查": ["review", "audit"],
    "调试": ["debug", "diagnose"],
    "测试": ["test", "tdd"],
    "数据库": ["database", "sql", "postgres"],
    "部署": ["deploy", "vercel"],
    "浏览器": ["browser", "playwright", "chrome"],
    "图片": ["image", "photo", "retouch", "visual"],
    "照片": ["photo", "image", "retouch", "portrait"],
    "修图": ["retouch", "photo", "image", "edit", "restore", "upscale"],
    "大片": ["photo", "image", "retouch", "cinematic", "editorial"],
    "摄影": ["photo", "photography", "portrait"],
    "人像": ["portrait", "face", "photo", "retouch"],
    "抠图": ["background", "remove", "image"],
    "海报": ["poster", "design", "canva", "graphic"],
    "设计": ["design", "figma", "canva", "ui"],
    "视频": ["video", "clip", "omni"],
    "前端": ["frontend", "react", "vue", "ui", "tailwind"],
    "后端": ["backend", "api", "fastapi", "server"],
    "爬虫": ["scrape", "crawl", "browser", "playwright"],
    "写作": ["write", "writing", "article"],
    "文档": ["doc", "docx", "pdf", "markdown"],
    "安全": ["security", "audit", "auth"],
    "自动化": ["automation", "workflow", "desktop"],
}


def load_chinese_info() -> dict:
    if not CHINESE_META_PATH.is_file():
        return {}
    old_flag = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_chinese_meta", str(CHINESE_META_PATH))
        if not spec or not spec.loader:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "SKILLS_CHINESE_INFO", {}) or {}
    except Exception:
        return {}
    finally:
        sys.dont_write_bytecode = old_flag


def parse_skill_frontmatter(skill_file: Path, fallback_name: str):
    name, desc, tags = fallback_name, "", ""
    try:
        header = skill_file.read_text(encoding="utf-8", errors="ignore")[:3072]
        m = re.search(r"^---\s*\r?\n(.*?)\r?\n---", header, re.DOTALL)
        if m:
            fm = m.group(1)
            name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
            if name_m:
                name = name_m.group(1).strip().strip("\"'")
            desc_m = re.search(
                r"^description:\s*(?:>-\s*|>\s*)?(.+?)(?=\r?\n[a-zA-Z0-9_-]+:|\Z)",
                fm,
                re.DOTALL | re.MULTILINE,
            )
            if desc_m:
                desc = re.sub(r"\s+", " ", desc_m.group(1)).strip().strip("\"'")
            tags_m = re.search(r"^tags:\s*(.+)$", fm, re.MULTILINE)
            if tags_m:
                tags = tags_m.group(1).strip()
    except Exception:
        pass
    return name, desc, tags


def _scan_plugin_dir(p_path: Path) -> dict:
    info = {
        "name": p_path.name,
        "type": "plugin",
        "desc": "",
        "keywords": [],
        "sub_skills": [],
        "path": str(p_path),
    }
    manifest = p_path / "plugin.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8", errors="ignore"))
            info["desc"] = (data.get("description") or "").strip()
            kws = data.get("keywords") or []
            if isinstance(kws, list):
                info["keywords"] = [str(k).strip() for k in kws if k]
        except Exception:
            pass

    skills_sub = p_path / "skills"
    if skills_sub.is_dir():
        for sub_dir in sorted(skills_sub.iterdir(), key=lambda p: p.name.lower()):
            sf = sub_dir / "SKILL.md"
            if sub_dir.is_dir() and sf.is_file():
                s_name, s_desc, _ = parse_skill_frontmatter(sf, sub_dir.name)
                info["sub_skills"].append({"name": s_name, "desc": s_desc})
    return info


def scan_all():
    cn_info = load_chinese_info()
    skills = []
    if SKILLS_DIR.is_dir():
        for folder_path in sorted(SKILLS_DIR.iterdir(), key=lambda p: p.name.lower()):
            if not folder_path.is_dir():
                continue
            skill_file = folder_path / "SKILL.md"
            if not skill_file.is_file():
                continue
            folder = folder_path.name
            name, desc, tags = parse_skill_frontmatter(skill_file, folder)
            meta = cn_info.get(folder) or cn_info.get(name) or {}
            skills.append({
                "name": name,
                "folder": folder,
                "desc": desc,
                "cn_title": meta.get("title", ""),
                "cn_category": meta.get("category", ""),
                "cn_desc": meta.get("desc", ""),
                "tags": tags,
                "path": str(skill_file),
            })

    plugins = []
    if PLUGINS_DIR.is_dir():
        for p_path in sorted(PLUGINS_DIR.iterdir(), key=lambda p: p.name.lower()):
            if p_path.is_dir():
                plugins.append(_scan_plugin_dir(p_path))

    if MCP_CONFIG_PATH.is_file():
        try:
            mcp_data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
            for srv_name, srv_cfg in mcp_data.get("mcpServers", {}).items():
                plugins.append({
                    "name": srv_name,
                    "type": "mcp",
                    "desc": "",
                    "keywords": [],
                    "sub_skills": [],
                    "path": srv_cfg.get("url") or srv_cfg.get("command", ""),
                })
        except Exception:
            pass

    return skills, plugins


def expand_terms(query: str):
    raw_terms = [t.lower() for t in re.split(r"[\s,，、/]+", query.strip()) if t]
    weights = {}

    def add_term(term: str, weight_scale: float):
        if term:
            prev = weights.get(term, 0.0)
            if weight_scale > prev:
                weights[term] = weight_scale

    for t in raw_terms:
        add_term(t, 1.0)
        for cn_key, en_list in CN_SYNONYMS.items():
            if cn_key in t:
                add_term(cn_key, 0.9)
                for en in en_list:
                    add_term(en, 0.8)

        stripped = CN_FILLER_RE.sub(" ", t)
        for sub in re.split(r"\s+", stripped.strip()):
            if len(sub) >= 2:
                add_term(sub, 0.85)
            # Extract 2-char CJK bigrams so unspaced Chinese phrases still match keywords
            for run in CJK_RUN_RE.findall(sub):
                for idx in range(len(run) - 1):
                    bigram = run[idx : idx + 2]
                    add_term(bigram, 0.45)

    return list(weights.items())


def _term_in_text(term: str, text_lower: str) -> bool:
    if len(term) <= 3 and ASCII_TERM_RE.match(term):
        return bool(re.search(rf"\b{re.escape(term)}\b", text_lower))
    return term in text_lower


def search_skills(query: str, top_k: int = 8, plugin_top_k: int = 6):
    skills, plugins = scan_all()
    if not query:
        return skills, plugins, []

    weighted_terms = expand_terms(query)
    scored_skills = []
    for s in skills:
        cn_text = f"{s['cn_title']} {s['cn_category']} {s['cn_desc']}".lower()
        en_text = f"{s['name']} {s['folder']} {s['desc']} {s['tags']}".lower()
        score = 0.0
        for t, scale in weighted_terms:
            if _term_in_text(t, s["name"].lower()):
                score += 15 * scale
            elif _term_in_text(t, s["folder"].lower()):
                score += 10 * scale
            elif _term_in_text(t, s["tags"].lower()):
                score += 8 * scale
            elif _term_in_text(t, s["cn_title"].lower()):
                score += 9 * scale
            elif _term_in_text(t, cn_text) or _term_in_text(t, en_text):
                score += 3 * scale
        if score > 0:
            scored_skills.append((score, s))

    scored_skills.sort(key=lambda x: x[0], reverse=True)
    matched_skills = [s for _, s in scored_skills[:top_k]]

    scored_plugins = []
    for p in plugins:
        sub_text = " ".join(f"{ss['name']} {ss['desc']}" for ss in p.get("sub_skills", [])).lower()
        kw_text = " ".join(p.get("keywords", [])).lower()
        desc_text = (p.get("desc") or "").lower()
        name_text = p["name"].lower()
        score = 0.0
        for t, scale in weighted_terms:
            if _term_in_text(t, name_text):
                score += 14 * scale
            elif _term_in_text(t, kw_text):
                score += 8 * scale
            elif _term_in_text(t, desc_text) or _term_in_text(t, sub_text):
                score += 4 * scale
        if score > 0:
            scored_plugins.append((score, p))

    scored_plugins.sort(key=lambda x: x[0], reverse=True)
    matched_plugins = [p for _, p in scored_plugins[:plugin_top_k]]
    return matched_skills, matched_plugins, weighted_terms


def _build_install_cmd(name: str, url: str) -> str:
    if "officialskills.sh" in url:
        parts = url.strip("/").split("/")
        if len(parts) >= 5 and parts[-2] == "skills":
            return f"npx skills add {parts[-3]}@{parts[-1]} -g -y"
    if "github.com" in url:
        return f"npx skills add {name} -g -y"
    return ""


def get_awesome_staleness_hours():
    if not AWESOME_README.is_file():
        return None
    marker = AWESOME_DIR / ".git" / "FETCH_HEAD"
    if not marker.is_file():
        marker = AWESOME_README
    try:
        age_sec = max(0.0, time.time() - marker.stat().st_mtime)
        return round(age_sec / 3600.0, 1)
    except Exception:
        return None


def refresh_awesome_repo(timeout: int = 12):
    if not (AWESOME_DIR / ".git").is_dir():
        return False, "awesome-agent-skills 目录非 Git 仓库"
    try:
        proc = subprocess.run(
            ["git", "-C", str(AWESOME_DIR), "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        msg = (proc.stdout or proc.stderr or "").strip().splitlines()
        summary = msg[-1] if msg else "ok"
        return proc.returncode == 0, summary
    except Exception as exc:
        return False, str(exc)


def search_awesome_readme(weighted_terms, top_k: int = 8):
    """Weighted OR-scoring search over local awesome-agent-skills/README.md."""
    if not AWESOME_README.is_file():
        return []

    ascii_terms = [
        (t, scale)
        for t, scale in weighted_terms
        if len(t) >= 2 and ASCII_TERM_RE.match(t)
    ]
    if not ascii_terms:
        return []

    try:
        lines = AWESOME_README.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    current_section = "General"
    scored = []
    for line in lines:
        line_clean = line.strip()
        if line_clean.startswith("<summary>") or line_clean.startswith("### "):
            sec = re.sub(r"<[^>]+>", "", line_clean).replace("###", "").strip()
            if sec:
                current_section = sec
            continue

        m = AWESOME_ENTRY_RE.match(line_clean)
        if not m:
            continue

        name, url, desc = m.groups()
        name_l = name.lower()
        desc_l = desc.lower()
        sec_l = current_section.lower()

        score = 0.0
        distinct_hits = 0
        for t, scale in ascii_terms:
            hit = False
            if _term_in_text(t, name_l):
                score += 10 * scale
                hit = True
            if _term_in_text(t, desc_l):
                score += 4 * scale
                hit = True
            elif _term_in_text(t, sec_l):
                score += 2 * scale
                hit = True
            if hit:
                distinct_hits += 1

        if score > 0:
            score += 6.0 * max(0, distinct_hits - 1)
            scored.append((
                score,
                {
                    "section": current_section,
                    "name": name,
                    "url": url,
                    "desc": desc,
                    "install": _build_install_cmd(name, url),
                },
            ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def search_prompts_chat(query: str, weighted_terms, limit: int = 6):
    if not PROMPTS_CHAT_SCRIPT.is_file():
        return []

    # prompts.chat index is primarily English; convert pure-CJK query via synonym expansion
    remote_query = query
    if not re.search(r"[a-zA-Z]{2,}", query):
        en_tokens = []
        for t, _ in weighted_terms:
            if len(t) >= 3 and ASCII_TERM_RE.match(t) and t not in en_tokens:
                en_tokens.append(t)
        if en_tokens:
            remote_query = " ".join(en_tokens[:4])

    old_flag = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(PROMPTS_CHAT_SCRIPT.parent))
    try:
        import prompts_chat

        res = prompts_chat.search_skills_smart(remote_query, limit=limit)
        return res.get("skills", [])
    except Exception as exc:
        print(f"  [!] prompts.chat 远端检索失败: {exc}", file=sys.stderr)
        return []
    finally:
        sys.dont_write_bytecode = old_flag


def _truncate(text: str, max_len: int = 110) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 1] + "…"


def main():
    parser = argparse.ArgumentParser(description="Real-time Skills & Plugins Scanner")
    parser.add_argument("query", nargs="*", help="Keywords for search")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--local-only", action="store_true", help="Skip awesome-agent-skills index")
    parser.add_argument("--refresh", action="store_true", help="Git pull awesome-agent-skills before searching")
    parser.add_argument("--remote", action="store_true", help="Also query online prompts.chat registry")
    parser.add_argument("--top", type=int, default=8, help="Max results per section")
    args = parser.parse_args()

    q = " ".join(args.query).strip()

    if args.refresh:
        ok, msg = refresh_awesome_repo()
        if not args.json:
            status = "已更新" if ok else "更新失败"
            print(f"[*] awesome-agent-skills {status}: {msg}")

    skills, plugins, weighted_terms = search_skills(q, top_k=args.top)
    awesome_skills = []
    stale_hours = get_awesome_staleness_hours()
    if q and not args.local_only:
        awesome_skills = search_awesome_readme(weighted_terms, top_k=args.top)

    remote_skills = []
    if args.remote and q:
        remote_skills = search_prompts_chat(q, weighted_terms, limit=min(args.top, 6))

    if args.json:
        print(json.dumps({
            "skills": skills,
            "plugins": plugins,
            "awesome_skills": awesome_skills,
            "awesome_stale_hours": stale_hours,
            "prompts_chat_skills": remote_skills,
        }, ensure_ascii=False, indent=2))
        return

    print(f"=== 实时扫描结果 (Query: '{q}') ===")
    print(f"本地匹配技能 ({len(skills)} 个):")
    for i, s in enumerate(skills, 1):
        title = s["cn_title"] or s["name"]
        summary = _truncate(s["cn_desc"] or s["desc"], 100)
        print(f"  {i}. [{s['name']}] ({s['folder']}): {title} — {summary}")

    if plugins:
        print(f"\n本地匹配插件/MCP ({len(plugins)} 个):")
        for i, p in enumerate(plugins, 1):
            sub_names = ", ".join(ss["name"] for ss in p.get("sub_skills", [])[:5])
            extra = f" | 子技能: {sub_names}" if sub_names else ""
            summary = _truncate(p.get("desc", ""), 80)
            desc_part = f" — {summary}" if summary else ""
            print(f"  {i}. [{p.get('type', 'plugin')}] {p['name']}{desc_part}{extra}")

    if q and not args.local_only:
        stale_note = ""
        if stale_hours is not None and stale_hours >= AWESOME_STALE_HOURS:
            days = round(stale_hours / 24.0, 1)
            stale_note = f" [索引距上次同步约 {days} 天，可用 --refresh 拉取 GitHub 最新]"
        print(f"\nGitHub 精选库 awesome-agent-skills ({len(awesome_skills)} 个):{stale_note}")
        if awesome_skills:
            for i, item in enumerate(awesome_skills, 1):
                inst = f" | {item['install']}" if item["install"] else ""
                print(f"  {i}. [{item['section']}] {item['name']} — {_truncate(item['desc'], 90)}{inst}")
        else:
            print("  (未命中，可尝试补充英文核心词或加 --remote 检索 prompts.chat)")

    if args.remote and q:
        print(f"\nprompts.chat 在线社区库 ({len(remote_skills)} 个):")
        if not remote_skills:
            print("  (未命中)")
        for i, s in enumerate(remote_skills, 1):
            print(
                f"  {i}. [{s.get('slug')}] {s.get('title')} (votes={s.get('votes', 0)}, files={s.get('fileCount', 1)})\n"
                f"     {_truncate(s.get('description', ''), 100)}\n"
                f"     安装: python \"{PROMPTS_CHAT_SCRIPT}\" install-skill {s.get('slug')}"
            )


if __name__ == "__main__":
    main()
