#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Samsung Mall Trade-In (ShanHuiShou / 闪回收) Price Query Tool
Direct REST API client with built-in Canary Health-Check, Contract Verification,
dynamic series/model discovery, default watchlist support, and daily report archival.
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "https://p1-smz-api-cdn.shop.samsung.com.cn"
PROVIDER = "SHANHS"
DEFAULT_RENEW_SKU = "SM-A5760DBBCHC"
DEFAULT_RENEW_NAME = "Galaxy A57 5G"
DEFAULT_RENEW_PRICE = "4399"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WATCHLIST_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "assets", "watchlist.txt"))

# Thread-safe in-memory caches to speed up batch queries
_CACHE_LOCK = threading.Lock()
_CACHE_BRAND_SERIES: Dict[str, List[str]] = {}
_CACHE_SERIES_MODELS: Dict[str, List[Dict[str, Any]]] = {}
_CACHE_QUESTIONS: Dict[int, List[Dict[str, Any]]] = {}


def _http_get(url: str, timeout: int = 10) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_post(url: str, data: Dict[str, Any], timeout: int = 15) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_series_for_brand(brand_code: str) -> List[str]:
    """Dynamically fetch all series under a brand (thread-safe)."""
    with _CACHE_LOCK:
        if brand_code in _CACHE_BRAND_SERIES:
            return _CACHE_BRAND_SERIES[brand_code]

    url = f"{API_BASE}/tokocommercewebservices/v2/cn/tradeIn/services/filterDevicesV2?q=deviceType:1:brand:{brand_code}&mainProductCode={DEFAULT_RENEW_SKU}&provider={PROVIDER}"
    try:
        res = _http_get(url)
        series_codes = [str(item.get("code")) for item in res.get("children", []) if item.get("code")]
    except Exception:
        series_codes = ["27_SE", "26_SE", "25_SE"] if brand_code == "10" else []

    with _CACHE_LOCK:
        _CACHE_BRAND_SERIES[brand_code] = series_codes
    return series_codes


def _get_models_for_series(brand_code: str, series_code: str) -> List[Dict[str, Any]]:
    """Fetch all models under a specific brand & series (thread-safe)."""
    cache_key = f"{brand_code}_{series_code}"
    with _CACHE_LOCK:
        if cache_key in _CACHE_SERIES_MODELS:
            return _CACHE_SERIES_MODELS[cache_key]

    url = f"{API_BASE}/tokocommercewebservices/v2/cn/tradeIn/services/filterDevicesV2?q=deviceType:1:brand:{brand_code}:series:{series_code}&mainProductCode={DEFAULT_RENEW_SKU}&provider={PROVIDER}"
    try:
        res = _http_get(url)
        models = res.get("children", [])
    except Exception:
        models = []

    with _CACHE_LOCK:
        _CACHE_SERIES_MODELS[cache_key] = models
    return models


def find_model_code(brand_name: str, model_name: str) -> Optional[Tuple[int, str, float]]:
    """
    Search for a device model in the category/brand/series hierarchy using
    strict normalized matching (never falsely matching e.g. 'iPhone SE' to 'iPhone SE 3').
    Returns (phoneId, displayName, maxExchangeValue) if found, else None.
    """
    brand_code = "10" if ("苹果" in brand_name or "apple" in brand_name.lower() or "iphone" in model_name.lower()) else "20"
    series_list = _get_series_for_brand(brand_code)
    norm_target = re.sub(r'[\s\-_]', '', model_name.lower())

    for series in series_list:
        models = _get_models_for_series(brand_code, series)
        for item in models:
            disp = item.get("displayName", "")
            code = int(item.get("code", 0))
            max_val = float(item.get("maxExchangeValue") or 0.0)
            norm_disp = re.sub(r'[\s\-_]', '', disp.lower())
            if norm_target == norm_disp:
                return code, disp, max_val

    return None


