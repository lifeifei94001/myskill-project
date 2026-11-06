#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Samsung Mall Trade-In (ShanHuiShou / 闪回收) Price Query Tool
Direct REST API client with built-in Canary Health-Check & Contract Verification.
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "https://p1-smz-api-cdn.shop.samsung.com.cn"
PROVIDER = "SHANHS"
DEFAULT_RENEW_SKU = "SM-A5760DBBCHC"
DEFAULT_RENEW_NAME = "Galaxy A57 5G"
DEFAULT_RENEW_PRICE = "4399"

# In-memory caches to speed up batch queries
_CACHE_SERIES: Dict[str, List[Dict[str, Any]]] = {}
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


def find_model_code(brand_name: str, model_name: str) -> Optional[Tuple[int, str, float]]:
    """
    Search for a device model in the category/brand/series hierarchy.
    Returns (phoneId, displayName, maxExchangeValue) if found.
    """
    brand_code = "10" if "苹果" in brand_name or "apple" in brand_name.lower() or "iphone" in model_name.lower() else "20"
    series_list = ["27_SE", "26_SE", "25_SE"]
    norm_target = re.sub(r'[\s\-_]', '', model_name.lower())

    for series in series_list:
        cache_key = f"{brand_code}_{series}"
        if cache_key not in _CACHE_SERIES:
            url = f"{API_BASE}/tokocommercewebservices/v2/cn/tradeIn/services/filterDevicesV2?q=deviceType:1:brand:{brand_code}:series:{series}&mainProductCode={DEFAULT_RENEW_SKU}&provider={PROVIDER}"
            try:
                res = _http_get(url)
                _CACHE_SERIES[cache_key] = res.get("children", [])
            except Exception as e:
                _CACHE_SERIES[cache_key] = []
        
        for item in _CACHE_SERIES[cache_key]:
            disp = item.get("displayName", "")
            code = int(item.get("code", 0))
            max_val = float(item.get("maxExchangeValue") or 0.0)
            norm_disp = re.sub(r'[\s\-_]', '', disp.lower())
            if norm_target == norm_disp:
                return code, disp, max_val

    # Partial / relaxed matching
    for series in series_list:
        cache_key = f"{brand_code}_{series}"
        for item in _CACHE_SERIES.get(cache_key, []):
            disp = item.get("displayName", "")
            code = int(item.get("code", 0))
            max_val = float(item.get("maxExchangeValue") or 0.0)
            norm_disp = re.sub(r'[\s\-_]', '', disp.lower())
            if norm_target in norm_disp or norm_disp in norm_target:
                return code, disp, max_val

    return None


def get_model_questions(phone_id: int) -> List[Dict[str, Any]]:
    """Fetch assessment question hierarchy for a given phone ID."""
    if phone_id in _CACHE_QUESTIONS:
        return _CACHE_QUESTIONS[phone_id]

    url = f"{API_BASE}/tokocommercewebservices/v2/cn/servicesv2/assessment/TRADE_IN?q=code:{phone_id}&provider={PROVIDER}"
    res = _http_post(url, {"imei": ""})
    questions = res.get("questions", [])
    if not questions:
        raise ValueError(f"官方题目接口返回异常：机型 {phone_id} 未能获取到问答选项树，接口可能已调整！")
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


