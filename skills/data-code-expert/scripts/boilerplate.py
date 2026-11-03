# ================================================================
# 数据处理脚本骨架 — 由 data-code-expert 技能生成
# 使用说明：只修改【参数配置】和【核心逻辑】两个区块
# 其余模块（环境自检/质量校验/空值分流/异常处理）保持不变
# ================================================================

# ========== 1. 环境自检（禁止删除）==========
import importlib.util
import sys

REQUIRED = {
    # 只保留本脚本实际使用的包（键为 import 模块名，值为 pip 安装包名）
    # 注意：Polars 的 read_excel(engine="calamine") 底层调用 fastexcel；
    # 若改用 Pandas 的 read_excel(engine="calamine")，请改为 "python_calamine": "python-calamine"
    "polars": "polars",
    "fastexcel": "fastexcel",
    "xlsxwriter": "xlsxwriter",
    # "numpy": "numpy",  # 需要向量化数据生成时取消注释
}
missing = [pkg for mod, pkg in REQUIRED.items() if not importlib.util.find_spec(mod)]
if missing:
    print(f"❌ 缺少依赖，请运行：pip install {' '.join(missing)}", file=sys.stderr)
    sys.exit(1)
print("✅ 环境检测通过，开始执行...")

# ========== 2. 完整 Import 区 ==========
import polars as pl
import xlsxwriter
# import numpy as np  # 需要向量化数据生成时取消注释

# ========== 3. 参数配置（集中修改这里）==========
INPUT_FILE  = "input.xlsx"       # 输入文件路径
OUTPUT_FILE = "output.xlsx"      # 输出文件路径
GROUP_BY    = ["字段A", "字段B"] # 分组字段
VALUE_COLS  = ["数值字段"]       # 计算字段
FILTER_COL  = None               # 过滤字段，如 "状态"
FILTER_VAL  = None               # 过滤值，如 "在售" 或 0（支持 0 / False / 空字符串）
COL_ORDER   = None               # 输出列顺序，None = 保持默认

# ========== 4. 读取数据 ==========
try:
    df = pl.read_excel(INPUT_FILE, engine="calamine")  # Polars calamine 引擎底层由 fastexcel 驱动
    print(f"📂 读取成功：{len(df):,} 行 × {len(df.columns)} 列")
except Exception as e:
    print(f"❌ 读取失败：{e}", file=sys.stderr)
    sys.exit(1)

# ========== 5. 数据质量校验与空值分流（禁止静默丢弃）==========
required_cols = list(dict.fromkeys((GROUP_BY or []) + (VALUE_COLS or [])))
if FILTER_COL is not None and FILTER_COL not in required_cols:
    required_cols.append(FILTER_COL)

missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    print(f"❌ 字段不存在：{missing_cols}", file=sys.stderr)
    print(f"   实际字段：{list(df.columns)}", file=sys.stderr)
    sys.exit(1)

# 显式捕获并分流空值行（后续写入独立 Sheet「异常空值明细」，绝不静默丢弃）
null_info = {c: int(df[c].null_count()) for c in required_cols if df[c].null_count() > 0}
null_rows_df = None
if null_info:
    null_mask = pl.any_horizontal([pl.col(c).is_null() for c in required_cols])
    null_rows_df = df.filter(null_mask)
    df = df.filter(~null_mask)
    print(
        f"⚠️  检测到空值：{null_info}，共 {len(null_rows_df):,} 行异常数据将单独输出至「异常空值明细」工作表，"
        f"参与正常计算：{len(df):,} 行"
    )

# 可选过滤（显式判断 is not None，防止过滤值为 0、False 或空字符串时被跳过）
if FILTER_COL is not None and FILTER_VAL is not None:
    df = df.filter(pl.col(FILTER_COL) == FILTER_VAL)
    print(f"🔍 按 {FILTER_COL} == {FILTER_VAL!r} 过滤后：{len(df):,} 行")

# ================================================================
# ⬇️  6. 核心逻辑（在这里替换业务逻辑）
# ================================================================

try:
    result = (
        df
        .group_by(GROUP_BY)
        .agg([pl.col(c).sum() for c in VALUE_COLS])  # 替换为实际计算逻辑
        .sort(VALUE_COLS[0], descending=True)
    )
    if COL_ORDER:
        result = result.select(COL_ORDER)
    print(f"✅ 计算完成：{len(result):,} 行")
except Exception as e:
    print(f"❌ 计算失败：{e}", file=sys.stderr)
    sys.exit(1)

# ================================================================
# ⬆️  核心逻辑结束
# ================================================================

# ========== 7. 输出到 Excel（主结果 + 异常空值明细）==========
try:
    with xlsxwriter.Workbook(OUTPUT_FILE) as workbook:
        result.write_excel(workbook=workbook, worksheet="结果")
        if null_rows_df is not None and len(null_rows_df) > 0:
            null_rows_df.write_excel(workbook=workbook, worksheet="异常空值明细")
    if null_rows_df is not None and len(null_rows_df) > 0:
        print(f"✅ 输出完成 → {OUTPUT_FILE}（含「结果」{len(result):,} 行 + 「异常空值明细」{len(null_rows_df):,} 行）")
    else:
        print(f"✅ 输出完成 → {OUTPUT_FILE}（共 {len(result):,} 行）")
except Exception as e:
    print(f"❌ 写入失败（请检查目标文件是否正被 Excel/WPS 打开占用）：{e}", file=sys.stderr)
    sys.exit(1)

# ================================================================
# 【回退方案】需要保留原文件样式 / 宏时，替换第 4 步和第 7 步为以下内容
# 原因：xlsxwriter 只能新建文件，无法在原文件上修改；openpyxl 可以
# ================================================================
# from openpyxl import load_workbook
#
# try:
#     wb = load_workbook(INPUT_FILE, keep_vba=True)   # keep_vba=True 保留宏
#     ws = wb.active
#     # 在这里操作 ws 单元格，例如：ws["B2"] = new_value
#     wb.save(OUTPUT_FILE)
#     print(f"✅ 输出完成（保留原样式）→ {OUTPUT_FILE}")
# except Exception as e:
#     print(f"❌ 写入失败：{e}", file=sys.stderr)
#     sys.exit(1)