def get_model_questions(phone_id: int) -> List[Dict[str, Any]]:
    """Fetch assessment question hierarchy for a given phone ID (thread-safe)."""
    with _CACHE_LOCK:
        if phone_id in _CACHE_QUESTIONS:
            return _CACHE_QUESTIONS[phone_id]

    url = f"{API_BASE}/tokocommercewebservices/v2/cn/servicesv2/assessment/TRADE_IN?q=code:{phone_id}&provider={PROVIDER}"
    res = _http_post(url, {"imei": ""})
    questions = res.get("questions", [])
    if not questions:
        raise ValueError(f"官方题目接口返回异常：机型 {phone_id} 未能获取到问答选项树，接口可能已调整！")

    with _CACHE_LOCK:
        _CACHE_QUESTIONS[phone_id] = questions
    return questions


def resolve_options(
    questions: List[Dict[str, Any]],
    submodel: str = "",
    storage: str = "",
    color: str = "",
    channel: str = "国行",
    warranty: str = "过保",
    condition: str = "完美",
) -> List[str]:
    """Select option codes for each question based on user criteria."""
    selected_codes = []

    for q in questions:
        title = q.get("title", "")
        multi = q.get("multichoice", False)
        answers = q.get("answers", [])

        if multi:
            continue

        chosen = None
        if title == "型号":
            if submodel:
                for a in answers:
                    if submodel.upper() in a.get("label", "").upper():
                        chosen = a
                        break
            if not chosen:
                chosen = answers[0]

        elif title == "内存":
            if storage:
                norm_storage = storage.upper().replace("GB", "G")
                for a in answers:
                    if a.get("label", "").upper().replace("GB", "G") == norm_storage:
                        chosen = a
                        break
            if not chosen:
                chosen = answers[0]

        elif title == "颜色":
            if color:
                norm_color = color.strip()
                for a in answers:
                    lbl = a.get("label", "")
                    if norm_color == lbl or norm_color in lbl:
                        chosen = a
                        break
            if not chosen:
                chosen = answers[0]

        elif title == "保修":
            if "在保" in warranty:
                for a in answers:
                    if "在保" in a.get("label", ""):
                        chosen = a
                        break
            else:
                for a in answers:
                    if "过保" in a.get("label", ""):
                        chosen = a
                        break
            if not chosen:
                chosen = answers[0]

        elif title == "购买渠道":
            for a in answers:
                if channel in a.get("label", ""):
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "开机":
            for a in answers:
                lbl = a.get("label", "")
                if ("能开机" in lbl or "正常开机" in lbl) and "不能" not in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "ID锁":
            for a in answers:
                lbl = a.get("label", "")
                if "无锁" in lbl or "已解锁" in lbl or "已退出" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "边框背板":
            for a in answers:
                lbl = a.get("label", "")
                if "完美" in lbl or "完好" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "摄像头镜片":
            for a in answers:
                lbl = a.get("label", "")
                if "正常" in lbl or "完好" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "机身弯曲情况":
            for a in answers:
                if "无弯曲" in a.get("label", ""):
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "屏幕外观":
            for a in answers:
                lbl = a.get("label", "")
                if "完美" in lbl or "完好" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "屏幕显示":
            for a in answers:
                lbl = a.get("label", "")
                if "完美" in lbl or "无瑕疵" in lbl or "正常" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "电池健康度":
            for a in answers:
                lbl = a.get("label", "")
                if "95%-100%" in lbl or ">90%" in lbl or "91%-100%" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "原装屏":
            for a in answers:
                lbl = a.get("label", "")
                if "无维修" in lbl or "原装" in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        elif title == "摄像头":
            for a in answers:
                lbl = a.get("label", "")
                if "正常" in lbl and "不正常" not in lbl:
                    chosen = a
                    break
            if not chosen:
                chosen = answers[0]

        else:
            chosen = answers[0]

        if chosen:
            selected_codes.append(chosen.get("code", ""))

    return selected_codes


