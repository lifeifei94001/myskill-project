> **重要依赖提示**：Polars 的 `pl.read_excel(..., engine="calamine")` 底层依赖包为 **`fastexcel`**（`pip install fastexcel`）；Pandas 的 `pd.read_excel(..., engine="calamine")` 底层依赖包为 **`python-calamine`**（`pip install python-calamine`，模块名为 `python_calamine`）。

# 高级模式参考库

## 1. 超大文件自动启用 Lazy 模式

```python
import os
file_size = os.path.getsize(INPUT_FILE) / (1024 ** 3)  # GB

if file_size > 2:
    print(f"📦 文件大小 {file_size:.1f}GB，自动启用 Lazy 模式...")
    df = pl.scan_csv(INPUT_FILE)  # 或 scan_parquet
    result = df.group_by(GROUP_BY).agg([...]).collect()
else:
    df = pl.read_excel(INPUT_FILE, engine="calamine")
```

## 2. 多文件并发处理

```python
from concurrent.futures import ThreadPoolExecutor
import glob

files = glob.glob("data/*.xlsx")

def process_one(path):
    return pl.read_excel(path, engine="calamine")

if len(files) >= 5:
    print(f"📂 检测到 {len(files)} 个文件，自动启用并发处理...")
    with ThreadPoolExecutor() as executor:
        dfs = list(executor.map(process_one, files))
    df = pl.concat(dfs)
else:
    df = pl.concat([pl.read_excel(f, engine="calamine") for f in files])
```

## 3. 向量化数据生成与规则处理

```python
import numpy as np
import polars as pl

n = 100_000

# 性能瓶颈处优先使用向量化
df = pl.DataFrame({
    "id": np.arange(1, n + 1),
    "品牌": np.random.choice(["苹果", "华为", "小米"], n),
    "价格": np.random.uniform(1000, 9999, n).round(2),
    "库存": np.random.randint(0, 500, n),
    "日期": pl.date_range(
        pl.date(2024, 1, 1), pl.date(2024, 12, 31), "1d", eager=True
    ).sample(n, with_replacement=True),
})
```

## 4. 多表 Left Join 模式

```python
# 左表保留全部，右表按关联键匹配
result = df_left.join(
    df_right,
    on="手机型号",          # 关联键
    how="left",             # left / inner / outer
    suffix="_右表"          # 同名字段后缀区分
)
```

## 5. xlsxwriter 条件格式（标红异常值）

```python
import xlsxwriter

workbook = xlsxwriter.Workbook(OUTPUT_FILE)
worksheet = workbook.add_worksheet("结果")

# 写入数据
for row_idx, row in enumerate(result.iter_rows(named=True), start=1):
    for col_idx, (key, val) in enumerate(row.items()):
        worksheet.write(row_idx, col_idx, val)

# 条件格式：价格列负值标红
red_fmt = workbook.add_format({"bg_color": "#FF6B6B", "font_color": "#FFFFFF"})
worksheet.conditional_format(
    1, price_col_idx, len(result), price_col_idx,
    {"type": "cell", "criteria": "<", "value": 0, "format": red_fmt}
)

workbook.close()
```

## 6. 时间分析：同比 / 环比

```python
# 按月汇总后计算环比
monthly = (
    df.with_columns(pl.col("日期").dt.month().alias("月份"))
    .group_by("月份")
    .agg(pl.col("销售额").sum())
    .sort("月份")
    .with_columns(
        pl.col("销售额").pct_change().alias("环比增长率")
    )
)
```

## 7. 财务口径：含税/不含税金额拆分

```python
TAX_RATE = 0.13  # 增值税率 13%

df = df.with_columns([
    (pl.col("含税金额") / (1 + TAX_RATE)).round(2).alias("不含税金额"),
    (pl.col("含税金额") * TAX_RATE / (1 + TAX_RATE)).round(2).alias("税额"),
])
```

## 8. TopN 分析

```python
# 每个品牌下销售额 Top3 型号
top_n = (
    df.group_by(["品牌", "型号"])
    .agg(pl.col("销售额").sum())
    .sort(["品牌", "销售额"], descending=[False, True])
    .group_by("品牌")
    .head(3)  # 每组取前 3
)
```

## 9. 数据质量报告模块

```python
def data_quality_report(df, required_cols):
    print("\n📊 数据质量报告")
    print(f"  总行数: {len(df):,}")
    
    for col in required_cols:
        if col not in df.columns:
            print(f"  ❌ 字段缺失: {col}")
            continue
        null_count = df[col].null_count()
        null_rate = null_count / len(df) * 100
        dtype = df[col].dtype
        print(f"  ✅ {col}: 类型={dtype}, 空值={null_count}({null_rate:.1f}%)")
    
    print()
```

