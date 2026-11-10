---
name: samsung-tradein-pricing
description: "Query official device trade-in / buyback prices from Samsung China Mall (powered by ShanHuiShou / 闪回收). Use when the user wants to check trade-in valuations, recycle prices, or resale quotes for smartphones (iPhone, Galaxy, Xiaomi, Huawei, etc.), especially for '过保' (out-of-warranty) and '完美机型' (flawless condition) or batch device lists. Triggers on: '三星以旧换新', '闪回收价格', '三星官网回收价', '以旧换新估价', '查询过保完美机型价格', 'samsung trade-in pricing'."
---

# Samsung Mall Trade-In (ShanHuiShou / 闪回收) Pricing Skill

## 1. 概述 (Overview)

本技能用于**直接调用三星商城（中国）以旧换新合作通道（闪回收 SHANHS）的底层 RESTful API**，对手机（iPhone、三星 Galaxy 等）进行超高速、精准的官方以旧换新折抵估价。

### 为什么不使用 Chrome DevTools 浏览器自动化？
- **效率相差百倍**：传统的 Chrome DevTools 需要开启浏览器 GUI、等待网页渲染、处理多步模态框与十几个问答项的点击交互，单台机型耗时约 15~30 秒，批量查询耗时数分钟且容易超时。
- **底层 API 极速免头**：通过逆向分析提取的轻量 REST/JSON 接口，并发查询 40 台机型仅需 **2~5 秒**。
- **三重防线自动校验**：每次运行自动运行“金丝雀基准机型（Canary Check）”探针自检、校验官方防伪签发 `discountAmount-hash`、并与官方最高置换限额做边界对比，确保接口改版时立即报错拦截。

---

## 2. 常用命令与使用方法 (Usage)

所有功能由脚本 `scripts/quote.py` 提供支持。

### 2.1 一键查询默认常查清单（40 款过保+完美预设清单）
用户常用的 40 款测试机型已固化在 `assets/watchlist.txt`。直接运行无参数命令或 `--watchlist` 即可按“过保+完美”条件批量拉取：
```bash
python scripts/quote.py --watchlist
```
*(若某个老款机型如 iPhone 6S / 7 / 8 / SE 初代在三星闪回收渠道已下架不支持，系统会自动精准标识为“暂不支持/已下架”，绝不张冠李戴错配其他机型。)*

### 2.2 单台机型查询
```bash
python scripts/quote.py --model "iPhone 16e" --submodel "A3410" --storage "256G" --color "黑色" --warranty "过保" --condition "完美"
```

### 2.3 批量文本直接查询
```bash
python scripts/quote.py --text "
iPhone 17e	A3635	256G	国行	白色
iPhone SE 3	A2785	256G	国行	红色
"
```

### 2.4 健康检查 / 导出格式
```bash
# 运行金丝雀自检（验证接口是否正常可用）
python scripts/quote.py --verify

# 输出为 JSON / CSV
python scripts/quote.py --watchlist --format json
python scripts/quote.py --watchlist --format csv
```

---

## 3. 评测成色标准与接口参考

详细的三星 Hybris / 闪回收电商接口定义、层级查询表达式（`filterDevicesV2`）、问答树解析与签名规则，请参考：
- `references/api_reference.md`
