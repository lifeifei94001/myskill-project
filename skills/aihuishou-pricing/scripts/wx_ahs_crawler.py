"""通过 agent-desktop 驱动 PC 微信小程序“爱回收”每日采集 18 个 SKU 纯物品估价（过保+完美，不加券）。"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
DEVICES_PATH = SKILL_DIR / "scripts" / "daily_devices.json"
DATA_DIR = SKILL_DIR / "data"
LOG_DIR = SKILL_DIR / "logs"

# 每题“过保+完美”匹配规则（按题目关键字顺序匹配选项正则）
OPTION_RULES: list[tuple[list[str], list[str], str]] = [
    (["使用情况"], [r"^正常进入桌面$"], "使用情况"),
    (["电池"], [r"电池原装且健康度高", r"原装.*健康度高", r"≥\s*9\d%", r"90%.*以上", r"85.*以上"], "电池健康完美"),
    (["边框", "背板", "外壳", "成色"], [r"外壳完美无瑕疵", r"外壳无瑕疵", r"完美无瑕疵", r"无瑕疵或轻微划痕", r"外观完好", r"几乎全新"], "外壳完美"),
    (["屏幕外观"], [r"屏幕完美无划痕", r"屏幕完美或轻微划痕", r"屏幕完美", r"无划痕"], "屏幕外观完美"),
    (["屏幕显示"], [r"显示完美", r"显示完好", r"显示正常"], "屏幕显示完美"),
    (["摄像头", "拍照"], [r"无维修更换", r"拍照正常", r"功能正常"], "摄像头完美"),
    (["整机维修", "受潮", "拆机", "拆修"], [r"无维修无受潮无拆机", r"无维修.*无拆", r"无拆修"], "无维修受潮拆机"),
    (["保修"], [r"已过保", r"过保", r"不足\s*1\s*个月", r"无保修"], "过保"),
]


def resolve_agent_desktop() -> str:
    """解析 agent-desktop 原生可执行文件路径。"""
    appdata = os.environ.get("APPDATA")
    if appdata:
        exe = Path(appdata) / "npm" / "node_modules" / "agent-desktop" / "bin" / "agent-desktop-win32-x64.exe"
        if exe.exists():
            return str(exe)
    found = shutil.which("agent-desktop.exe") or shutil.which("agent-desktop.cmd") or shutil.which("agent-desktop")
    if found:
        return found
    raise FileNotFoundError("未找到 agent-desktop，请先确认已全局安装。")


AD = resolve_agent_desktop()


def item_key(item: dict[str, Any]) -> str:
    """生成与 daily_progress.py 一致的机型唯一键。"""
    channel = item.get("channel") or "国行"
    color = item.get("color") or "标准色"
    return f"{item['name']}|{item['capacity']}|{channel}|{color}"


def run_ad(*args: str, check: bool = True) -> dict[str, Any]:
    """以 UTF-8 直接调用 agent-desktop 并解析返回的 JSON envelope。"""
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
        raise RuntimeError(f"agent-desktop {' '.join(args)} 无输出: stderr={proc.stderr!r}")
    data = json.loads(raw)
    if check and not data.get("ok"):
        raise RuntimeError(f"agent-desktop {' '.join(args)} 失败: {data}")
    return data


def get_ahs_window() -> dict[str, Any]:
    """定位 WeChatAppEx.exe 的“爱回收”窗口。"""
    resp = run_ad("list-windows")
    for w in resp.get("data") or []:
        if w.get("app_name") == "WeChatAppEx.exe" and "爱回收" in (w.get("title") or ""):
            return w
    raise RuntimeError("未找到“爱回收”微信小程序窗口，请先在 PC 微信中打开爱回收小程序。")


def ensure_foreground(wid: str) -> dict[str, Any]:
    """若最小化则还原，并将“爱回收”窗口置为前台焦点。"""
    win = get_ahs_window()
    if win.get("minimized"):
        run_ad("restore", "--window-id", wid)
        time.sleep(0.4)
    run_ad("focus-window", "--window-id", wid)
    time.sleep(0.2)
    return get_ahs_window()


def snap_window(wid: str, timeout_ms: int = 20000) -> dict[str, Any]:
    """抓取完整 UIA 树（含坐标）。"""
    return run_ad(
        "snapshot",
        "--window-id",
        wid,
        "--compact",
        "--include-bounds",
        "--timeout-ms",
        str(timeout_ms),
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


def find_all(node: dict[str, Any], pred) -> list[dict[str, Any]]:
    res: list[dict[str, Any]] = []
    if pred(node):
        res.append(node)
    for ch in node.get("children") or []:
        res.extend(find_all(ch, pred))
    return res


def find_first(node: dict[str, Any], pred) -> dict[str, Any] | None:
    if pred(node):
        return node
    for ch in node.get("children") or []:
        r = find_first(ch, pred)
        if r:
            return r
    return None


def active_page(tree: dict[str, Any]) -> dict[str, Any]:
    """page_stack 的最后一个子节点即当前可见顶层页面。"""
    ps = find_by_native_id(tree, "page_stack")
    return ps["children"][-1] if ps and ps.get("children") else tree


def collect_static_nodes(node: dict[str, Any], include_offscreen: bool = False) -> list[dict[str, Any]]:
    if not include_offscreen and "offscreen" in (node.get("states") or []):
        return []
    res: list[dict[str, Any]] = []
    if node.get("role") == "statictext" and node.get("name"):
        res.append(node)
    for ch in node.get("children") or []:
        res.extend(collect_static_nodes(ch, include_offscreen=include_offscreen))
    return res


def compact_text(s: str) -> str:
    return re.sub(r"\s+", "", s).strip().lower()


def click_bounds(bounds: dict[str, Any], x_ratio: float = 0.5) -> None:
    cx = int(round(bounds["x"] + bounds["width"] * x_ratio))
    cy = int(round(bounds["y"] + bounds["height"] / 2))
    run_ad("--headed", "mouse-click", "--xy", f"{cx},{cy}")


def scroll_page(page_bounds: dict[str, Any], lines: int) -> None:
    cx = int(round(page_bounds["x"] + page_bounds["width"] / 2))
    cy = int(round(page_bounds["y"] + page_bounds["height"] * 0.55))
    run_ad("--headed", "mouse-wheel", "--x", str(cx), "--y", str(cy), "--dy", str(lines))


def navigate_to_search(wid: str) -> dict[str, Any]:
    """从任意页面退回或进入搜索页（带 search 节点的页面）。"""
    for _ in range(8):
        snap = snap_window(wid)
        page = active_page(snap["data"]["tree"])
        if find_by_native_id(page, "search") is not None:
            return page
        home_hdr = find_by_native_id(page, "index-b-header")
        if home_hdr is not None:
            lb = find_first(home_hdr, lambda n: n.get("role") == "listbox")
            if lb:
                click_bounds(lb["bounds"])
                time.sleep(1.0)
                continue
        back = find_first(
            page,
            lambda n: n.get("name") == "\ue012" and "offscreen" not in (n.get("states") or []),
        )
        if not back:
            raise RuntimeError("当前页面既无 search 也无返回按钮 \\ue012")
        click_bounds(back["bounds"])
        time.sleep(0.9)
    raise RuntimeError("多次返回仍未能到达搜索页")


def find_search_card(page: dict[str, Any], target_title: str) -> dict[str, Any] | None:
    """在搜索结果中精确匹配机型卡片（排除右侧新人价文本）。"""
    target_compact = compact_text(target_title)
    candidates: list[dict[str, Any]] = []

    def walk(node: dict[str, Any]) -> None:
        if "offscreen" in (node.get("states") or []):
            return
        b = node.get("bounds") or {}
        if 50 <= b.get("height", 0) <= 130 and b.get("width", 0) >= 300:
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


def is_target_questionnaire_page(page: dict[str, Any], target_title: str) -> bool:
    """判断当前页面是否已经是目标机型的问卷页。"""
    has_q = find_first(
        page,
        lambda n: ((n.get("native_id") or {}).get("value") or "").startswith("question_"),
    )
    if not has_q:
        return False
    target_compact = compact_text(target_title)
    for n in collect_static_nodes(page, include_offscreen=False):
        if compact_text(n["name"]) == target_compact:
            return True
    return False


def search_and_enter_device(wid: str, device_name: str) -> None:
    """在搜索页输入机型并点进对应估价问卷页。"""
    ensure_foreground(wid)
    page = navigate_to_search(wid)
    search_box = find_by_native_id(page, "search")
    tf = find_first(page, lambda n: n.get("role") == "textfield" and "offscreen" not in (n.get("states") or []))
    if not tf:
        raise RuntimeError("搜索页未找到 textfield")

    # 若输入框内已有内容且右侧存在清除按钮(×)，先点击清除
    if (tf.get("value") or "").strip() and search_box:
        tf_right = tf["bounds"]["x"] + tf["bounds"]["width"]
        clear_btn = find_first(
            search_box,
            lambda n: n.get("role") == "group"
            and 15 <= (n.get("bounds") or {}).get("width", 0) <= 50
            and (n.get("bounds") or {}).get("x", 0) >= tf_right - 5,
        )
        if clear_btn:
            click_bounds(clear_btn["bounds"])
            time.sleep(0.3)

    click_bounds(tf["bounds"])
    time.sleep(0.25)
    run_ad("--headed", "press", "ctrl+a")
    time.sleep(0.1)
    run_ad("--headed", "press", "delete")
    time.sleep(0.15)
    run_ad("clipboard-set", device_name)
    time.sleep(0.1)
    run_ad("--headed", "press", "ctrl+v")
    time.sleep(0.5)
    run_ad("--headed", "press", "return")

    target_title = f"苹果 {device_name}"
    last_snap = None
    for attempt in range(9):
        time.sleep(0.9)
        last_snap = snap_window(wid)
        page = active_page(last_snap["data"]["tree"])
        if is_target_questionnaire_page(page, target_title):
            return
        # 若回车误跳到了别的机型问卷页，退回搜索页
        if find_first(page, lambda n: ((n.get("native_id") or {}).get("value") or "").startswith("question_")):
            page = navigate_to_search(wid)
            continue
        card = find_search_card(page, target_title)
        if card:
            click_bounds(card["bounds"])
            time.sleep(1.8)
            return
        # 若列表多结果可能被折叠到下方，第3次与第6次尝试向下滚屏找精确卡片
        if attempt in (2, 5):
            pb = page.get("bounds") or {"x": 1400, "y": 150, "width": 414, "height": 797}
            scroll_page(pb, lines=-5)

    if last_snap:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / "debug_search_fail.json").write_text(
            json.dumps(last_snap, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        texts = [n["name"] for n in collect_static_nodes(active_page(last_snap["data"]["tree"]))]
        raise RuntimeError(f"搜索后未找到精确卡片: {target_title} | 当前可见文本={texts[:20]}")
    raise RuntimeError(f"搜索后未找到精确卡片: {target_title}")


def extract_question_blocks(page: dict[str, Any]) -> list[dict[str, Any]]:
    """提取问卷页上的所有 question_* 块，解析标题、已选值与选项列表。"""
    qnodes = find_all(
        page,
        lambda n: ((n.get("native_id") or {}).get("value") or "").startswith("question_"),
    )
    blocks: list[dict[str, Any]] = []
    for q in qnodes:
        nid = (q.get("native_id") or {}).get("value", "")
        children = q.get("children") or []
        if not children:
            continue
        header_node = children[0]
        header_texts = [n["name"] for n in collect_static_nodes(header_node, include_offscreen=True)]
        q_title = ""
        selected_val = ""
        if len(header_texts) >= 2 and re.match(r"^\d+\.", header_texts[0].strip()):
            q_title = header_texts[1].strip()
            selected_val = "".join(t for t in header_texts[2:] if t != "\ue01a").strip()
        elif header_texts:
            q_title = header_texts[0].strip()
            selected_val = "".join(t for t in header_texts[1:] if t != "\ue01a").strip()

        options: list[dict[str, Any]] = []
        if len(children) >= 2:
            opt_container = children[1]
            for opt_node in opt_container.get("children") or []:
                opt_texts = [n["name"] for n in collect_static_nodes(opt_node, include_offscreen=True)]
                if opt_texts:
                    options.append(
                        {
                            "label": opt_texts[0].strip(),
                            "all_text": " | ".join(opt_texts),
                            "bounds": opt_node.get("bounds") or {},
                            "offscreen": "offscreen" in (opt_node.get("states") or []),
                        }
                    )

        blocks.append(
            {
                "id": nid,
                "title": q_title,
                "selected": selected_val,
                "options": options,
                "bounds": q.get("bounds") or {},
                "offscreen": "offscreen" in (q.get("states") or []),
            }
        )
    return blocks


def match_patterns_for_question(title: str, device: dict[str, Any]) -> tuple[list[str], str] | None:
    """返回指定题目的目标选项正则列表与说明。"""
    if "存储容量" in title or "容量" in title:
        cap = re.escape(device["capacity"])
        return [rf"^{cap}$", cap], f"存储容量={device['capacity']}"

    if "购买渠道" in title or "渠道" in title or "版本" in title:
        ch = device.get("channel") or "国行"
        pats = [r"大陆国行", r"国行"] if ch == "国行" else [re.escape(ch)]
        return pats, f"渠道={ch}"

    if "颜色" in title:
        color = device.get("color") or ""
        if not color:
            return None
        return [rf"^{re.escape(color)}$", re.escape(color)], f"颜色={color}"

    if "型号" in title and device.get("model"):
        m = re.escape(device["model"])
        return [m, r"全网通", r"公开版"], f"型号={device['model']}"

    for title_keys, patterns, desc in OPTION_RULES:
        if any(k in title for k in title_keys):
            return patterns, desc

    return None


def is_selected_value_ok(title: str, selected: str, device: dict[str, Any]) -> bool:
    """校验收起态汇总行中已选值是否符合目标 SKU 与过保+完美条件。"""
    if not selected:
        return False
    rule = match_patterns_for_question(title, device)
    if rule is None:
        return True
    patterns, _ = rule
    return any(re.search(pat, selected, re.IGNORECASE) for pat in patterns)


def choose_option_for_question(
    title: str, options: list[dict[str, Any]], device: dict[str, Any]
) -> tuple[dict[str, Any] | None, str]:
    """根据 SKU 参数与“过保+完美”规则选择唯一目标选项。"""
    if "功能" in title:
        return None, "功能情况无需勾选"

    rule = match_patterns_for_question(title, device)
    if rule is None:
        return None, f"未识别题目({title}): {[o['label'] for o in options]}"

    patterns, desc = rule
    for pat in patterns:
        for opt in options:
            if re.search(pat, opt["label"], re.IGNORECASE):
                return opt, desc
    return None, desc


def extract_quote_result(page: dict[str, Any]) -> dict[str, Any] | None:
    """从结果页提取“物品估价”（纯底价，不加券）及总价。"""
    snodes = collect_static_nodes(page, include_offscreen=False)
    base_label = next((n for n in snodes if n["name"].strip() == "物品估价"), None)
    if not base_label:
        return None

    lb = base_label["bounds"]
    num_candidates = []
    for n in snodes:
        txt = n["name"].strip().replace(",", "")
        if not re.fullmatch(r"\d+", txt):
            continue
        nb = n["bounds"]
        if lb["y"] - 48 <= nb["y"] < lb["y"] and abs(nb["x"] - lb["x"]) <= 60:
            num_candidates.append((abs(nb["x"] - lb["x"]), int(txt)))
    if not num_candidates:
        return None
    num_candidates.sort(key=lambda t: t[0])
    base_price = num_candidates[0][1]

    total_price = None
    rpv = find_by_native_id(page, "recycle-price-view")
    if rpv:
        for n in collect_static_nodes(rpv, include_offscreen=False):
            t = n["name"].strip().replace(",", "")
            if re.fullmatch(r"\d+", t):
                total_price = int(t)
                break

    model_title = ""
    for n in snodes:
        if n["name"].startswith("苹果 "):
            model_title = n["name"].strip()
            break

    return {
        "base_price": base_price,
        "total_with_coupon": total_price,
        "page_model_title": model_title,
    }


def scroll_into_view_and_click(
    wid: str, target_bounds: dict[str, Any], page_bounds: dict[str, Any], offscreen: bool
) -> bool:
    """若目标不在安全可视区域内（避开顶部155px导航与底部135px预约条）则滚动并重抓快照，否则点击。"""
    min_y = page_bounds["y"] + 155
    max_y = page_bounds["y"] + page_bounds["height"] - 135
    cy = target_bounds["y"] + target_bounds["height"] / 2
    if cy < min_y or target_bounds["y"] < page_bounds["y"] + 125:
        scroll_page(page_bounds, lines=5)
        time.sleep(0.45)
        return False
    if offscreen or cy > max_y or target_bounds["y"] + target_bounds["height"] > page_bounds["y"] + page_bounds["height"] - 115:
        scroll_page(page_bounds, lines=-5)
        time.sleep(0.45)
        return False
    # 宽卡片偏右点击(0.6)，避开左侧“回收说明”悬浮图标
    x_ratio = 0.6 if target_bounds.get("width", 0) >= 200 else 0.5
    click_bounds(target_bounds, x_ratio=x_ratio)
    return True


def complete_questionnaire_and_read_price(
    wid: str, device: dict[str, Any], verbose: bool = True
) -> dict[str, Any]:
    """逐步作答或校验汇总问卷（过保+完美）并提交读取纯物品估价。"""
    answered_log: list[dict[str, Any]] = []
    seen_steps = 0
    last_snap = None

    while seen_steps < 40:
        seen_steps += 1
        snap = snap_window(wid)
        last_snap = snap
        page = active_page(snap["data"]["tree"])
        page_bounds = page.get("bounds") or {"x": 1400, "y": 150, "width": 414, "height": 797}

        # 1. 检查是否已到达估价结果页
        quote = extract_quote_result(page)
        if quote is not None:
            # 稍微等待数字滚动动画稳定
            if quote["total_with_coupon"] is not None and quote["total_with_coupon"] < quote["base_price"]:
                time.sleep(0.8)
                snap2 = snap_window(wid)
                quote2 = extract_quote_result(active_page(snap2["data"]["tree"]))
                if quote2:
                    quote = quote2
            if verbose:
                print(f"  [结果页] {quote}")
            return {**quote, "answered": answered_log}

        blocks = extract_question_blocks(page)
        expanded = [b for b in blocks if b["options"] and "功能" not in b["title"]]

        # 2. 有展开的单选题：选出目标项
        if expanded:
            q = expanded[-1]
            opt, reason = choose_option_for_question(q["title"], q["options"], device)
            if verbose:
                print(
                    f"  [题目] {q['title']} | 选项={[o['label'] for o in q['options']]} "
                    f"-> 选择={opt['label'] if opt else None} ({reason})"
                )
            if opt is None:
                raise RuntimeError(
                    f"无法自动匹配题目 {q['title']!r}，可选={[o['label'] for o in q['options']]}"
                )

            if scroll_into_view_and_click(wid, opt["bounds"], page_bounds, opt["offscreen"]):
                answered_log.append({"title": q["title"], "selected": opt["label"]})
                time.sleep(0.65)
            continue

        # 3. 无展开题时，先检查所有已收起汇总行是否全部符合目标 SKU（防历史缓存容量/成色错配）
        mismatch = next(
            (
                b
                for b in blocks
                if "功能" not in b["title"] and not is_selected_value_ok(b["title"], b["selected"], device)
            ),
            None,
        )
        if mismatch is not None:
            if verbose:
                print(f"  [修正汇总项] {mismatch['title']} 当前={mismatch['selected']!r}，点击重新选择")
            if scroll_into_view_and_click(wid, mismatch["bounds"], page_bounds, mismatch["offscreen"]):
                time.sleep(0.7)
            continue

        # 4. 所有汇总项均已匹配且无展开题，点击“马上估价”
        submit_btn = find_first(
            page,
            lambda n: n.get("role") == "button"
            and n.get("name") == "马上估价"
            and "offscreen" not in (n.get("states") or []),
        )
        if submit_btn:
            if verbose:
                print("  [提交] 点击 马上估价")
            if submit_btn.get("ref_id") and "Click" in (submit_btn.get("available_actions") or []):
                run_ad("click", submit_btn["ref_id"])
            else:
                click_bounds(submit_btn["bounds"])
            time.sleep(2.2)
            continue

        scroll_page(page_bounds, lines=-5)
        time.sleep(0.7)

    if last_snap:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / "debug_q_fail.json").write_text(
            json.dumps(last_snap, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    raise RuntimeError(f"超过最大步数仍未完成估价: {device['name']}")


def try_re_evaluate_on_result_page(wid: str) -> bool:
    """在结果页点击“重新估价”，快速返回当前机型的汇总问卷页（用于同机型多容量切换）。"""
    snap = snap_window(wid)
    page = active_page(snap["data"]["tree"])
    btn = find_first(
        page,
        lambda n: n.get("role") == "statictext"
        and n.get("name") == "重新估价"
        and "offscreen" not in (n.get("states") or []),
    )
    if not btn:
        return False
    click_bounds(btn["bounds"])
    time.sleep(1.2)
    snap2 = snap_window(wid)
    page2 = active_page(snap2["data"]["tree"])
    return bool(find_first(page2, lambda n: ((n.get("native_id") or {}).get("value") or "").startswith("question_")))


def load_wx_ledger(date_str: str) -> dict[str, Any]:
    path = DATA_DIR / f"wx_quotes_{date_str}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "date": date_str,
        "source": "微信小程序（爱回收）",
        "condition": "过保+完美（纯物品估价/不加券）",
        "quotes": {},
    }


def save_wx_ledger(date_str: str, ledger: dict[str, Any]) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"wx_quotes_{date_str}.json"
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def merge_into_main_ledger(date_str: str, wx_quotes: dict[str, Any]) -> Path:
    """把微信小程序价格合并进 daily_progress.py 使用的 quotes_YYYY-MM-DD.json。"""
    main_path = DATA_DIR / f"quotes_{date_str}.json"
    if main_path.exists():
        main_ledger = json.loads(main_path.read_text(encoding="utf-8"))
    else:
        main_ledger = {
            "date": date_str,
            "condition": "过保+完美（纯物品估价/不加券）",
            "quotes": {},
        }
    quotes = main_ledger.setdefault("quotes", {})
    for k, v in wx_quotes.items():
        quotes[k] = {
            "name": v["name"],
            "model": v.get("model", ""),
            "capacity": v["capacity"],
            "channel": v.get("channel") or "国行",
            "color": v.get("color") or "标准色",
            "matchedProductName": v.get("matchedProductName", ""),
            "price": v["price"],
            "inquiryKey": v.get("inquiryKey", ""),
        }
    main_path.write_text(json.dumps(main_ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return main_path


def export_csv(date_str: str, devices: list[dict[str, Any]], quotes: dict[str, Any]) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / f"wx_quotes_{date_str}.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "机型", "型号", "容量", "渠道", "颜色", "物品估价(纯底价)", "含券展示价", "采集时间"])
        for idx, dev in enumerate(devices, start=1):
            entry = quotes.get(item_key(dev)) or {}
            writer.writerow(
                [
                    idx,
                    dev["name"],
                    dev.get("model", ""),
                    dev["capacity"],
                    dev["channel"],
                    dev["color"],
                    entry.get("price", ""),
                    entry.get("totalWithCoupon", ""),
                    entry.get("capturedAt", ""),
                ]
            )
    return csv_path


def print_report(date_str: str, devices: list[dict[str, Any]], quotes: dict[str, Any], compare_date: str | None) -> None:
    prev_quotes: dict[str, Any] = {}
    if compare_date:
        for cand in [DATA_DIR / f"wx_quotes_{compare_date}.json", DATA_DIR / f"quotes_{compare_date}.json"]:
            if cand.exists():
                prev_quotes = json.loads(cand.read_text(encoding="utf-8")).get("quotes", {})
                break

    headers = ["序号", "机型", "型号", "容量", "渠道", "颜色", f"{date_str} 物品估价（元）"]
    if prev_quotes:
        headers.append(f"较 {compare_date} 涨跌")
    print("\n| " + " | ".join(headers) + " |")
    print("| " + " | ".join([":---:" if i in (0, 6, 7) else ":---" for i in range(len(headers))]) + " |")

    for idx, dev in enumerate(devices, start=1):
        key = item_key(dev)
        entry = quotes.get(key)
        price_str = f"{entry['price']:,}" if entry and entry.get("price") is not None else "待查"
        row = [str(idx), dev["name"], dev.get("model", ""), dev["capacity"], dev["channel"], dev["color"], price_str]
        if prev_quotes:
            prev = prev_quotes.get(key)
            if entry and prev and entry.get("price") is not None and prev.get("price") is not None:
                diff = entry["price"] - prev["price"]
                diff_str = f"+{diff}" if diff > 0 else ("0" if diff == 0 else str(diff))
            else:
                diff_str = "-"
            row.append(diff_str)
        print("| " + " | ".join(row) + " |")


def main() -> int:
    parser = argparse.ArgumentParser(description="微信小程序爱回收爬虫（agent-desktop）")
    parser.add_argument("--test-one", action="store_true", help="仅测试第 1 个机型 iPhone 17e")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="账本日期 YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="忽略当日已采集缓存，全部重新爬取")
    parser.add_argument("--only", default="", help="仅采集名称包含该字符串的 SKU（如 'iPhone 15'）")
    parser.add_argument("--merge-ledger", action="store_true", help="同时合并进 daily_progress.py 的 quotes_YYYY-MM-DD.json")
    parser.add_argument("--compare", default="", help="对比历史日期 YYYY-MM-DD（默认自动查找昨日文件）")
    args = parser.parse_args()

    all_devices: list[dict[str, Any]] = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))
    target_devices = all_devices[:1] if args.test_one else all_devices
    if args.only:
        target_devices = [d for d in target_devices if args.only.lower() in d["name"].lower()]

    ledger = load_wx_ledger(args.date)
    quotes = ledger.setdefault("quotes", {})

    pending = [d for d in target_devices if args.force or item_key(d) not in quotes]
    print(f"日期={args.date} 目标={len(target_devices)} 已完成={len(target_devices) - len(pending)} 待采={len(pending)}")

    if pending:
        win = get_ahs_window()
        wid = win["id"]
        ensure_foreground(wid)

        prev_dev: dict[str, Any] | None = None
        for idx, dev in enumerate(pending, start=1):
            print(f"[{idx}/{len(pending)}] 开始查询: {dev['name']} {dev['capacity']} {dev['channel']} {dev['color']}")
            reused = False
            if (
                prev_dev is not None
                and prev_dev["name"] == dev["name"]
                and prev_dev.get("channel") == dev.get("channel")
                and prev_dev.get("color") == dev.get("color")
            ):
                reused = try_re_evaluate_on_result_page(wid)
                if reused:
                    print("  [复用] 同机型点击“重新估价”切换容量")

            if not reused:
                search_and_enter_device(wid, dev["name"])

            res = complete_questionnaire_and_read_price(wid, dev, verbose=True)
            k = item_key(dev)
            quotes[k] = {
                "name": dev["name"],
                "model": dev.get("model", ""),
                "capacity": dev["capacity"],
                "channel": dev.get("channel") or "国行",
                "color": dev.get("color") or "标准色",
                "matchedProductName": res["page_model_title"],
                "price": res["base_price"],
                "totalWithCoupon": res["total_with_coupon"],
                "inquiryKey": f"wx_{dt.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "capturedAt": dt.datetime.now().isoformat(timespec="seconds"),
            }
            saved_path = save_wx_ledger(args.date, ledger)
            prev_dev = dev
            print(f"  => 纯物品估价: ¥{quotes[k]['price']} (已落盘 {saved_path.name})")

    csv_path = export_csv(args.date, all_devices, quotes)
    print(f"\nCSV 已导出: {csv_path}")

    if args.merge_ledger:
        main_path = merge_into_main_ledger(args.date, quotes)
        print(f"已同步合并主账本: {main_path}")

    compare_date = args.compare or (dt.date.fromisoformat(args.date) - dt.timedelta(days=1)).isoformat()
    print_report(args.date, all_devices, quotes, compare_date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
