# 桌面工具模式 — 工程模板参考库（原生 GUI，默认 CustomTkinter）

生成桌面小工具代码时，以下每个模块直接作为骨架填充业务逻辑，禁止改变整体结构。

---

## 1. 目录结构（支持本地 EXE 与未来云端 Web 复用的解耦结构）

```
项目根/
├── main.py                   # 入口：SafeWriter 重定向 → 创建主窗口 → 进入 GUI 事件循环
├── config/
│   ├── __init__.py
│   ├── paths.py              # 路径自适应（源码运行与打包无缝兼容）
│   └── settings.py           # 默认参数、常量配置
├── core/                     # ⭐ 纯业务逻辑层（绝不依赖 GUI、绝不直接 import win32com）
│   ├── __init__.py
│   ├── matching.py           # 机型/SKU 跨表映射与字典匹配
│   ├── pricing.py            # 价格计算、阶梯比率与单调性调整
│   └── validation.py         # 业务规则校验与异常判定
├── data_engine/              # 数据 I/O 与存储层
│   ├── __init__.py
│   ├── atomic_io.py          # 线程锁 + 跨进程文件锁 + .tmp + .bak + os.replace 原子写入
│   ├── reader.py             # 基于 Calamine / Pandas / Polars 的统一批量读取器
│   └── excel_io.py           # 表头两趟严格匹配与模板填充
├── office_engine/            # 可选 Office 增强适配层（按需启用，绝非 core 的强依赖）
│   ├── __init__.py
│   ├── base.py               # 抽象引擎基类
│   ├── python_engine.py      # 默认纯 Python 渲染与输出引擎（Linux/云端/无Office环境兜底）
│   └── wps_engine.py         # 本地 Windows 下按需 WPS COM 引擎（A/B/C/D 四层容错驱动，含主动唤醒轮询）
├── ui/                       # 视图层（CustomTkinter 组件与事件回调）
│   ├── __init__.py
│   └── main_window.py        # 主窗口骨架
├── data/                     # 运行时生成：用户记忆、字典库、.bak 备份
├── test_suite.py             # 独立单元测试（针对 core/ 与 atomic_io，无需 GUI 和 Office 进程）
└── build.spec                # PyInstaller 打包配置（upx=False 防杀软误报 + 英文构建名）
```

---

## 2. `config/paths.py` — 路径自适应（源码运行 / PyInstaller 打包通用）

```python
import sys
from pathlib import Path

def get_base_dir() -> Path:
    """
    获取应用根目录：
    - 源码运行时为当前项目根目录
    - PyInstaller 单文件/单目录打包运行时为 exe 所在目录
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
```

---

## 3. `data_engine/atomic_io.py` — 线程安全 + 跨进程安全的原子写入（字典库/配置回写）

> **修复说明**：除了单进程内的 `threading.Lock()`，还内置了零第三方依赖的跨进程文件锁 `_InterProcessFileLock`（Windows 使用标准库 `msvcrt.locking`，Linux/macOS 使用 `fcntl.flock`），防止用户双击多开两个 EXE 实例同时回写字典文件时发生竞争损坏。

```python
from contextlib import contextmanager
import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any, Iterator

_write_lock = threading.Lock()


@contextmanager
def _interprocess_file_lock(lock_path: Path, timeout: float = 10.0) -> Iterator[None]:
    """标准库跨进程文件锁（兼容 Windows msvcrt 与 Unix fcntl，无需第三方依赖）"""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_path, "a+b")
    deadline = time.monotonic() + timeout
    locked = False
    try:
        while True:
            try:
                if sys.platform == "win32":
                    import msvcrt
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"等待跨进程文件锁超时: {lock_path}")
                time.sleep(0.05)
        yield
    finally:
        if locked:
            try:
                if sys.platform == "win32":
                    import msvcrt
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        f.close()


def atomic_write_json(target: Path, data: dict[str, Any] | list[Any]) -> None:
    """
    线程安全 + 跨进程安全的原子写入：
    1. 获取进程内线程锁 _write_lock 与跨进程文件锁 target.lock
    2. 先写入带进程 PID 与线程 ID 的唯一临时文件 .tmp，并执行 os.fsync 落盘
    3. 若原目标存在，生成 .bak 备份
    4. 用 os.replace 原子替换目标文件（同分区内 OS 级原子操作）
    """
    target = Path(target)
    lock_file = target.with_suffix(target.suffix + ".lock")
    with _write_lock, _interprocess_file_lock(lock_file):
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f"{target.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())

            if target.exists():
                bak = target.with_suffix(target.suffix + ".bak")
                shutil.copy2(target, bak)

            os.replace(tmp, target)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
```

