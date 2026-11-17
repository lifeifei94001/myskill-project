"""探测爱回收微信小程序搜索结果页与问卷页的实时 UIA 结构。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

OUT_SEARCH = Path(r"d:\APP\development_projects\_wx_search_probe.json")


def resolve_agent_desktop() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        exe = Path(appdata) / "npm" / "node_modules" / "agent-desktop" / "bin" / "agent-desktop-win32-x64.exe"
        if exe.exists():
            return str(exe)
    found = shutil.which("agent-desktop.exe") or shutil.which("agent-desktop.cmd") or shutil.which("agent-desktop")
    if found:
        return found
    raise FileNotFoundError("未找到 agent-desktop 可执行文件")


AD = resolve_agent_desktop()


def run_ad(*args: str) -> dict[str, Any]:
    proc = subprocess.run(
        [AD, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError(f"agent-desktop {' '.join(args)} 无输出: {proc.stderr!r}")
    return json.loads(raw)


def get_ahs_window() -> dict[str, Any]:
    resp = run_ad("list-windows")
    for w in resp.get("data") or []:
        if w.get("app_name") == "WeChatAppEx.exe" and "爱回收" in (w.get("title") or ""):
            return w
    raise RuntimeError("未找到爱回收小程序窗口")


def snap_window(wid: str) -> dict[str, Any]:
    return run_ad(
        "snapshot",
        "--window-id",
        wid,
        "--compact",
        "--include-bounds",
        "--timeout-ms",
        "20000",
        "--max-depth",
        "40",
    )


def find_by_native_id(node: dict[str, Any], target: str) -> dict[str, Any] | None:
    if (node.get("native_id") or {}).get("value") == target:
        return node
    for ch in node.get("children") or []:
        found = find_by_native_id(ch, target)
        if found:
            return found
    return None


def active_page(tree: dict[str, Any]) -> dict[str, Any]:
    ps = find_by_native_id(tree, "page_stack")
    if not ps or not ps.get("children"):
        return tree
    return ps["children"][-1]


def find_first(node: dict[str, Any], pred) -> dict[str, Any] | None:
    if pred(node):
        return node
    for ch in node.get("children") or []:
        found = find_first(ch, pred)
        if found:
            return found
    return None


def center_xy(node: dict[str, Any]) -> str:
    b = node["bounds"]
    cx = int(round(b["x"] + b["width"] / 2))
    cy = int(round(b["y"] + b["height"] / 2))
    return f"{cx},{cy}"


def click_node(node: dict[str, Any]) -> None:
    xy = center_xy(node)
    res = run_ad("--headed", "mouse-click", "--xy", xy)
    if not res.get("ok"):
        raise RuntimeError(f"点击坐标 {xy} 失败: {res}")


def dump_visible(node: dict[str, Any], lines: list[str], depth: int = 0) -> None:
    st = node.get("states") or []
    if "offscreen" in st:
        return
    nid = (node.get("native_id") or {}).get("value", "")
    name = node.get("name", "")
    val = node.get("value", "")
    ref = node.get("ref_id", "")
    b = node.get("bounds") or {}
    if name or (val and not str(val).startswith("https://")) or ref or nid:
        lines.append(
            f"{'  ' * min(depth, 8)}[{node.get('role')}] ref={ref} id={nid} "
            f"name={name!r} val={val if not str(val).startswith('https://') else 'URL'!r} "
            f"b=({int(b.get('x', 0))},{int(b.get('y', 0))},{int(b.get('width', 0))}x{int(b.get('height', 0))})"
        )
    for ch in node.get("children") or []:
        dump_visible(ch, lines, depth + 1)


def main() -> int:
    win = get_ahs_window()
    wid = win["id"]
    if win.get("minimized"):
        run_ad("restore", "--window-id", wid)
    run_ad("focus-window", "--window-id", wid)

    # 1. 回到搜索页
    for _ in range(5):
        snap = snap_window(wid)
        page = active_page(snap["data"]["tree"])
        pid = (page.get("native_id") or {}).get("value", "")
        search_node = find_by_native_id(page, "search")
        print(f"当前顶层页面: {pid}, has_search={search_node is not None}")
        if search_node is not None:
            break
        # 若在首页(index-b-header)，点搜索框进入搜索页；否则点左上角返回(\ue012)
        home_hdr = find_by_native_id(page, "index-b-header")
        if home_hdr is not None:
            lb = find_first(home_hdr, lambda n: n.get("role") == "listbox")
            if lb:
                click_node(lb)
                time.sleep(1.0)
                continue
        back = find_first(page, lambda n: n.get("name") == "\ue012" and "offscreen" not in (n.get("states") or []))
        if not back:
            raise RuntimeError(f"在页面 {pid} 上既未找到 search 也未找到返回按钮")
        click_node(back)
        time.sleep(0.8)

    # 2. 在搜索页输入 "iPhone 17e"
    snap = snap_window(wid)
    page = active_page(snap["data"]["tree"])
    tf = find_first(page, lambda n: n.get("role") == "textfield" and "offscreen" not in (n.get("states") or []))
    if not tf:
        raise RuntimeError("搜索页未找到 textfield")

    click_node(tf)
    time.sleep(0.3)
    run_ad("--headed", "press", "ctrl+a")
    run_ad("--headed", "press", "delete")
    run_ad("clipboard-set", "iPhone 17e")
    run_ad("--headed", "press", "ctrl+v")
    time.sleep(0.5)
    run_ad("--headed", "press", "return")
    time.sleep(2.0)

    # 3. 抓取搜索结果页快照
    snap2 = snap_window(wid)
    OUT_SEARCH.write_text(json.dumps(snap2, ensure_ascii=False, indent=2), encoding="utf-8")
    page2 = active_page(snap2["data"]["tree"])
    lines: list[str] = []
    dump_visible(page2, lines)
    print(f"搜索后顶层页面={((page2.get('native_id') or {}).get('value'))} visible_nodes={len(lines)}")
    for line in lines[:80]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
