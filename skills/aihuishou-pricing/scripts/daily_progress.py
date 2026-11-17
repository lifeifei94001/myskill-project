"""爱回收每日估价进度账本与断点续查工具。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
DEVICES_PATH = SKILL_DIR / "scripts" / "daily_devices.json"
SKU_CACHE_PATH = SKILL_DIR / "scripts" / "sku_cache.json"
DATA_DIR = SKILL_DIR / "data"


def item_key(item: dict[str, Any]) -> str:
    """生成与 sku_cache.json 一致的机型唯一键。"""
    channel = item.get("channel") or "国行"
    color = item.get("color") or "标准色"
    return f"{item['name']}|{item['capacity']}|{channel}|{color}"


def ledger_path_for(date_str: str) -> Path:
    """返回指定日期的账本文件路径。"""
    return DATA_DIR / f"quotes_{date_str}.json"


def load_ledger(date_str: str) -> dict[str, Any]:
    """读取指定日期的账本；不存在则返回空结构。"""
    path = ledger_path_for(date_str)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "date": date_str,
        "condition": "过保+完美（纯物品估价/不加券）",
        "quotes": {},
    }


def save_ledger(date_str: str, ledger: dict[str, Any]) -> Path:
    """持久化指定日期的报价账本。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = ledger_path_for(date_str)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def cmd_pending(date_str: str, limit: int | None) -> None:
    """输出当天尚未查询的剩余机型 JSON，方便直接注入批量脚本。"""
    devices: list[dict[str, Any]] = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))
    ledger = load_ledger(date_str)
    done_keys = set(ledger.get("quotes", {}).keys())
    pending = [d for d in devices if item_key(d) not in done_keys]
    if limit and limit > 0:
        pending = pending[:limit]
    output = {
        "date": date_str,
        "total": len(devices),
        "completed": len(done_keys),
        "remaining": len([d for d in devices if item_key(d) not in done_keys]),
        "items": pending,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_merge(date_str: str, input_file: str) -> None:
    """将浏览器脚本返回的 JSON 结果合并进当天账本，并自动回写新 SKU 缓存。"""
    raw = json.loads(Path(input_file).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "results" in raw:
        results = raw["results"]
    elif isinstance(raw, list):
        results = raw
    else:
        raise ValueError("输入文件格式必须是结果数组或包含 results 字段的对象")

    ledger = load_ledger(date_str)
    quotes = ledger.setdefault("quotes", {})
    sku_cache: dict[str, Any] = json.loads(SKU_CACHE_PATH.read_text(encoding="utf-8"))
    sku_updated = False
    added = 0

    for row in results:
        if row.get("error") or row.get("price") is None:
            continue
        key = item_key(row)
        quotes[key] = {
            "name": row["name"],
            "model": row.get("model", ""),
            "capacity": row["capacity"],
            "channel": row.get("channel") or "国行",
            "color": row.get("color") or "标准色",
            "matchedProductName": row.get("matchedProductName", ""),
            "price": row["price"],
            "inquiryKey": row.get("inquiryKey", ""),
        }
        added += 1
        if row.get("resolvedSku") and key not in sku_cache:
            sku_cache[key] = row["resolvedSku"]
            sku_updated = True

    saved_path = save_ledger(date_str, ledger)
    if sku_updated:
        SKU_CACHE_PATH.write_text(json.dumps(sku_cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "date": date_str,
                "addedOrUpdated": added,
                "totalCompleted": len(quotes),
                "skuCacheUpdated": sku_updated,
                "ledgerPath": str(saved_path),
            },
            ensure_ascii=False,
        )
    )


def cmd_report(date_str: str, compare_date: str | None) -> None:
    """按标准清单顺序输出 Markdown 报价表（可选对比前一日涨跌）。"""
    devices: list[dict[str, Any]] = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))
    ledger = load_ledger(date_str)
    quotes = ledger.get("quotes", {})
    prev_quotes = load_ledger(compare_date).get("quotes", {}) if compare_date else {}

    headers = ["序号", "机型", "型号", "容量", "渠道", "颜色", f"{date_str} 纯物品估价（元）"]
    if compare_date:
        headers.append(f"较 {compare_date} 涨跌")
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join([":---:" if i in (0, 6, 7) else ":---" for i in range(len(headers))]) + " |")

    for idx, dev in enumerate(devices, start=1):
        key = item_key(dev)
        entry = quotes.get(key)
        price_str = f"{entry['price']:,}" if entry and entry.get("price") is not None else "待查"
        row = [str(idx), dev["name"], dev.get("model", ""), dev["capacity"], dev["channel"], dev["color"], price_str]
        if compare_date:
            prev = prev_quotes.get(key)
            if entry and prev and entry.get("price") is not None and prev.get("price") is not None:
                diff = entry["price"] - prev["price"]
                diff_str = f"+{diff}" if diff > 0 else ("0" if diff == 0 else str(diff))
            else:
                diff_str = "-"
            row.append(diff_str)
        print("| " + " | ".join(row) + " |")


def main() -> None:
    parser = argparse.ArgumentParser(description="爱回收每日查价进度账本工具")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="查询日期 YYYY-MM-DD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pending = sub.add_parser("pending", help="输出当天尚未查询的机型")
    p_pending.add_argument("--limit", type=int, default=None, help="本次最多返回的机型数（如 4）")

    p_merge = sub.add_parser("merge", help="合并查询结果 JSON 到当天账本")
    p_merge.add_argument("--input", required=True, help="结果 JSON 文件路径")

    p_report = sub.add_parser("report", help="打印 Markdown 价格汇总表")
    p_report.add_argument("--compare", default=None, help="对比日期 YYYY-MM-DD")

    args = parser.parse_args()
    if args.command == "pending":
        cmd_pending(args.date, args.limit)
    elif args.command == "merge":
        cmd_merge(args.date, args.input)
    elif args.command == "report":
        cmd_report(args.date, args.compare)


if __name__ == "__main__":
    main()