---

## 4. `data_engine/excel_io.py` — 表头两趟严格匹配（禁止子串模糊匹配）

```python
import unicodedata

def _normalize(s: str) -> str:
    """全角转半角 + 去首尾空格，用于第二趟匹配"""
    return unicodedata.normalize("NFKC", str(s)).strip()

def match_headers(actual_headers: list[str], expected_headers: list[str]) -> dict[str, str]:
    """
    两趟严格全等匹配，返回 {期望列名: 实际列名}
    第一趟：原始字符串精确全等匹配
    第二趟：仅对未匹配上的列做全半角/空格归一化后再次精确全等匹配
    全程禁止用 `in` / startswith 做子串包含匹配，防止"单价"误匹配"单价(含税)"
    """
    mapping = {}
    remaining_expected = list(expected_headers)
    remaining_actual = list(actual_headers)

    dup_raw = [h for h in set(remaining_actual) if remaining_actual.count(h) > 1]
    if dup_raw:
        raise ValueError(f"检测到重复表头，无法确定应使用哪一列，请人工确认后重新导出：{dup_raw}")
    norm_counts: dict[str, list[str]] = {}
    for a in remaining_actual:
        norm_counts.setdefault(_normalize(a), []).append(a)
    dup_norm = {k: v for k, v in norm_counts.items() if len(v) > 1}
    if dup_norm:
        raise ValueError(f"检测到归一化后冲突的表头（全半角/空格差异掩盖了重复列），请人工确认后重新导出：{dup_norm}")

    for exp in list(remaining_expected):
        if exp in remaining_actual:
            mapping[exp] = exp
            remaining_expected.remove(exp)
            remaining_actual.remove(exp)

    norm_actual = {_normalize(a): a for a in remaining_actual}
    for exp in list(remaining_expected):
        norm_exp = _normalize(exp)
        if norm_exp in norm_actual:
            mapping[exp] = norm_actual[norm_exp]
            remaining_expected.remove(exp)
            remaining_actual.pop(list(remaining_actual).index(norm_actual[norm_exp]))

    if remaining_expected:
        raise ValueError(f"缺少必需列：{remaining_expected}（实际列：{actual_headers}）")

    return mapping
```

---

## 5. `core/pricing.py` — 纯业务逻辑层示例（纯 Python，零 Office 依赖）

```python
import numpy as np
import pandas as pd
from typing import Dict

def calculate_tier_prices(
    df_master: pd.DataFrame,
    sku_mapping: Dict[str, str],
    price_rules: pd.DataFrame,
    min_protect_prices: Dict[str, float]
) -> pd.DataFrame:
    """
    纯业务核心计算：不依赖 GUI，不依赖 win32com，不依赖 openpyxl
    """
    df = df_master.copy()
    df["标准机型"] = df["原始机型"].map(sku_mapping).fillna(df["原始机型"])
    df = df.merge(price_rules, on=["标准机型", "内存配置"], how="left")
    base_price = pd.to_numeric(df["基准报价"], errors="coerce").fillna(0.0)
    discount = np.where(base_price >= 5000, 0.92,
               np.where(base_price >= 3000, 0.95, 0.98))
    raw_calc = base_price * discount
    protect_vals = df["标准机型"].map(min_protect_prices).fillna(0.0)
    final_price = np.maximum(raw_calc, protect_vals)
    df["最终核算价"] = (final_price // 10) * 10
    return df
```

---

## 6. `office_engine/wps_engine.py` — 可选 Office 增强适配器（A/B/C/D 四层驱动，实战强化版）

