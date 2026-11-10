#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huishoubao Batch Pricing Engine (回收宝批量估价引擎)
Support: Auto-mapping "过保 + 完美", SHA1 dynamic signature, and batch evaluation.
"""

import os
import sys
import time
import json
import csv
import hashlib
import requests

SECRET = 'b7cab12b2b81385dd2cccb8ce67e4998'

def calculate_sign(query_params, body_params):
    """Calculate Huishoubao SHA1 signature."""
    combined = {**query_params, **body_params}
    # Sort keys alphabetically, filter out sign, images, and empty values
    sorted_parts = []
    for k in sorted(combined.keys()):
        if k in ['sign', 'images']:
            continue
        v = combined[k]
        if v is not None and str(v) != '':
            sorted_parts.append(f"{k}{v}")
    raw_str = "".join(sorted_parts) + SECRET
    return hashlib.sha1(raw_str.encode('utf-8')).hexdigest().lower()

def match_option(question, target_spec):
    """
    Intelligently match standard option for '过保 + 完美' condition.
    """
    name = question.get('name', '')
    opts = question.get('question', [])
    
    # 购买渠道 / 版本
    if any(k in name for k in ['购买渠道', '版本', '渠道']):
        return next((o for o in opts if '国行' in o['name']), opts[0])
    
    # 保修期
    if '保修' in name:
        return next((o for o in opts if any(k in o['name'] for k in ['过保', '30天以上', '过保修期'])), opts[0])
        
    # 存储容量
    if any(k in name for k in ['内存', '容量', '存储']):
        target_s = target_spec.get('storage', '').upper().replace('G', 'GB')
        matched = next((o for o in opts if o['name'].upper() == target_s or o['name'].upper().startswith(target_s)), None)
        return matched if matched else opts[0]
        
    # 颜色
    if '颜色' in name:
        target_c = target_spec.get('color', '')
        matched = next((o for o in opts if target_c in o['name'] or o['name'] in target_c), None)
        return matched if matched else opts[0]
        
    # 型号代码
    if '型号' in name:
        code = target_spec.get('code', '')
        matched = next((o for o in opts if code and code in o['name']), None)
        return matched if matched else opts[0]
        
    # 开机情况
    if any(k in name for k in ['开机', '使用状态']):
        return next((o for o in opts if any(k in o['name'] for k in ['正常进入桌面', '正常使用'])), opts[0])
        
    # iCloud / 账号锁
    if 'icloud' in name.lower() or '锁' in name:
        return next((o for o in opts if '无' in o['name'] or '注销' in o['name'] or '退出' in o['name']), opts[0])
        
    # 边框背板 / 外观成色
    if any(k in name for k in ['成色', '外观', '边框']):
        return next((o for o in opts if any(k in o['name'] for k in ['完好', '无磕碰', '完美', '无任何痕迹'])), opts[0])
        
    # 屏幕外观
    if '屏幕外观' in name or '屏幕划痕' in name:
        return next((o for o in opts if any(k in o['name'] for k in ['完好', '无划痕', '完美'])), opts[0])
        
    # 屏幕显示
    if '屏幕显示' in name or '显示' in name:
        return next((o for o in opts if any(k in o['name'] for k in ['正常', '完美', '无任何异常'])), opts[0])
        
    # 维修情况
    if '维修' in name or '拆修' in name:
        return next((o for o in opts if '无维修' in o['name'] or '未拆修' in o['name']), opts[0])
        
    # 功能性问题
    if '功能' in name:
        return next((o for o in opts if any(k in o['name'] for k in ['全部正常', '完好', '功能正常'])), opts[0])
        
    # 默认返回第一项最佳成色
    return opts[0] if opts else None

def get_product_questions(pid):
    """Fetch evaluate parameters for product."""
    ts = str(int(time.time()))
    q = {
        'pid': '1004',
        'platform': '5',
        'timestamp': ts,
        'version': '1',
        'productId': str(pid)
    }
    q['sign'] = calculate_sign(q, {})
    resp = requests.post(
        'https://api.huishoubao.com/api/product/getEvaluateParam',
        params=q,
        proxies={'http': None, 'https': None},
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get('_data', {}).get('itemList', [])
    return []

def evaluate_single(pid, select_ids, token):
    """Execute single evaluation call."""
    select_str = json.dumps(select_ids, separators=(',', ':'))
    ts = str(int(time.time()))
    q = {
        'pid': '1004',
        'platform': '5',
        'timestamp': ts,
        'version': '1',
        'token': token
    }
    b = {
        'productId': str(pid),
        'select': select_str
    }
    q['sign'] = calculate_sign(q, b)
    
    headers = {
        'Origin': 'https://ka.huishoubao.com',
        'Referer': 'https://ka.huishoubao.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': f'token={token}'
    }
    
    resp = requests.post(
        'https://api.huishoubao.com/api/product/evaluate',
        params=q,
        data=b,
        headers=headers,
        proxies={'http': None, 'https': None},
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json()
    return {'_errCode': str(resp.status_code), '_errStr': resp.text}

if __name__ == '__main__':
    print("Huishoubao pricing engine initialized successfully.")
