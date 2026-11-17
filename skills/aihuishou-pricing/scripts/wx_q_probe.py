"""确保搜索并点击苹果 iPhone 17e，抓取问卷页初始 UIA 结构。"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

OUT_Q = Path(r"d:\APP\development_projects\_wx_q_probe.json")


def resolve_agent_desktop() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        exe = Path(appdata) / "npm" / "node_modules" / "agent-desktop" / "bin" / "agent-desktop-win32-x64.exe"
        if exe.exists():
            return str(exe)
    found = shutil.which("agent-desktop.exe") or shutil.which("agent-desktop.cmd") or shutil.which("agent-desktop")
    if found:
        return found
    raise FileNotFoundError("未找到 agent-desktop")


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
    return json.loads(proc.stdout.strip())


def get_ahs_window() -> dict[str, Any]:
    for w in run_ad("list-windows").get("data") or []:
        if w.get("app_name") == "WeChatAppEx.exe" and "爱回收" in (w.get("title") or ""):
            return w
    raise RuntimeError("未找到爱回收窗口")


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
        r = find_by_native_id(ch, target)
        if r:
            return r
    return None


def find_first(node: dict[str, Any], pred) -> dict[str, Any] | None:
    if pred(node):
        return node
    for ch in node.get("children") or []:
        r = find_first(ch, pred)
        if r:
            return r
    return None


def active_page(tree: dict[str, Any]) -> dict[str, Any]:
    ps = find_by_native_id(tree, "page_stack")
    return ps["children"][-1] if ps and ps.get("children") else tree


def collect_static_nodes(node: dict[str, Any]) -> list[dict[str, Any]]:
    res: list[dict[str, Any]] = []
    if node.get("role") == "statictext" and node.get("name"):
        res.append(node)
    for ch in node.get("children") or []:
        res.extend(collect_static_nodes(ch))
    return res


def compact_text(s: str) -> str:
    return re.sub(r"\s+", "", s).strip().lower()


def find_search_card(page: dict[str, Any], target_title: str) -> dict[str, Any] | None:
    target_compact = compact_text(target_title)
    candidates: list[dict[str, Any]] = []

    def walk(node: dict[str, Any]) -> None:
        if "offscreen" in (node.get("states") or []):
            return
        b = node.get("bounds") or {}
        if 50 <= b.get("height", 0) <= 120 and b.get("width", 0) >= 300:
            snodes = collect_static_nodes(node)
            cat = next((n for n in snodes if "手机" in n["name"] and "苹果" in n["name"]), None)
            if cat:
                cat_y = (cat.get("bounds") or {}).get("y", 999999)
                max_title_x = b["x"] + b["width"] * 0.70
                title_parts = [
                    n["name"]
                    for n in snodes
                    if (n.get("bounds") or {}).get("y", 999999) < cat_y - 5
                    and (n.get("bounds") or {}).get("x", 999999) < max_title_x
                ]
                if compact_text("".join(title_parts)) == target_compact:
                    candidates.append(node)
        for ch in node.get("children") or []:
            walk(ch)

    walk(page)
    if not candidates:
        return None
    candidates.sort(key=lambda n: n["bounds"]["width"] * n["bounds"]["height"])
    return candidates[0]


def click_node(node: dict[str, Any]) -> None:
    b = node["bounds"]
    xy = f"{int(round(b['x'] + b['width'] / 2))},{int(round(b['y'] + b['height'] / 2))}"
    res = run_ad("--headed", "mouse-click", "--xy", xy)
    if not res.get("ok"):
        raise RuntimeError(f"点击失败 {xy}: {res}")


def dump_visible(node: dict[str, Any], lines: list[str], depth: int = 0) -> None:
    if "offscreen" in (node.get("states") or []):
        return
    nid = (node.get("native_id") or {}).get("value", "")
    name = node.get("name", "")
    ref = node.get("ref_id", "")
    b = node.get("bounds") or {}
    if name or ref or nid.startswith(("question_", "group_", "page-")):
        lines.append(
            f"{'  ' * min(depth, 6)}[{node.get('role')}] ref={ref} id={nid} name={name!r} "
            f"b=({int(b.get('x', 0))},{int(b.get('y', 0))},{int(b.get('width', 0))}x{int(b.get('height', 0))})"
        )
    for ch in node.get("children") or []:
        dump_visible(ch, lines, depth + 1)


def ensure_search_page(wid: str) -> dict[str, Any]:
    for _ in range(5):
        snap = snap_window(wid)
        page = active_page(snap["data"]["tree"])
        if find_by_native_id(page, "search") is not None:
            return page
        home_hdr = find_by_native_id(page, "index-b-header")
        if home_hdr is not None:
            lb = find_first(home_hdr, lambda n: n.get("role") == "listbox")
            if lb:
                click_node(lb)
                time.sleep(1.0)
                continue
        back = find_first(page, lambda n: n.get("name") == "\ue012" and "offscreen" not in (n.get("states") or []))
        if not back:
            raise RuntimeError("无法返回搜索页")
        click_node(back)
        time.sleep(0.8)
    raise RuntimeError("多次返回仍未到达搜索页")


def main() -> int:
    win = get_ahs_window()
    wid = win["id"]
    if win.get("minimized"):
        run_ad("restore", "--window-id", wid)
    run_ad("focus-window", "--window-id", wid)

    snap = snap_window(wid)
    page = active_page(snap["data"]["tree"])
    card = find_search_card(page, "苹果 iPhone 17e")
    if not card:
        page = ensure_search_page(wid)
        tf = find_first(page, lambda n: n.get("role") == "textfield" and "offscreen" not in (n.get("states") or []))
        if not tf:
            raise RuntimeError("搜索页未找到 textfield")
        click_node(tf)
        time.sleep(0.3)
        run_ad("--headed", "press", "ctrl+a")
        run_ad("--headed", "press", "delete")
        run_ad("clipboard-set", "iPhone 17e")
        run_ad("--headed", "press", "ctrl+v")
        time.sleep(0.4)
        run_ad("--headed", "press", "return")
        time.sleep(2.0)
        snap = snap_window(wid)
        page = active_page(snap["data"]["tree"])
        card = find_search_card(page, "苹果 iPhone 17e")
        if not card:
            raise RuntimeError("搜索后仍未找到 '苹果 iPhone 17e'")

    click_node(card)
    time.sleep(2.5)

    snap2 = snap_window(wid)
    OUT_Q.write_text(json.dumps(snap2, ensure_ascii=False, indent=2), encoding="utf-8")
    page2 = active_page(snap2["data"]["tree"])
    lines: list[str] = []
    dump_visible(page2, lines)
    print(f"当前顶层页面={(page2.get('native_id') or {}).get('value')} visible_nodes={len(lines)}")
    for line in lines[:80]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
