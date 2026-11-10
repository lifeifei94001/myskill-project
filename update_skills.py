#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Skills Upstream Auto-Updater (技能上游自动更新器)
=====================================================
自动从 GitHub 官方与开源社区仓库检测并更新本地 Agent Skills，
防止技能版本落后，同时严格保护用户本地精调/定制技能不被覆盖。

使用示例：
  python update_skills.py --check               # 快速检查所有技能是否有上游更新
  python update_skills.py --update --all --sync # 一键更新所有落后技能并同步到 myskill-project 备份
  python update_skills.py --update --skill brainstorming # 仅更新指定技能
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
import stat

def on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def safe_rmtree(path):
    if path.exists():
        shutil.rmtree(path, onerror=on_rm_error)
from pathlib import Path
from datetime import datetime

# Windows 终端编码兼容保护
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 路径常量
SCRIPT_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = SCRIPT_DIR / "upstream_registry.json"
BACKUP_DIR = SCRIPT_DIR / ".backup"
CACHE_DIR = SCRIPT_DIR / ".cache"
LOCAL_SKILLS_DIR = Path(r"d:\APP\development_projects\.agents\skills")
SYNC_SCRIPT = SCRIPT_DIR / "sync.py"

def run_cmd(cmd, cwd=None, timeout=30):
    """运行外部命令并返回 (exit_code, stdout, stderr)"""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=isinstance(cmd, str)
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def get_remote_head_sha(repo_url, branch="main"):
    """使用 git ls-remote 极速获取远端分支最新 commit SHA (无需下载代码)"""
    ref = f"refs/heads/{branch}" if branch != "HEAD" else "HEAD"
    code, out, _ = run_cmd(["git", "ls-remote", repo_url, ref], timeout=15)
    if code == 0 and out:
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and (parts[1] == ref or parts[1] == "HEAD"):
                return parts[0]
            elif len(parts) >= 1 and "\n" not in out.strip():
                return parts[0]
    return None

def load_registry():
    if not REGISTRY_FILE.exists():
        print(f"[!] 找不到注册表配置文件: {REGISTRY_FILE}")
        sys.exit(1)
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_registry(registry):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def backup_skill(skill_name, backup_root):
    """备份单个技能目录"""
    skill_path = LOCAL_SKILLS_DIR / skill_name
    if not skill_path.exists():
        return None
    dest_path = backup_root / skill_name
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        safe_rmtree(dest_path)
    shutil.copytree(skill_path, dest_path)
    return dest_path