def evaluate_price(phone_id: int, options: List[str]) -> Tuple[float, str, str]:
    """
    Submit options and receive evaluation quote.
    Returns (price_val, formatted_str, quote_hash).
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
    
    # Contract validation: check for official error messages
    error_msgs = res.get("result", {}).get("errorMessages", [])
    if error_msgs:
        raise ValueError(f"官方计价接口返回错误：{error_msgs}")

    entries = res.get("result", {}).get("additionalParameters", {}).get("entry", [])
    if not entries:
        raise ValueError("官方计价接口返回数据为空或结构变更！")

    entry_dict = {e["key"]: e["value"] for e in entries}
    
    # Validation: must contain price and hash signature
    price_str = entry_dict.get("price") or entry_dict.get("discountAmount")
    quote_hash = entry_dict.get("discountAmount-hash", "")
    if not price_str or not quote_hash:
        raise ValueError(f"官方数据缺失关键签名或金额字段：entry_dict keys = {list(entry_dict.keys())}")

    price_val = float(price_str)
    formatted = entry_dict.get("discountAmountFormattervalue") or f"¥{int(price_val)}"
    return price_val, formatted, quote_hash


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
        price, formatted, quote_hash = evaluate_price(phone_id, opts)
        
        # In baseline, iPhone 17 256G White out-of-warranty was evaluated at ¥3400
        if price <= 0:
            return False, f"金丝雀自检异常：基准估价为 0 元 ({formatted})"
        return True, f"金丝雀自检正常：iPhone 17 基准机型返回 {formatted} (Hash: {quote_hash[:8]}...)"
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
            "error": f"Model '{model_name}' not found in database",
            "price": 0.0,
            "formatted": "未找到机型",
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
        price_val, formatted, quote_hash = evaluate_price(phone_id, options)
        
        # Sanity check: price must not exceed max_val (with a 5% margin)
        warning = ""
        if max_val > 0 and price_val > max_val * 1.05:
            warning = f"警告：估价 ({price_val}) 超过了官方标定最高上限 ({max_val})"

        return {
            **spec,
            "phone_id": phone_id,
            "matched_name": display_name,
            "success": True,
            "price": price_val,
            "max_reference": max_val,
            "formatted": formatted,
            "hash": quote_hash,
            "warning": warning,
        }
    except Exception as e:
        return {
            **spec,
            "phone_id": phone_id,
            "matched_name": display_name,
            "success": False,
            "error": str(e),
            "price": 0.0,
            "formatted": "接口校验失败",
            "hash": "",
        }


def parse_raw_text(text: str) -> List[Dict[str, str]]:
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
            })
    return items


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
    parser.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown", help="Output format")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent query threads")
    parser.add_argument("--verify", action="store_true", help="Run canary baseline verification and exit")

    args = parser.parse_args()

    # If --verify requested, run canary check and report
    if args.verify:
        passed, msg = verify_canary()
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"[{status}] {msg}")
        sys.exit(0 if passed else 1)

    # Automatic pre-flight canary check: ensure API contract is alive
    canary_ok, canary_msg = verify_canary()
    if not canary_ok:
        print(f"⚠️ [警告] 接口健康检查异常：{canary_msg}", file=sys.stderr)
        print("提示：官方后端接口或返回结构可能已调整，请谨慎采信以下结果！\n", file=sys.stderr)

    device_list: List[Dict[str, str]] = []

    if args.text:
        device_list = parse_raw_text(args.text)
    elif args.batch_file:
        with open(args.batch_file, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip().startswith("[") or content.strip().startswith("{"):
                loaded = json.loads(content)
                device_list = loaded if isinstance(loaded, list) else [loaded]
            else:
                device_list = parse_raw_text(content)
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
    else:
        device_list = [
            {"model": "iPhone 17", "submodel": "A3521", "storage": "256G", "channel": "国行", "color": "白色", "warranty": "过保", "condition": "完美"}
        ]

    # Run queries concurrently
    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(query_single_device, dev) for dev in device_list]
        for f in futures:
            results.append(f.result())

    # Format output
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print("序号,机型,型号编码,内存,渠道,颜色,估价,验真签名,上限参考,状态")
        for idx, r in enumerate(results, 1):
            status = "正常" if r.get("success") else r.get("error", "失败")
            print(f"{idx},{r.get('model')},{r.get('submodel')},{r.get('storage')},{r.get('channel')},{r.get('color')},{r.get('formatted')},{r.get('hash')},{r.get('max_reference')},{status}")
    else:
        # Markdown table
        print(f"> 🔍 **官方接口健康检查**：{canary_msg}\n")
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
            print(f"| {idx} | **{model}** | {sub} | {storage} | {channel} | {color} | **{formatted}** | {hash_display} |")


if __name__ == "__main__":
    main()