def evaluate_price(phone_id: int, options: List[str]) -> Tuple[float, str, str, str]:
    """
    Submit options and receive evaluation quote.
    Returns (price_val, formatted_str, quote_hash, log_id).
    Raises ValueError if response contract is violated.
    """
    url = f"{API_BASE}/tokocommercewebservices/v2/cn/assessment/TRADE_IN/json"
    payload = {
        "productCode": str(phone_id),
        "selectionResponses": [
            {"key": "provider", "value": PROVIDER},
            {"key": "phoneId", "value": str(phone_id)},
            {"key": "options", "value": ",".join(options)},
            {"key": "renewPhoneSku", "value": DEFAULT_RENEW_SKU},
            {"key": "renewPhoneSkuName", "value": DEFAULT_RENEW_NAME},
            {"key": "renewPhoneSkuPrice", "value": DEFAULT_RENEW_PRICE},
            {"key": "isSupportSubsidy", "value": False},
        ],
    }
    res = _http_post(url, payload)

    error_msgs = res.get("result", {}).get("errorMessages", [])
    if error_msgs:
        raise ValueError(f"官方计价接口返回错误：{error_msgs}")

    entries = res.get("result", {}).get("additionalParameters", {}).get("entry", [])
    if not entries:
        raise ValueError("官方计价接口返回数据为空或结构变更！")

    entry_dict = {e["key"]: e["value"] for e in entries}

    price_str = entry_dict.get("price") or entry_dict.get("discountAmount")
    quote_hash = entry_dict.get("discountAmount-hash", "")
    log_id = entry_dict.get("logId", "")
    if not price_str or not quote_hash:
        raise ValueError(f"官方数据缺失关键签名或金额字段：entry_dict keys = {list(entry_dict.keys())}")

    price_val = float(price_str)
    formatted = entry_dict.get("discountAmountFormattervalue") or f"¥{int(price_val)}"
    return price_val, formatted, quote_hash, log_id


def verify_canary() -> Tuple[bool, str]:
    """
    Canary benchmark verification:
    Evaluates the known reference phone (iPhone 17 256G White) to verify
    that the backend pricing engine, network connection, and option mappings
    are 100% active and functioning normally.
    """
    try:
        found = find_model_code("苹果", "iPhone 17")
        if not found:
            return False, "金丝雀自检失败：未能在官方机型库中检索到 'iPhone 17'"
        phone_id, name, max_val = found
        qs = get_model_questions(phone_id)
        opts = resolve_options(qs, submodel="A3521", storage="256G", color="白色", channel="国行", warranty="过保", condition="完美")
        price, formatted, quote_hash, log_id = evaluate_price(phone_id, opts)

        if price <= 0:
            return False, f"金丝雀自检异常：基准估价为 0 元 ({formatted})"
        return True, f"金丝雀自检正常：iPhone 17 基准返回 {formatted} (logId: {log_id}, Hash: {quote_hash[:8]}...)"
    except Exception as e:
        return False, f"金丝雀自检发生异常：{e}"