```python
# -*- coding: utf-8 -*-
"""
office_engine/wps_engine.py
WPS/Excel 本地增强适配器 (按需启用，四层渐进式容错驱动)
Layer A: GetActiveObject 零等待热复用
Layer B: Dispatch 接管已在跑但未注册 ROT 的实例
Layer C: 注册表 LocalServer32 静默唤醒 + DispatchEx 轮询接管
Layer D: 纯内存兜底（required=False 时平稳降级，required=True 时抛 WpsEnhancementFailed）
"""
import os
import sys
import time
import subprocess
from typing import Dict, List, Optional, Tuple, Any

XL_CALC_MANUAL = -4135
XL_CALC_AUTO = -4105


def _try_wake_office_exe(log_callback=print) -> bool:
    import winreg
    prog_ids = ["KET.Application", "ET.Application", "Excel.Application"]
    for prog_id in prog_ids:
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, prog_id + r"\CLSID") as k:
                clsid = winreg.QueryValue(k, "")
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"CLSID\{clsid}\LocalServer32") as k:
                raw = winreg.QueryValue(k, "").strip()
            exe = raw[1:].split('"')[0] if raw.startswith('"') else raw.split()[0]
            if os.path.exists(exe):
                subprocess.Popen(
                    [exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000,
                )
                log_callback(f"  └ [Layer C] 已从注册表唤醒 {os.path.basename(exe)}，等待接管...")
                return True
        except Exception:
            continue
    log_callback("  └ [Layer C] 注册表中未找到 WPS/Excel 可执行路径")
    return False


def get_wps_app(log_callback=print) -> Tuple[Any, Optional[str], bool]:
    if sys.platform != "win32":
        return None, None, False
    try:
        import win32com.client as win32
    except ImportError:
        log_callback("⚠️ 未检测到 pywin32 库，将自动降级为 Layer D 纯内存兜底")
        return None, None, False

    prog_ids = ["KET.Application", "ET.Application", "Excel.Application"]
    for prog_id in prog_ids:
        try:
            app = win32.GetActiveObject(prog_id)
            if hasattr(app, "Workbooks"):
                log_callback(f"[*] [Layer A] 复用活跃窗口，零等待: {prog_id}")
                return app, prog_id, True
        except Exception:
            pass

    for prog_id in prog_ids:
        try:
            app = win32.Dispatch(prog_id)
            if hasattr(app, "Workbooks"):
                is_reused = False
                try:
                    is_reused = app.Workbooks.Count > 0
                except Exception:
                    pass
                if not is_reused:
                    try:
                        app.Visible = False
                        app.DisplayAlerts = False
                    except Exception:
                        pass
                log_callback(f"[*] [Layer B] Dispatch 接管成功 ({prog_id}, {'复用' if is_reused else '新建'}实例)")
                return app, prog_id, is_reused
            try:
                app.Quit()
            except Exception:
                pass
        except Exception:
            continue

    log_callback("  ⏳ [Layer C] 桌面未检测到 WPS/Excel，尝试主动唤醒...")
    if not _try_wake_office_exe(log_callback):
        return None, None, False

    for prog_id in prog_ids:
        for attempt in range(12):
            try:
                app = win32.DispatchEx(prog_id)
                if hasattr(app, "Workbooks"):
                    try:
                        app.Visible = False
                        app.DisplayAlerts = False
                    except Exception:
                        pass
                    log_callback(f"[*] [Layer C] DispatchEx 接管成功 ({prog_id}，耗时约 {attempt * 1.5:.0f}s)")
                    return app, prog_id, False
            except Exception:
                time.sleep(1.5)

    log_callback("  ⚠️ [Layer C] 轮询 18 秒仍未接管，降级至 Layer D 纯内存兜底")
    return None, None, False


def freeze_engine(app):
    for attr, val in (("Calculation", XL_CALC_MANUAL), ("EnableEvents", False), ("ScreenUpdating", False)):
        try:
            setattr(app, attr, val)
        except Exception:
            pass


def unfreeze_engine(app):
    for attr, val in (("Calculation", XL_CALC_AUTO), ("EnableEvents", True), ("ScreenUpdating", True)):
        try:
            setattr(app, attr, val)
        except Exception:
            pass


class WpsEnhancementFailed(RuntimeError):
    """仅在 required=True 时抛出：结果正确性依赖 WPS 刷新成功，禁止静默降级"""


def apply_wps_enhancement(
    output_path: str,
    link_mapping: Optional[Dict[str, str]] = None,
    recalc_sheets: Optional[List[str]] = None,
    required: bool = False,
    log_callback=print
) -> bool:
    if sys.platform != "win32":
        msg = "非 Windows 平台，跳过 WPS COM 增强"
        if required:
            raise WpsEnhancementFailed(msg + "，但本次任务标记为 required=True，无法降级")
        log_callback(f"ℹ️ {msg}")
        return False

    co_inited = False
    try:
        import pythoncom
        pythoncom.CoInitialize()
        co_inited = True
    except Exception:
        pass

    app, _, is_reused = get_wps_app(log_callback)
    if not app:
        if co_inited:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
        if required:
            raise WpsEnhancementFailed(
                "四层驱动均未能接管 WPS/Excel COM 引擎，而本次任务标记为 required=True，不能静默降级。"
            )
        log_callback("ℹ️ [Layer D] 未能接管 COM 引擎，已由底层 openpyxl 完成数据落地")
        return False

    wb = None
    abs_path = os.path.abspath(output_path)
    freeze_engine(app)
    try:
        wb = app.Workbooks.Open(abs_path, UpdateLinks=0)
        if link_mapping:
            sources = wb.LinkSources(1)
            if sources:
                for old_lnk in sources:
                    old_fn = os.path.basename(old_lnk)
                    for kw, new_file in link_mapping.items():
                        if new_file and os.path.exists(new_file) and (kw in old_fn):
                            new_abs = os.path.abspath(new_file)
                            if os.path.normpath(new_abs) != os.path.normpath(old_lnk):
                                wb.ChangeLink(old_lnk, new_abs, 1)
                                wb.UpdateLink(Name=new_abs)
                            break

        if recalc_sheets:
            for s in wb.Sheets:
                if any(name in str(s.Name) for name in recalc_sheets):
                    s.Calculate()
        else:
            wb.Calculate()

        wb.Save()
        log_callback(f"✅ [WPS适配器] 工作簿重算并安全保存: {os.path.basename(abs_path)}")
        return True
    except Exception as ex:
        if required:
            raise WpsEnhancementFailed(f"WPS 增强执行失败（required=True）：{ex}") from ex
        log_callback(f"⚠️ [WPS适配器] 增强执行提示: {ex}")
        return False
    finally:
        if wb:
            try:
                wb.Close(SaveChanges=True)
            except Exception:
                pass
        unfreeze_engine(app)
        if app and not is_reused:
            try:
                app.Quit()
            except Exception:
                pass
        if co_inited:
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass


def batch_fill_formula_columns(ws, col_start: str, col_end: str, template_row: int, last_row: int, log_callback=print):
    def _col_to_num(c: str) -> int:
        c, n = c.upper(), 0
        for ch in c:
            n = n * 26 + (ord(ch) - ord("A") + 1)
        return n

    def _num_to_col(n: int) -> str:
        s = ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    if last_row <= template_row:
        return
    for cn in range(_col_to_num(col_start), _col_to_num(col_end) + 1):
        col = _num_to_col(cn)
        cell = ws.Range(f"{col}{template_row}")
        formula = cell.Formula
        if formula and str(formula).startswith("="):
            cell.Copy()
            ws.Range(f"{col}{template_row}:{col}{last_row}").PasteSpecial(Paste=-4123)
    try:
        ws.Application.CutCopyMode = False
    except Exception:
        pass
    log_callback(f"[*] [批量公式引擎] {col_start}:{col_end} 列公式已下拉至第 {last_row} 行")
```

