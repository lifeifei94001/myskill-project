import os
import shutil
import stat
from pathlib import Path
from datetime import datetime
from generate_chinese_readme import generate_chinese_readme

def on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        pass

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
    src_folder_names = {p.name for p in skill_folders}
    ignore_patterns = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".DS_Store", "node_modules")

    # Prune skills no longer present in source
    for dest_folder in SKILLS_DEST.iterdir():
        if dest_folder.is_dir() and dest_folder.name not in src_folder_names:
            shutil.rmtree(dest_folder, onerror=on_rm_error)
            print(f"  [-] Pruned removed skill: {dest_folder.name}")

    for src_folder in sorted(skill_folders, key=lambda x: x.name.lower()):
        dest_folder = SKILLS_DEST / src_folder.name
        
        # Copy directory tree
        if dest_folder.exists():
            shutil.rmtree(dest_folder, onerror=on_rm_error)
        shutil.copytree(src_folder, dest_folder, ignore=ignore_patterns)

    print(f"[*] Successfully copied {len(skill_folders)} skills.")

    # 3. Generate detailed Chinese README.md
    generate_chinese_readme()

if __name__ == "__main__":
    sync_skills()