def query_single_device(spec: Dict[str, str]) -> Dict[str, Any]:
    """Query a single device specification with full validation."""
    model_name = spec.get("model", "")
    submodel = spec.get("submodel", "")
    storage = spec.get("storage", "")
    channel = spec.get("channel", "国行")
    color = spec.get("color", "")
    warranty = spec.get("warranty", "过保")
    condition = spec.get("condition", "完美")

    found = find_model_code("苹果", model_name)
    if not found:
        return {
            **spec,
            "success": False,
            "unsupported": True,
            "error": "官方已下架/暂不支持回收",
            "price": 0.0,
            "formatted": "暂不支持/已下架",
            "hash": "",
        }

    phone_id, display_name, max_val = found
    try:
        questions = get_model_questions(phone_id)
        options = resolve_options(
            questions,
            submodel=submodel,
            storage=storage,
            color=color,
            channel=channel,
            warranty=warranty,
            condition=condition,
        )
        price_val, formatted, quote_hash, log_id = evaluate_price(phone_id, options)

        warning = ""
        if max_val > 0 and price_val > max_val * 1.05:
            warning = f"警告：估价 ({price_val}) 超过了官方标定最高上限 ({max_val})"

        return {
            **spec,
            "phone_id": phone_id,
            "matched_name": display_name,
            "success": True,
            "unsupported": False,
            "price": price_val,
            "max_reference": max_val,
            "formatted": formatted,
            "hash": quote_hash,
            "log_id": log_id,
            "warning": warning,
        }
    except Exception as e:
        return {
            **spec,
            "phone_id": phone_id,
            "matched_name": display_name,
            "success": False,
            "unsupported": False,
            "error": str(e),
            "price": 0.0,
            "formatted": "接口校验失败",
            "hash": "",
        }


def parse_raw_text(text: str, warranty: str = "过保", condition: str = "完美") -> List[Dict[str, str]]:
    """Parse tabular raw text into structured dicts."""
    items = []
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    for line in lines:
        parts = [p.strip() for p in re.split(r'[\t\s]{2,}|\t', line) if p.strip()]
        if len(parts) >= 3:
            model = parts[0]
            submodel = ""
            storage = ""
            channel = "国行"
            color = ""

            for p in parts[1:]:
                if re.match(r'^A\d{4}$', p, re.IGNORECASE):
                    submodel = p.upper()
                elif p == "其他型号":
                    submodel = p
                elif re.match(r'^\d+[GT]B?$', p, re.IGNORECASE):
                    storage = p.upper()
                elif p in ["国行", "港行", "美版", "非国行"]:
                    channel = p
                else:
                    color = p

            items.append({
                "model": model,
                "submodel": submodel,
                "storage": storage,
                "channel": channel,
                "color": color,
                "warranty": warranty,
                "condition": condition,
            })
    return items


def _sku_key(r: Dict[str, Any]) -> str:
    return f"{r.get('model','')}|{r.get('submodel','')}|{r.get('storage','')}|{r.get('channel','')}|{r.get('color','')}"