---

## 7. `main.py` — CustomTkinter 入口 + 防崩溃 + 子线程任务

```python
import os
import sys
import threading
from pathlib import Path

class SafeWriter:
    def __init__(self, log_path: Path):
        self.log_path = log_path

    def write(self, message):
        if not message:
            return
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass

    def flush(self):
        pass

log_file = Path(os.environ.get("APPDATA", ".")) / "app_error.log"
if sys.stdout is None or getattr(sys, "frozen", False):
    sys.stdout = SafeWriter(log_file)
if sys.stderr is None or getattr(sys, "frozen", False):
    sys.stderr = SafeWriter(log_file)

import customtkinter as ctk
from ui.main_window import MainWindow

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    def run_in_thread(task_fn, on_done=None, on_error=None):
        def worker():
            try:
                res = task_fn()
                if on_done:
                    app.after(0, lambda: on_done(res))
            except Exception as e:
                if on_error:
                    app.after(0, lambda: on_error(e))
                else:
                    sys.stderr.write(f"任务出错: {e}\n")
        threading.Thread(target=worker, daemon=True).start()

    app = MainWindow(run_in_thread=run_in_thread)
    app.mainloop()

if __name__ == "__main__":
    main()
```

---

## 8. `ui/main_window.py` — CustomTkinter 主窗口骨架