## 10. openpyxl 回退（保留原文件样式/宏时使用）

```python
# 需保留原文件的条件格式/图表/宏时回退使用 openpyxl
from openpyxl import load_workbook

wb = load_workbook(INPUT_FILE, keep_vba=True)  # keep_vba=True 保留宏
ws = wb.active

# 定向更新单元格，其余样式完好无损
ws["B2"] = "更新的值"
wb.save(OUTPUT_FILE)
```

## 11. 纯 Python 极速多表联算与模板回填（默认 Native 基础模式）

适用于绝大多数多表关联、VLOOKUP 字段匹配、阶梯比率计算、防倒挂校准与模板填充。纯 Python 内存处理不依赖任何外部办公软件，在本地 Windows 与云端 Linux 环境下均可高效完成。

```python
import numpy as np
import pandas as pd
from openpyxl import load_workbook

# 1. 统一加载各数据表
df_main = pd.read_excel("主表_待校准数据.xlsx", engine="calamine")
df_param = pd.read_excel("参数维表.xlsx", engine="calamine")
df_benchmark = pd.read_excel("基准价格表.xlsx", engine="calamine")

# 2. 纯内存哈希字典映射与跨表关联
param_dict = dict(zip(df_param["SKU"], df_param["基准扣率"]))
df_main["基准扣率"] = df_main["SKU"].map(param_dict).fillna(0.0)

df_main = pd.merge(
    df_main,
    df_benchmark[["品牌", "型号", "最低保护价"]],
    on=["品牌", "型号"],
    how="left"
)

# 3. 业务规则计算与防倒挂单调性截断
conditions = [
    df_main["成色"] == "充新",
    df_main["成色"] == "靓机",
    df_main["成色"] == "小花",
]
choices = [
    df_main["基准扣率"] * 0.95,
    df_main["基准扣率"] * 1.00,
    df_main["基准扣率"] * 1.10,
]
df_main["最终扣率"] = np.select(conditions, choices, default=df_main["基准扣率"])

raw_price = df_main["官方指导价"] * (1 - df_main["最终扣率"])
df_main["核准报价"] = np.maximum(raw_price, df_main["最低保护价"].fillna(0)).round(2)

# 4. 纯 Python 模板回填（保持原有排版格式）
wb = load_workbook("模板_最终报价单.xlsx")
ws = wb.active
start_row = 3
cols_to_write = ["SKU", "核准报价", "最终扣率"]
for r_idx, row_data in enumerate(df_main[cols_to_write].itertuples(index=False), start=start_row):
    for c_idx, val in enumerate(row_data, start=1):
        ws.cell(row=r_idx, column=c_idx, value=val)

wb.save("输出_最终报价单_已校准.xlsx")
print("✅ 纯 Python 多表联算与模板灌入完成，零外部 COM 依赖！")
```

## 12. Python 核心 + 可选 WPS 增强适配架构（复杂 Office 场景按需启用）

当且仅当存在**原生复杂跨表公式计算、外部链接刷新（`ChangeLink`）、特殊打印区域排版保真**时，在纯 Python 完成数据与业务计算后，按需唤起 WPS COM 适配器执行最终呈现。

### 架构决策流
```
                  多表自动化任务
                        │
                  Python 核心计算
            (清洗/映射/定价/防倒挂校验)
                        │
            ┌───────────┴───────────┐
            ↓                       ↓
    本地 Windows 环境           云端 Linux / Docker
            │                       │
     是否需要原生 Office 能力？     纯 Python 输出 XLSX
      (公式/链接/特殊排版)                  │
       ┌────┴────┐                          │
      是         否                         │
       ↓         ↓                          ↓
   调用 WPS   纯 Python 输出             最终交付
   执行终审       │
       │         │
       └────┬────┘
            ↓
        最终交付
```

