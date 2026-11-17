"""爱回收微信小程序 UIA 树诊断探针（规避 PowerShell 5.1 管道编码乱码）。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

OUT_PATH = Path(r"d:\APP\development_projects\_wx_probe_clean.json")


def resolve_agent_desktop() -> str:
    """解析 agent-desktop 可执行文件路径（优先原生 exe，回退 PATH 中的 cmd/exe）。"""
    appdata = os.environ.get("APPDATA")
    if appdata:
        exe = Path(appdata) / "npm" / "node_modules" / "agent-desktop" / "bin" / "agent-desktop-win32-x64.exe"
        if exe.exists():
            return str(exe)
    found = shutil.which("agent-desktop.exe") or shutil.which("agent-desktop.cmd") or shutil.which("agent-desktop")
    if found:
        return found
    raise FileNotFoundError("未找到 agent-desktop 可执行文件，请确认已全局安装 agent-desktop。")


AGENT_DESKTOP_BIN = resolve_agent_desktop()


def run_ad(*args: str) -> dict[str, Any]:
    """以 UTF-8 直接调用 agent-desktop 并解析 JSON。"""
    proc = subprocess.run(
        [AGENT_DESKTOP_BIN, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError(f"agent-desktop {' '.join(args)} 无输出，stderr={proc.stderr!r}")
    return json.loads(raw)


def find_ahs_window() -> dict[str, Any]:
    """查找“爱回收”微信小程序窗口。"""
    resp = run_ad("list-windows")
    if not resp.get("ok"):
        raise RuntimeError(f"list-windows 失败: {resp}")
    for win in resp["data"]:
        if win.get("app_name") == "WeChatAppEx.exe" and "爱回收" in (win.get("title") or ""):
            return win
    raise RuntimeError("未找到 WeChatAppEx.exe 的“爱回收”窗口，请先在 PC 微信中打开爱回收小程序。")


def summarize_pages(node: dict[str, Any], out: list[str], depth: int = 0) -> None:
    """提取带 name/value/automation_id/ref_id 的关键节点。"""
    nid = (node.get("native_id") or {}).get("value", "")
    name = node.get("name", "")
    val = node.get("value", "")
    ref = node.get("ref_id", "")
    role = node.get("role", "")
    cc = node.get("children_count")
    states = node.get("states") or []
    bounds = node.get("bounds") or {}
    interesting = bool(
        name
        or val
        or ref
        or nid.startswith(("page-", "question_", "group_", "search", "recycle", "Order", "order"))
    )
    if interesting and "offscreen" not in states:
        indent = "  " * min(depth, 10)
        parts = [f"{indent}[{role}]"]
        if ref:
            parts.append(ref)
        if nid:
            parts.append(f"id={nid}")
        if name:
            parts.append(f"name={name!r}")
        if val and val != name:
            parts.append(f"val={val!r}")
        if cc is not None:
            parts.append(f"children_count={cc}")
        if bounds:
            parts.append(
                f"@({int(bounds.get('x', 0))},{int(bounds.get('y', 0))},"
                f"{int(bounds.get('width', 0))}x{int(bounds.get('height', 0))})"
            )
        out.append(" ".join(parts))
    for ch in node.get("children") or []:
        summarize_pages(ch, out, depth + 1)


def main() -> int:
    win = find_ahs_window()
    wid = win["id"]
    if win.get("minimized"):
        run_ad("restore", "--window-id", wid)

    snap = run_ad(
        "snapshot",
        "--window-id",
        wid,
        "--compact",
        "--include-bounds",
        "--timeout-ms",
        "30000",
        "--max-depth",
        "40",
    )
    OUT_PATH.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")

    data = snap.get("data") or {}
    print(
        f"ok={snap.get('ok')} complete={data.get('complete')} "
        f"truncated={data.get('truncated')} ref_count={data.get('ref_count')}"
    )
    lines: list[str] = []
    if data.get("tree"):
        summarize_pages(data["tree"], lines)
    print(f"visible_key_nodes={len(lines)} saved_to={OUT_PATH}")
    for line in lines[:80]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
