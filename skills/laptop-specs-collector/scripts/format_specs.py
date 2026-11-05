import re
import sys
import json
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def validate_date_ymd(date_str: str) -> bool:
    """Validate that date strictly follows YYYY年MM月DD日 or YYYY/MM/DD format down to the exact day."""
    if not date_str or date_str == '空':
        return False
    if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', date_str):
        return True
    if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
        return True
    return False

def format_images_section(
    front_img: Dict[str, str],
    rear_img: Dict[str, str],
    color_scheme: str = "",
    gallery_url: str = ""
) -> str:
    """
    Format standard dual white-background images (Front + Rear/Side).
    front_img: {"url": str, "source": str, "title": str}
    rear_img: {"url": str, "source": str, "title": str}
    Ensures referrerpolicy='no-referrer' to prevent hotlink/403/whitelabel errors.
    Provides dual-rail fallback (direct image link + official gallery page).
    CRITICAL QUALITY CHECK:
    front_url and rear_url MUST NOT be identical!
    """
    front_title = front_img.get("title", "正视展开完整白底图")
    front_url = front_img.get("url", "")
    front_source = front_img.get("source", "品牌官方商城")

    rear_title = rear_img.get("title", "背面/斜侧展开完整白底图")
    rear_url = rear_img.get("url", "")
    rear_source = rear_img.get("source", "中关村在线 (ZOL)")

    color_header = f"（展示配色：{color_scheme}）" if color_scheme else ""
    gallery_link = f"[官方图库/商详情直达]({gallery_url})" if gallery_url else "[品牌官方专区](javascript:void(0))"

    front_img_html = f'<img src="{front_url}" referrerpolicy="no-referrer" width="280" alt="{front_title}" />' if front_url else "*(请直达官方图库查看)*"
    
    # Critical Check: Anti-duplicate perspective rule
    if rear_url and front_url and rear_url == front_url:
        # Detected identical front and rear URL! Block copy-paste and fall back to gallery inspection
        rear_img_html = f"*(需前往官方图库查看A面顶盖/背面展开专属视角，严禁重复展示正面图)*"
        rear_direct_link = "[查看官方图库背面分类]"
    else:
        rear_img_html = f'<img src="{rear_url}" referrerpolicy="no-referrer" width="280" alt="{rear_title}" />' if rear_url else "*(请直达官方图库查看)*"
        rear_direct_link = f"[点击查看原图]({rear_url})" if rear_url else "见官方图库"

    front_direct_link = f"[点击查看原图]({front_url})" if front_url else "见图库"

    md = f"""### 一、 官方标准白底建档图 {color_header}

| 视图类型 | 画面预览 | 来源渠道 | 高清图原链 | 官方图库直达 |
|:---:|:---:|:---:|:---|:---|
| **{front_title}** | {front_img_html} | {front_source} | {front_direct_link} | {gallery_link} |
| **{rear_title}** | {rear_img_html} | {rear_source} | {rear_direct_link} | {gallery_link} |

> **图片防盗链与视角质检说明**：
> 1. 已启用 `referrerpolicy="no-referrer"` 穿透防盗链限制，可在各主流浏览器直接预览；
> 2. **视角隔离红线**：图 1（B/C 面正视展开）与 图 2（A 面顶盖/斜侧 45° 视角）必须为两张完全独立的素材，严禁正反重复。"""
    return md

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
    skus: List[Dict[str, Any]],
    front_img_url: str = "",
    rear_img_url: str = "",
    gallery_url: str = ""
) -> str:
    """
    Extract aggregated attributes strictly from the verified real SKUs without Cartesian hallucinations.
    Includes建档白底图 links and gallery fallback for downstream 3C inventory systems.
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

    img_section = ""
    if front_img_url or rear_img_url or gallery_url:
        img_section = f"""【建档白底图】：
- 正视展开图：{front_img_url or '见官方图库'}
- 背面斜侧图：{rear_img_url if rear_img_url != front_img_url else '见官方图库背面专区'}
- 官方图库直达：{gallery_url or '空'}
────────────────────────────────────────────────────────────\n"""

    card = f"""════════════════════════════════════════════════════════════
【品牌名称】：{brand}
【机型别名】：{alias}
【发布时间】：{release_date}（首销：{first_sale_date}）
────────────────────────────────────────────────────────────
{img_section}【处理器 CPU】 (顿号分隔)：
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
【数据统计】：官方真实在售组合总数 {len(skus)} 种独立 SKU（严格基于真实在售组合，拒绝虚假笛卡尔积）"""
    return card

if __name__ == "__main__":
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
        }
    ]
    front = {"url": "https://2b.zol-img.com.cn/product/275_800x600/415/ceLTP4WNBlRg.jpg", "source": "中关村在线", "title": "正视展开完整白底图"}
    rear = {"url": "https://2b.zol-img.com.cn/product/275_800x600/415/diff_rear.jpg", "source": "中关村在线", "title": "背面/斜侧展开完整白底图"}
    gallery = "https://detail.zol.com.cn/picture/index1257900.shtml"
    
    print(format_images_section(front, rear, "冰魄白", gallery))
