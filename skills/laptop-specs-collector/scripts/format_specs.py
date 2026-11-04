import re
import sys
import json
from typing import List, Dict, Any, Optional

def validate_date_ymd(date_str: str) -> bool:
    """Validate that date strictly follows YYYY年MM月DD日 or YYYY/MM/DD format down to the exact day."""
    if not date_str or date_str == '空':
        return False
    # Check YYYY年MM月DD日
    if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', date_str):
        return True
    # Check YYYY/MM/DD
    if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
        return True
    return False

def format_real_sku_table(rows: List[Dict[str, Any]]) -> str:
    """
    Format official real SKUs into the 8-column fixed markdown table:
    | 序号 | CPU | 运存（内存） | 显卡 | 固态硬盘（SSD） | 机械硬盘（HDD） | 屏幕尺寸 | 是否已下架 | 来源 |
    """
    headers = [
        "| 序号 | CPU | 运存（内存） | 显卡 | 固态硬盘（SSD） | 机械硬盘（HDD） | 屏幕尺寸 | 是否已下架 | 来源 |",
        "|:---:|:---|:---|:---|:---|:---|:---|:---:|:---|"
    ]
    lines = list(headers)
    for idx, row in enumerate(rows, 1):
        cpu = row.get("cpu", "空") or "空"
        ram = row.get("ram", "空") or "空"
        gpu = row.get("gpu", "空") or "空"
        ssd = row.get("ssd", "空") or "空"
        hdd = row.get("hdd", "空") or "空"
        screen = row.get("screen", "空") or "空"
        discontinued = row.get("is_discontinued", "否") or "否"
        source = row.get("source", "官方商城") or "官方商城"
        lines.append(f"| {idx} | {cpu} | {ram} | {gpu} | {ssd} | {hdd} | {screen} | {discontinued} | {source} |")
    return "\n".join(lines)

def format_release_info_table(release_info: List[Dict[str, str]]) -> str:
    """
    Format release time table:
    | 批次 | 发布日期 | 首销日期 | 版本差异说明 |
    """
    headers = [
        "| 批次 | 发布日期 | 首销日期 | 版本差异说明 |",
        "|:---|:---|:---|:---|"
    ]
    lines = list(headers)
    for info in release_info:
        batch = info.get("batch", "空") or "空"
        pub = info.get("publish_date", "空") or "空"
        sale = info.get("first_sale_date", "空") or "空"
        diff = info.get("version_diff", "空") or "空"
        lines.append(f"| {batch} | {pub} | {sale} | {diff} |")
    return "\n".join(lines)

def extract_dedup_attributes_from_skus(
    brand: str,
    alias: str,
    release_date: str,
    first_sale_date: str,
    skus: List[Dict[str, Any]]
) -> str:
    """
    Extract aggregated attributes strictly from the verified real SKUs without Cartesian hallucinations.
    """
    cpus, rams, gpus, ssds, hdds = [], [], [], [], []
    for s in skus:
        c = s.get("cpu", "").strip()
        r = s.get("ram", "").strip()
        g = s.get("gpu", "").strip()
        sd = s.get("ssd", "").strip()
        hd = s.get("hdd", "").strip()
        if c and c != "空" and c not in cpus:
            cpus.append(c)
        if r and r != "空" and r not in rams:
            rams.append(r)
        if g and g != "空" and g not in gpus:
            gpus.append(g)
        if sd and sd != "空" and sd not in ssds:
            ssds.append(sd)
        if hd and hd != "空" and hd not in hdds:
            hdds.append(hd)
        elif not hd or hd == "空":
            if "无" not in hdds:
                hdds.append("无")

    cpu_str = "、".join(cpus) if cpus else "空"
    ram_str = "、".join(rams) if rams else "空"
    gpu_str = "、".join(gpus) if gpus else "空"
    ssd_str = "、".join(ssds) if ssds else "空"
    hdd_str = "、".join(hdds) if hdds else "无"

    card = f"""════════════════════════════════════════════════════════════
【品牌名称】：{brand}
【机型别名】：{alias}
【发布时间】：{release_date}（首销：{first_sale_date}）
────────────────────────────────────────────────────────────
【处理器 CPU】 (顿号分隔)：
{cpu_str}

【运存内存】 (顿号分隔)：
{ram_str}

【显卡型号】 (顿号分隔)：
{gpu_str}

【固态硬盘】 (顿号分隔)：
{ssd_str}

【机械硬盘】 (顿号分隔)：
{hdd_str}
════════════════════════════════════════════════════════════
📊 官方真实在售组合总数：{len(skus)} 种独立 SKU（严格基于真实在售组合，拒绝虚假笛卡尔积）"""
    return card

if __name__ == "__main__":
    # Test example
    demo_skus = [
        {
            "cpu": "Intel Core Ultra 9 290HX Plus",
            "ram": "32GB DDR5 6400MHz",
            "gpu": "NVIDIA GeForce RTX 5070 12GB",
            "ssd": "1TB",
            "hdd": "空",
            "screen": "空",
            "is_discontinued": "否",
            "source": "联想官方商城"
        },
        {
            "cpu": "Intel Core Ultra 9 290HX Plus",
            "ram": "32GB DDR5 6400MHz",
            "gpu": "NVIDIA GeForce RTX 5080 16GB",
            "ssd": "2TB",
            "hdd": "空",
            "screen": "空",
            "is_discontinued": "否",
            "source": "联想官方商城"
        }
    ]
    print("=== 真实在售组合表格 ===")
    print(format_real_sku_table(demo_skus))
    print("\n=== 上市时间表格 ===")
    demo_release = [
        {"batch": "首发批次", "publish_date": "2026年05月19日", "first_sale_date": "2026年05月19日", "version_diff": "空"}
    ]
    print(format_release_info_table(demo_release))
    print("\n=== 逆向聚合录入卡 ===")
    print(extract_dedup_attributes_from_skus("联想", "拯救者 Y9000P 2026", "2026年05月19日", "2026年05月19日", demo_skus))