### 核心代码范式
```python
import os
import sys
import pandas as pd
import openpyxl

# 1. Python 核心层：统一读取数据并完成业务逻辑（纯 Python，零 Office 依赖）
df_master = pd.read_excel("后台数据.xlsx", engine="calamine")
df_price = pd.read_excel("价格表.xlsx", engine="calamine")
df_map = pd.read_excel("映射表.xlsx", engine="calamine")

# 业务匹配与计算
sku_dict = dict(zip(df_map["渠道机型"], df_map["标准机型"]))
df_master["标准机型"] = df_master["原始机型"].map(sku_dict).fillna(df_master["原始机型"])
df_result = df_master.merge(df_price, on="标准机型", how="left")

# 2. 一次性回填模板
OUTPUT_XLSX = "处理后/最终成果表.xlsx"
wb = openpyxl.load_workbook("模板_大表.xlsx")
ws = wb["数据底表"]
start_row = 3
cols = ["标准机型", "核算报价", "备注"]
for r_idx, row_vals in enumerate(df_result[cols].itertuples(index=False), start=start_row):
    for c_idx, val in enumerate(row_vals, start=1):
        ws.cell(row=r_idx, column=c_idx, value=val)
wb.save(OUTPUT_XLSX)
wb.close()

# 3. 按需 Office 增强（仅在 Windows 且需要原生公式/外部链接刷新时调用）
def apply_optional_wps_recalc(file_path: str):
    if sys.platform != "win32":
        return
    try:
        import win32com.client
        app = None
        is_reused = False
        try:
            app = win32com.client.GetActiveObject("ket.application")
            is_reused = True
        except Exception:
            app = win32com.client.Dispatch("ket.application")
            app.Visible = False
            app.DisplayAlerts = False
        
        if app:
            wb = app.Workbooks.Open(os.path.abspath(file_path), UpdateLinks=0)
            wb.Sheets("数据底表").Calculate()
            wb.Save()
            wb.Close(SaveChanges=True)
            if not is_reused:
                app.Quit()
            print("✅ WPS 增强引擎重算完成！")
    except Exception as e:
        print(f"ℹ️ WPS 增强跳过或提示: {e}，数据已由底层 Python 完成安全落地")

apply_optional_wps_recalc(OUTPUT_XLSX)
```

> **这个简化版函数只适合"WPS 增强"场景**（失败了也无所谓，纯 Python 结果本身就是对的）。
> 如果这次任务是"外部链接必须刷新到新文件、否则数据是错的"这种**WPS 强依赖**场景，
> 不要用这个静默吞异常的简化版——改用 `references/desktop_app_architecture.md` 里
> `office_engine/wps_engine.py` 的 `apply_wps_enhancement(..., required=True)`，失败时
> 会抛出 `WpsEnhancementFailed` 让用户明确看到，而不是悄悄产出一份没刷新链接的文件。

## 13. 多表联动实战强化：字典查表引擎 + 批量公式引擎（替代跨表 VLOOKUP 逐格计算）

**这条是"Python 负责数据怎么算，WPS 负责 Excel 怎么工作"这条总原则在多表联动里最具体的落地写法。** 当"关联键"来自另一张表且该表本身带合并单元格/向下填充省略值（如"型号"列只在变化时才写一次，其余留空表示"同上"）时，不要在 Excel 里用跨表 VLOOKUP/INDEX-MATCH 让 WPS 逐格计算——先用 Python 把参照表一次性摊平成 `(行键, 列键) -> 值` 的字典，查表就变成 O(1) 内存操作，比 COM 遍历快至少一个数量级，也不会有公式跨表引用失效的风险。

```python
import numpy as np

def build_lookup_dict(raw_rows: list, key_col_idx: int = 0, header_row_idx: int = 0) -> dict:
    """
    把"表头在第 header_row_idx 行、关联键列有合并单元格向下省略值"的参照表，
    摊平为 {(行键, 列键): 值} 字典。raw_rows 是二维 list（例如 ws.Range(...).Value 或
    pandas 读出来再 .values.tolist() 的结果）。
    """
    if not raw_rows or len(raw_rows) <= header_row_idx:
        return {}
    header = raw_rows[header_row_idx]
    lookup, last_row_key = {}, ""
    for row in raw_rows[header_row_idx + 1:]:
        row_key = str(row[key_col_idx]).strip() if row[key_col_idx] not in (None, "") else last_row_key
        if row_key:
            last_row_key = row_key
        else:
            continue
        for col_idx, col_key in enumerate(header):
            if col_key in (None, "") or col_idx >= len(row):
                continue
            lookup[(row_key, str(col_key).strip())] = row[col_idx]
    return lookup

# 用法：三张表统一摊平成字典后，主表用向量化 map/apply 一次性查完，不逐行进 WPS
ref_dict = build_lookup_dict(raw_rows=参照表二维数组)
df_main["匹配结果"] = df_main.apply(
    lambda r: ref_dict.get((r["型号"], r["成色"] + "扣减比例")), axis=1
)
```

**必须保留原生公式（而非纯数值）时**，用 `office_engine/wps_engine.py` 里的 `batch_fill_formula_columns`（`PasteSpecial` 批量下拉公式列）而不是逐行写 `Formula`，原理和这里的字典查表一致：把"逐格/逐行"操作变成"一次性批量"操作。

> 一句话记住这条：**公式是模板，Python 是计算引擎**——不追求"彻底脱离 WPS"，也不追求"什么都用公式"，按这次任务的实际瓶颈（重算风暴？逐格 IPC？还是必须保真的原生语法？）选组合。