```python
import customtkinter as ctk
from tkinter import messagebox
from core.pricing import calculate_tier_prices

class MainWindow(ctk.CTk):
    def __init__(self, run_in_thread):
        super().__init__()
        self.run_in_thread = run_in_thread
        self.title("多表自动化处理工作台")
        self.geometry("780x580")

        ctk.CTkLabel(self, text="多表联动自动化工作台", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        self.btn_run = ctk.CTkButton(self, text="开始批量处理", command=self._on_click_run)
        self.btn_run.pack(pady=20)
        self.status_label = ctk.CTkLabel(self, text="就绪")
        self.status_label.pack(pady=10)

    def _on_click_run(self):
        try:
            self.btn_run.configure(state="disabled")
            self.status_label.configure(text="正在处理中，请稍候...")
            self.run_in_thread(
                lambda: "处理成功完成！",
                on_done=self._on_success,
                on_error=self._on_error
            )
        except Exception as e:
            messagebox.showerror("异常", f"启动失败: {e}")
            self.btn_run.configure(state="normal")

    def _on_success(self, msg):
        self.btn_run.configure(state="normal")
        self.status_label.configure(text=msg)
        messagebox.showinfo("完成", msg)

    def _on_error(self, err):
        self.btn_run.configure(state="normal")
        self.status_label.configure(text="处理失败")
        messagebox.showerror("错误", f"处理中断: {err}")
```

---

## 9. `test_suite.py` — 核心算法用例 + 多线程/跨进程原子写入测试模板

```python
import threading
import unittest
from pathlib import Path
import pandas as pd

from data_engine.atomic_io import atomic_write_json
from data_engine.excel_io import match_headers
from core.pricing import calculate_tier_prices

class TestCorePricing(unittest.TestCase):
    def test_pricing_logic_standalone(self):
        df_dummy = pd.DataFrame({"原始机型": ["iPhone 13", "Mate 60"], "内存配置": ["128G", "256G"]})
        rules = pd.DataFrame({"标准机型": ["iPhone 13", "Mate 60"], "内存配置": ["128G", "256G"], "基准报价": [3200, 5500]})
        res = calculate_tier_prices(
            df_master=df_dummy,
            sku_mapping={"iPhone 13": "iPhone 13"},
            price_rules=rules,
            min_protect_prices={"iPhone 13": 2500, "Mate 60": 4000}
        )
        self.assertEqual(len(res), 2)
        self.assertIn("最终核算价", res.columns)

class TestAtomicWrite(unittest.TestCase):
    def test_concurrent_atomic_write(self):
        target = Path("data/test_atomic.json")
        def worker(idx):
            atomic_write_json(target, {"worker_id": idx})

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(target.exists())
        target.unlink(missing_ok=True)
        target.with_suffix(".json.bak").unlink(missing_ok=True)
        target.with_suffix(".json.lock").unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
```

---

## 10. `build.spec` — PyInstaller 打包（`upx=False` 防杀软误报 + 英文内部构建名）

> **防误报与路径兼容说明**：`upx=False` 可显著降低 Windows Defender / 360 等杀毒软件将 PyInstaller 打包程序误判为木马的概率；`name='MultiTableWorkbench'` 采用纯英文 ASCII 构建名，避免部分 Windows 环境或批处理调用链下的中文路径编码冲突（打包完成后可为生成的 `.exe` 创建中文快捷方式）。

```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('core', 'core'), ('data_engine', 'data_engine'), ('office_engine', 'office_engine'), ('ui', 'ui')],
    hiddenimports=['customtkinter', 'openpyxl', 'pandas', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MultiTableWorkbench',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```
