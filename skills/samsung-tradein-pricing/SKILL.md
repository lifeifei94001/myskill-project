---
name: samsung-tradein-pricing
description: "Query official device trade-in / buyback prices from Samsung China Mall (powered by ShanHuiShou / 闪回收). Use when the user wants to check trade-in valuations, recycle prices, or resale quotes for smartphones (iPhone, Galaxy, Xiaomi, Huawei, etc.), especially for '过保' (out-of-warranty) and '完美机型' (flawless condition) or batch device lists. Triggers on: '三星以旧换新', '闪回收价格', '三星官网回收价', '以旧换新估价', '查询过保完美机型价格', 'samsung trade-in pricing'."
---

# Samsung Mall Trade-In (ShanHuiShou / 闪回收) Pricing Skill

## 1. 概述 (Overview)

本技能用于**直接调用三星商城（中国）以旧换新合作通道（闪回收 SHANHS）的底层 RESTful API**，对手机（iPhone、三星 Galaxy 等）进行超高速、精准的官方以旧换新折抵估价。

### 为什么不使用 Chrome DevTools 浏览器自动化？
- **效率相差百倍**：传统的 Chrome DevTools 需要开启浏览器 GUI、等待网页渲染、处理多步模态框与十几个问答项的点击交互，单台机型耗时约 15~30 秒，批量 20 台需要数分钟且容易超时崩溃。
- **底层 API 极速免头**：通过逆向分析提取的轻量 REST/JSON 接口，单机型仅需 **100~200ms**，20 台机型并发查询仅需 **2~3 秒**。
- **免依赖与免配置**：无需在本地启动带 `--remote-debugging-port` 的 Chrome 实例，无需人工干预。

---

## 2. 常用命令与使用方法 (Usage)

所有功能由脚本 `scripts/quote.py` 提供支持。

### 2.1 单台机型查询
```bash
python scripts/quote.py --model "iPhone 16e" --submodel "A3410" --storage "256G" --color "黑色" --warranty "过保" --condition "完美"
```

参数说明：
- `--model`：机型名称（如 `iPhone 16e`、`iPhone 15 Pro`、`Galaxy S24 Ultra`）
- `--submodel`：型号/监管编码（如 `A3410`、`A3104`，非必填，自动匹配全网通）
- `--storage`：内存容量（如 `128G`、`256G`、`512G`、`1T`）
- `--color`：机身颜色（如 `黑色`、`白色`、`暗紫色`、`粉色` 等）
- `--channel`：购买渠道，默认 `国行`
- `--warranty`：保修状态，`过保`（默认，保修期≤1个月）或 `在保`
- `--condition`：成色预设，默认 `完美`（全硬件正常、屏幕与外观无划痕、电池健康最好档）

---

### 2.2 批量文本直接查询（支持用户原样粘贴文本/表格）
如果用户直接发来多行制表符分隔或空格分隔的机型清单：

```bash
python scripts/quote.py --text "
iPhone 17e	A3635	256G	国行	白色
iPhone 17e	A3635	512G	国行	白色
iPhone 16e	A3410	512G	国行	黑色
iPhone 15 Pro	A3104	128G	国行	白色钛金属
"
```

### 2.3 批量文件查询与格式化输出
支持从文本文件或 JSON 文件批量导入，并导出为 Markdown、JSON 或 CSV：

```bash
# 输出为标准 Markdown 表格（默认）
python scripts/quote.py --batch-file devices.txt --format markdown

# 输出为 JSON
python scripts/quote.py --batch-file devices.txt --format json

# 输出为 CSV
python scripts/quote.py --batch-file devices.txt --format csv
```

---

## 3. 评测成色标准与接口参考

详细的三星 Hybris / 闪回收电商接口定义、层级查询表达式（`filterDevicesV2`）、问答树解析与签名规则，请参考：
- `references/api_reference.md`