def check_updates(registry, target_skill=None):
    """检查哪些技能存在上游更新"""
    print("=" * 68)
    print(" [*] 开始检测上游 GitHub 技能仓库更新状态...")
    print("=" * 68)

    status_report = []

    # 1. 检测 Bundle Repositories (如 superpowers, mattpocock)
    bundles = registry.get("bundle_repositories", {})
    for b_key, b_info in bundles.items():
        repo_name = b_info.get("name", b_key)
        repo_url = b_info["repo_url"]
        branch = b_info.get("branch", "main")
        last_sha = b_info.get("last_synced_sha", "")

        # 过滤技能
        skills_in_bundle = []
        if "skill_mapping" in b_info:
            skills_in_bundle = list(b_info["skill_mapping"].keys())
        elif "skills" in b_info:
            skills_in_bundle = b_info["skills"]

        if target_skill and target_skill not in skills_in_bundle:
            continue

        print(f"\n[*] 正在查询 [{repo_name}] 远端最新状态 ({branch})...")
        remote_sha = get_remote_head_sha(repo_url, branch)
        
        has_new_commit = False
        if remote_sha:
            if not last_sha:
                has_new_commit = True
                sha_status = f"首次追踪 (远端 SHA: {remote_sha[:7]})"
            elif remote_sha != last_sha:
                has_new_commit = True
                sha_status = f"有新提交 ({last_sha[:7]} -> {remote_sha[:7]})"
            else:
                sha_status = f"最新 (SHA: {remote_sha[:7]})"
        else:
            sha_status = "网络超时或查询失败"

        for s in skills_in_bundle:
            if target_skill and s != target_skill:
                continue
            local_exists = (LOCAL_SKILLS_DIR / s).exists()
            status_report.append({
                "skill": s,
                "bundle": b_key,
                "repo": repo_name,
                "has_update": has_new_commit,
                "status_desc": sha_status if local_exists else "本地未安装",
                "remote_sha": remote_sha
            })

    # 2. 检测单仓库技能 (Single Repositories)
    single_repos = registry.get("single_repositories", {})
    for s_name, s_info in single_repos.items():
        if target_skill and s_name != target_skill:
            continue
        repo_url = s_info["repo_url"]
        branch = s_info.get("branch", "main")
        last_sha = s_info.get("last_synced_sha", "")

        print(f"[*] 正在查询单仓库 [{s_name}] ({repo_url})...")
        remote_sha = get_remote_head_sha(repo_url, branch)
        has_new_commit = False
        if remote_sha:
            if not last_sha:
                has_new_commit = True
                sha_status = f"首次追踪 (SHA: {remote_sha[:7]})"
            elif remote_sha != last_sha:
                has_new_commit = True
                sha_status = f"有新提交 ({last_sha[:7]} -> {remote_sha[:7]})"
            else:
                sha_status = f"最新 (SHA: {remote_sha[:7]})"
        else:
            sha_status = "查询失败"

        status_report.append({
            "skill": s_name,
            "bundle": None,
            "repo": repo_url.split("/")[-1].replace(".git", ""),
            "has_update": has_new_commit,
            "status_desc": sha_status,
            "remote_sha": remote_sha
        })

    # 3. 检测本地 Git 管理的技能
    git_skills = registry.get("git_managed_skills", {})
    for g_name, g_info in git_skills.items():
        if target_skill and g_name != target_skill:
            continue
        g_path = Path(g_info["local_path"])
        if g_path.exists() and (g_path / ".git").exists():
            print(f"[*] 正在检测本地 Git 技能 [{g_name}]...")
            code, out, _ = run_cmd(["git", "fetch", "--dry-run"], cwd=str(g_path))
            code2, out2, _ = run_cmd(["git", "status", "-uno"], cwd=str(g_path))
            has_behind = "Your branch is behind" in out2 or code == 0 and len(out) > 0
            status_report.append({
                "skill": g_name,
                "bundle": "git_managed",
                "repo": "本地 Git 仓库",
                "has_update": has_behind,
                "status_desc": "可 pull 更新" if has_behind else "本地与远端一致",
                "remote_sha": None
            })

    # 4. 统计输出
    print("\n" + "=" * 68)
    print(" [=] 技能更新检测结果汇总：")
    print("=" * 68)
    update_count = 0
    for item in status_report:
        icon = "[UPDATE]" if item["has_update"] else "[OK]    "
        if item["has_update"]:
            update_count += 1
        print(f" {icon}  {item['skill']:<30} [{item['repo']}] -> {item['status_desc']}")

    print("-" * 68)
    print(f" 检测完成：共检查 {len(status_report)} 个技能，其中 {update_count} 个技能有可用更新。")
    print("=" * 68)
    return status_report

