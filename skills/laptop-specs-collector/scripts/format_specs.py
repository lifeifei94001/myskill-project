import re
import sys
import json
from typing import List, Dict, Any, Optional

def normalize_cpu(cpu_str: str) -> str:
    s = cpu_str.strip()
    # Remove leading Intel / AMD / Core prefixes
    s = re.sub(r'(?i)\bintel\b\s*', '', s)
    s = re.sub(r'(?i)\bcore\b\s*', '', s)
    s = re.sub(r'(?i)\bamd\b\s*', '', s)
    s = re.sub(r'(?i)\bryzen\b\s*', '', s)
    s = re.sub(r'(?i)^酷睿\s*', '', s)
    s = re.sub(r'(?i)^锐龙\s*', 'R', s)
    # i9 14900HX -> i9-14900HX
    s = re.sub(r'(?i)\b(i[3579])\s*[-_]?\s*([0-9]{4,5}[A-Z]*)', r'\1-\2', s)
    # R7 7840H -> R7-7840H
    s = re.sub(r'(?i)\b(R[3579])\s*[-_]?\s*([0-9]{4}[A-Z]*)', r'\1-\2', s)
    # Ultra 7 155H
    s = re.sub(r'(?i)\bultra\b', 'Ultra', s)
    return s.strip()

def normalize_gpu(gpu_str: str) -> str:
    s = gpu_str.strip()
    s = re.sub(r'(?i)\bnvidia\b\s*', '', s)
    s = re.sub(r'(?i)\bgeforce\b\s*', '', s)
    s = re.sub(r'(?i)\s*(laptop\s*gpu|移动版|笔记本电脑gpu|独立显卡|独显)', '', s)
    s = re.sub(r'(?i)rtx\s*([0-9]{4}[a-z]*)', r'RTX\1', s)
    s = re.sub(r'(?i)gtx\s*([0-9]{4}[a-z]*)', r'GTX\1', s)
    if any(k in s.lower() for k in ['核显', '集显', '集成', 'intel iris', 'amd radeon graphics', 'uhd', '集成显卡']):
        return '集显'
    return s.strip()

def normalize_storage(cap_str: str) -> str:
    s = cap_str.strip().upper()
    s = s.replace('GB', 'G').replace(' ', '')
    if s == '1024G':
        return '1TB'
    if s == '2048G':
        return '2TB'
    return s

def clean_and_join(items: List[str], normalizer=None) -> str:
    cleaned = []
    for item in items:
        # Split only by comma, pause, semicolon, or newline (NOT spaces within CPU/GPU names)
        tokens = re.split(r'[,，、;\n]+', str(item).strip())
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if normalizer:
                t = normalizer(t)
            if t and t not in cleaned:
                cleaned.append(t)
    return '、'.join(cleaned)

def format_laptop_record(
    brand: str,
    alias: str,
    release_date: str,
    cpus: List[str],
    gpus: List[str],
    ssds: List[str],
    hdds: Optional[List[str]] = None
) -> Dict[str, Any]:
    cpu_str = clean_and_join(cpus, normalize_cpu)
    gpu_str = clean_and_join(gpus, normalize_gpu)
    ssd_str = clean_and_join(ssds, normalize_storage)
    
    if not hdds or hdds == ['无'] or hdds == ['none']:
        hdd_str = '无'
    else:
        hdd_str = clean_and_join(hdds, normalize_storage)
        if not hdd_str:
            hdd_str = '无'

    # Date normalization: 2024年1月 -> 2024/01/01
    date_clean = release_date.strip().replace('年', '/').replace('月', '/').replace('日', '').replace('-', '/')
    date_clean = re.sub(r'/+$', '', date_clean)

    # Compute combination count
    c_count = len(cpu_str.split('、')) if cpu_str else 0
    g_count = len(gpu_str.split('、')) if gpu_str else 0
    s_count = len(ssd_str.split('、')) if ssd_str else 0
    h_count = len(hdd_str.split('、')) if hdd_str else 0
    combo_count = c_count * g_count * s_count * h_count

    return {
        "brand": brand,
        "alias": alias,
        "release_date": date_clean,
        "cpu_raw": cpu_str,
        "gpu_raw": gpu_str,
        "ssd_raw": ssd_str,
        "hdd_raw": hdd_str,
        "combo_count": combo_count
    }

if __name__ == "__main__":
    # Test example
    demo = format_laptop_record(
        brand="联想",
        alias="拯救者Y9000P 2024",
        release_date="2024/01/17",
        cpus=["Intel Core i9 14900HX", "i7-14650HX"],
        gpus=["NVIDIA GeForce RTX 4060 Laptop", "RTX 4070"],
        ssds=["1024GB", "2TB"],
        hdds=["无"]
    )
    print("=== 规范化结果示范 ===")
    print(f"品牌名称: {demo['brand']}")
    print(f"别名:     {demo['alias']}")
    print(f"发布时间: {demo['release_date']}")
    print(f"CPU:      {demo['cpu_raw']}")
    print(f"显卡:     {demo['gpu_raw']}")
    print(f"固态硬盘: {demo['ssd_raw']}")
    print(f"机械硬盘: {demo['hdd_raw']}")
    print(f"理论SKU组合数: {demo['combo_count']} 种")