def compute_diffs_and_archive(results: List[Dict[str, Any]], save_dir: str, canary_msg: str) -> Tuple[List[Dict[str, Any]], str]:
    """Compare against previous run in save_dir/latest.json and save daily CSV + MD + JSON."""
    os.makedirs(save_dir, exist_ok=True)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    latest_path = os.path.join(save_dir, "latest.json")
    prev_map: Dict[str, float] = {}
    prev_date = ""
    if os.path.exists(latest_path):
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
                prev_date = prev_data.get("updated_at", "")
                for item in prev_data.get("results", []):
                    if item.get("success"):
                        prev_map[_sku_key(item)] = float(item.get("price", 0.0))
        except Exception:
            pass

    changed_count = 0
    for r in results:
        key = _sku_key(r)
        if r.get("success"):
            if key in prev_map:
                diff = r["price"] - prev_map[key]
                if diff > 0:
                    r["diff_str"] = f"🔺+{int(diff)}" if diff.is_integer() else f"🔺+{diff:.1f}"
                    changed_count += 1
                elif diff < 0:
                    r["diff_str"] = f"🔻{int(diff)}" if diff.is_integer() else f"🔻{diff:.1f}"
                    changed_count += 1
                else:
                    r["diff_str"] = "持平"
            else:
                r["diff_str"] = "首次记录" if not prev_map else "新增"
        else:
            r["diff_str"] = "-"

    # Save CSV (UTF-8 with BOM for Excel)
    csv_path = os.path.join(save_dir, f"samsung_tradein_{date_str}.csv")
    with open(csv_path, "w", encoding="utf-8-sig") as f:
        f.write("序号,机型,型号编码,内存,渠道,颜色,成色,保修,估价(元),较上次涨跌,验真Hash,状态,查询时间\n")
        for idx, r in enumerate(results, 1):
            price_num = int(r["price"]) if r.get("success") else ""
            status = "正常" if r.get("success") else r.get("error", "失败")
            f.write(
                f"{idx},{r.get('model')},{r.get('submodel')},{r.get('storage')},{r.get('channel')},{r.get('color')},"
                f"{r.get('condition','完美')},{r.get('warranty','过保')},{price_num},{r.get('diff_str','-')},{r.get('hash','')},{status},{now_str}\n"
            )

    # Save Markdown report
    md_lines = [
        f"# 三星商城（闪回收通道）每日回收估价日报 ({date_str})",
        "",
        f"- **查询时间**：{now_str}",
        f"- **健康检查**：{canary_msg}",
        f"- **对比基准**：{prev_date or '首次运行（无历史对比）'} | **价格变动机型数**：{changed_count} 款",
        "",
        "| 序号 | 机型 | 型号/编码 | 内存 | 渠道 | 颜色 | 今日估价 | 较上次变动 | 官方验真Hash |",
        "| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: |",
    ]
    for idx, r in enumerate(results, 1):
        model = r.get("model", "")
        sub = r.get("submodel", "-") or "-"
        storage = r.get("storage", "")
        channel = r.get("channel", "国行")
        color = r.get("color", "-") or "-"
        formatted = r.get("formatted", "¥0")
        diff_str = r.get("diff_str", "-")
        quote_hash = r.get("hash", "")
        hash_display = f"`{quote_hash[:8]}`" if quote_hash else "-"
        if r.get("unsupported"):
            md_lines.append(f"| {idx} | {model} | {sub} | {storage} | {channel} | {color} | *{formatted}* | - | - |")
        else:
            md_lines.append(f"| {idx} | **{model}** | {sub} | {storage} | {channel} | {color} | **{formatted}** | {diff_str} | {hash_display} |")

    md_path = os.path.join(save_dir, f"samsung_tradein_{date_str}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # Update latest.json
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump({"updated_at": now_str, "results": results}, f, ensure_ascii=False, indent=2)

    return results, f"已归档日报：{csv_path} 与 {md_path}（变动 {changed_count} 款）"


def main():
    parser = argparse.ArgumentParser(description="Query Samsung Mall Trade-In / ShanHuiShou Prices")
    parser.add_argument("--model", help="Device model name, e.g. 'iPhone 16e'")
    parser.add_argument("--submodel", default="", help="Submodel / A-code, e.g. 'A3410'")
    parser.add_argument("--storage", default="", help="Storage capacity, e.g. '256G'")
    parser.add_argument("--color", default="", help="Device color, e.g. '黑色'")
    parser.add_argument("--channel", default="国行", help="Purchase channel, default '国行'")
    parser.add_argument("--warranty", default="过保", help="Warranty status ('过保' or '在保'), default '过保'")
    parser.add_argument("--condition", default="完美", help="Condition preset, default '完美'")
    parser.add_argument("--batch-file", help="Path to text or JSON file with devices")
    parser.add_argument("--text", help="Raw multi-line text input")
    parser.add_argument("--watchlist", action="store_true", help="Query the saved default 40-model watchlist")
    parser.add_argument("--save-dir", help="Optional directory to save daily CSV/MD reports and compute price diffs")
    parser.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown", help="Output format")
    parser.add_argument("--concurrency", type=int, default=8, help="Number of concurrent query threads")
    parser.add_argument("--verify", action="store_true", help="Run canary baseline verification and exit")

    args = parser.parse_args()

    if args.verify:
        passed, msg = verify_canary()
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"[{status}] {msg}")
        sys.exit(0 if passed else 1)

    canary_ok, canary_msg = verify_canary()
    if not canary_ok:
        print(f"⚠️ [警告] 接口健康检查异常：{canary_msg}", file=sys.stderr)
        print("提示：官方后端接口或返回结构可能已调整，请谨慎采信以下结果！\n", file=sys.stderr)

    device_list: List[Dict[str, str]] = []

    if args.text:
        device_list = parse_raw_text(args.text, args.warranty, args.condition)
    elif args.batch_file:
        with open(args.batch_file, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip().startswith("[") or content.strip().startswith("{"):
                loaded = json.loads(content)
                device_list = loaded if isinstance(loaded, list) else [loaded]
            else:
                device_list = parse_raw_text(content, args.warranty, args.condition)
    elif args.model:
        device_list = [{
            "model": args.model,
            "submodel": args.submodel,
            "storage": args.storage,
            "channel": args.channel,
            "color": args.color,
            "warranty": args.warranty,
            "condition": args.condition,
        }]
    elif args.watchlist or os.path.exists(DEFAULT_WATCHLIST_PATH):
        with open(DEFAULT_WATCHLIST_PATH, "r", encoding="utf-8") as f:
            device_list = parse_raw_text(f.read(), args.warranty, args.condition)
    else:
        device_list = [
            {"model": "iPhone 17", "submodel": "A3521", "storage": "256G", "channel": "国行", "color": "白色", "warranty": "过保", "condition": "完美"}
        ]

    # Run queries concurrently (preserving original order via executor.map)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        results = list(executor.map(query_single_device, device_list))

    archive_msg = ""
    if args.save_dir:
        results, archive_msg = compute_diffs_and_archive(results, args.save_dir, canary_msg)

    # Format output
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print("序号,机型,型号编码,内存,渠道,颜色,估价,较上次变动,验真签名,上限参考,状态")
        for idx, r in enumerate(results, 1):
            status = "正常" if r.get("success") else r.get("error", "失败")
            print(f"{idx},{r.get('model')},{r.get('submodel')},{r.get('storage')},{r.get('channel')},{r.get('color')},{r.get('formatted')},{r.get('diff_str','-')},{r.get('hash')},{r.get('max_reference')},{status}")
    else:
        print(f"> 🔍 **官方接口健康检查**：{canary_msg}")
        if archive_msg:
            print(f"> 💾 **本地日报归档**：{archive_msg}")
        print("")
        has_diff = bool(args.save_dir)
        if has_diff:
            print("| 序号 | 机型 | 型号/编码 | 内存容量 | 购买渠道 | 外观颜色 | 估算价值 | 较上次变动 | 官方验真Hash |")
            print("| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: |")
        else:
            print("| 序号 | 机型 | 型号/编码 | 内存容量 | 购买渠道 | 外观颜色 | 估算价值 | 官方验真Hash |")
            print("| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :---: |")

        for idx, r in enumerate(results, 1):
            model = r.get("model", "")
            sub = r.get("submodel", "-") or "-"
            storage = r.get("storage", "")
            channel = r.get("channel", "国行")
            color = r.get("color", "-") or "-"
            formatted = r.get("formatted", "¥0")
            quote_hash = r.get("hash", "")
            hash_display = f"`{quote_hash[:8]}`" if quote_hash else "-"
            diff_str = r.get("diff_str", "-")

            if r.get("unsupported"):
                if has_diff:
                    print(f"| {idx} | {model} | {sub} | {storage} | {channel} | {color} | *{formatted}* | - | - |")
                else:
                    print(f"| {idx} | {model} | {sub} | {storage} | {channel} | {color} | *{formatted}* | - |")
            else:
                if has_diff:
                    print(f"| {idx} | **{model}** | {sub} | {storage} | {channel} | {color} | **{formatted}** | {diff_str} | {hash_display} |")
                else:
                    print(f"| {idx} | **{model}** | {sub} | {storage} | {channel} | {color} | **{formatted}** | {hash_display} |")


if __name__ == "__main__":
    main()