def update_bundle_repo(b_key, b_info, registry, backup_root, target_skill=None):
    """从 Bundle 仓库克隆并覆盖更新对应技能"""
    repo_name = b_info.get("name", b_key)
    repo_url = b_info["repo_url"]
    branch = b_info.get("branch", "main")

    # 准备临时克隆目录
    clone_dest = CACHE_DIR / b_key
    if clone_dest.exists():
        safe_rmtree(clone_dest)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n[+] 正在拉取 [{repo_name}] 最新仓库代码 ({branch})...")
    base_sub = b_info.get("skills_base_path", "skills")
    if b_info.get("sparse"):
        code, out, err = run_cmd([
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            "-b", branch, repo_url, str(clone_dest)
        ], timeout=60)
        if code == 0 and base_sub not in ("", "."):
            code, out, err = run_cmd(["git", "sparse-checkout", "set", base_sub], cwd=str(clone_dest), timeout=60)
    else:
        code, out, err = run_cmd(["git", "clone", "--depth", "1", "-b", branch, repo_url, str(clone_dest)], timeout=60)
    if code != 0:
        print(f"[!] 克隆仓库失败 [{repo_name}]: {err}")
        return False

    # 获取克隆后的最新 commit SHA
    _, sha_out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=str(clone_dest))
    latest_sha = sha_out.strip() if sha_out else ""

    # 获取技能映射
    base_dir = clone_dest if base_sub in ("", ".") else clone_dest / base_sub
    mapping = {}
    if "skill_mapping" in b_info:
        for s_name, sub in b_info["skill_mapping"].items():
            if sub == ".":
                mapping[s_name] = clone_dest
            else:
                mapping[s_name] = base_dir / sub
    elif "skills" in b_info:
        for s_name in b_info["skills"]:
            if s_name == b_key:
                mapping[s_name] = clone_dest
            else:
                mapping[s_name] = base_dir / s_name

    updated_skills = []
    protected = registry.get("protected_custom_skills", {})

    for s_name, src_path in mapping.items():
        if target_skill and s_name != target_skill:
            continue
        if s_name in protected:
            print(f"  [LOCKED 跳过保护技能] {s_name} ({protected[s_name].get('reason', '受保护')})")
            continue

        if not src_path.exists():
            print(f"  [?] 远端仓库未找到该技能路径: {src_path.relative_to(clone_dest)}")
            continue

        # 备份本地现有版本
        backup_skill(s_name, backup_root)

        # 覆盖安装到本地 .agents/skills
        target_dir = LOCAL_SKILLS_DIR / s_name
        if target_dir.exists():
            safe_rmtree(target_dir)

        ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
        shutil.copytree(src_path, target_dir, ignore=ignore)
        updated_skills.append(s_name)
        print(f"  [+] 已更新: {s_name}")

    # 更新 registry 中记录的 SHA（仅在全量更新该 bundle 时记录）
    if latest_sha and not target_skill:
        b_info["last_synced_sha"] = latest_sha
        b_info["last_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 清理缓存
    safe_rmtree(clone_dest)
    return True

def update_single_repo(s_name, s_info, registry, backup_root):
    """更新单个仓库技能"""
    protected = registry.get("protected_custom_skills", {})
    if s_name in protected:
        print(f"  [LOCKED 跳过保护技能] {s_name} ({protected[s_name].get('reason', '受保护')})")
        return False

    repo_url = s_info["repo_url"]
    branch = s_info.get("branch", "main")
    subpath = s_info.get("subpath", ".")

    clone_dest = CACHE_DIR / f"single_{s_name}"
    if clone_dest.exists():
        safe_rmtree(clone_dest)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n[+] 正在更新单仓库技能 [{s_name}] ({repo_url})...")
    code, out, err = run_cmd(["git", "clone", "--depth", "1", "-b", branch, repo_url, str(clone_dest)])
    if code != 0:
        print(f"[!] 克隆失败: {err}")
        return False

    _, sha_out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=str(clone_dest))
    latest_sha = sha_out.strip() if sha_out else ""

    src_path = clone_dest if subpath == "." else clone_dest / subpath
    if not src_path.exists():
        print(f"[!] 找不到技能目录: {subpath}")
        safe_rmtree(clone_dest)
        return False

    # 备份现有
    backup_skill(s_name, backup_root)

    # 覆盖更新
    target_dir = LOCAL_SKILLS_DIR / s_name
    if target_dir.exists():
        safe_rmtree(target_dir)

    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
    shutil.copytree(src_path, target_dir, ignore=ignore)
    print(f"  [+] 已更新: {s_name}")

    if latest_sha:
        s_info["last_synced_sha"] = latest_sha
        s_info["last_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    safe_rmtree(clone_dest)
    return True

def update_git_managed(g_name, g_info):
    """更新本地 Git 管理的仓库"""
    g_path = Path(g_info["local_path"])
    if not g_path.exists() or not (g_path / ".git").exists():
        print(f"[!] 本地 Git 路径不存在: {g_path}")
        return False

    print(f"\n[+] 正在通过 git pull 更新 [{g_name}]...")
    code, out, err = run_cmd(["git", "pull", "--ff-only"], cwd=str(g_path))
    if code == 0:
        print(f"  [✅ 已更新] {g_name}: {out}")
        return True
    else:
        print(f"  [!] git pull 异常: {err}")
        return False

def do_update(registry, target_skill=None, do_sync=True):
    """执行完整的更新流程"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = BACKUP_DIR / f"pre_update_{timestamp}"

    print("=" * 68)
    print(f" [*] 开始执行技能更新 (自动快照备份至: .backup/{backup_root.name})")
    print("=" * 68)

    # 1. 更新 Bundle Repositories
    bundles = registry.get("bundle_repositories", {})
    for b_key, b_info in bundles.items():
        skills_in_bundle = list(b_info.get("skill_mapping", {}).keys()) or b_info.get("skills", [])
        if target_skill and target_skill not in skills_in_bundle:
            continue
        update_bundle_repo(b_key, b_info, registry, backup_root, target_skill)

    # 2. 更新 Single Repositories
    single_repos = registry.get("single_repositories", {})
    for s_name, s_info in single_repos.items():
        if target_skill and s_name != target_skill:
            continue
        update_single_repo(s_name, s_info, registry, backup_root)

    # 3. 更新 Git Managed
    git_skills = registry.get("git_managed_skills", {})
    for g_name, g_info in git_skills.items():
        if target_skill and g_name != target_skill:
            continue
        update_git_managed(g_name, g_info)

    # 保存最新 SHA 状态
    save_registry(registry)

    # 清理缓存
    if CACHE_DIR.exists():
        safe_rmtree(CACHE_DIR)

    print("\n" + "=" * 68)
    print(" [*] 所有选定技能已完成上游更新并安全备份！")
    print("=" * 68)

    # 4. 触发 sync.py 同步到 myskill-project 并更新中文文档
    if do_sync and SYNC_SCRIPT.exists():
        print("\n[*] 正在触发 sync.py 同步最新技能到 myskill-project 备份仓库...")
        code, out, err = run_cmd([sys.executable, str(SYNC_SCRIPT)])
        if code == 0:
            print("  [+] 已同步到 myskill-project 并重构最新中文 README.md！")
        else:
            print(f"  [!] sync.py 同步警告: {err}")

def main():
    parser = argparse.ArgumentParser(description="Agent Skills Upstream Auto-Updater")
    parser.add_argument("--check", action="store_true", help="仅检查是否有更新，不执行实际修改")
    parser.add_argument("--update", action="store_true", help="执行更新操作")
    parser.add_argument("--all", action="store_true", help="针对全部追踪的技能执行")
    parser.add_argument("--skill", type=str, default=None, help="针对指定单个技能执行")
    parser.add_argument("--sync", action="store_true", default=True, help="更新后自动同步到 myskill-project 备份")
    parser.add_argument("--no-sync", action="store_false", dest="sync", help="更新后不同步到备份")

    args = parser.parse_args()
    registry = load_registry()

    if args.check or (not args.update):
        check_updates(registry, target_skill=args.skill)
        if not args.update:
            print("\n[*] 提示：若要执行实际更新，请加上 --update 参数，或运行 update.bat 快速更新。")
            return

    if args.update:
        do_update(registry, target_skill=args.skill, do_sync=args.sync)

if __name__ == "__main__":
    main()
