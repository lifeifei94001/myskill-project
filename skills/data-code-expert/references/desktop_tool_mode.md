# 桌面工具模式（原生 GUI 优先架构）

用于生成**可长期使用、可打包成 exe 发给同事**的桌面端小工具，而非一次性脚本。

**默认走原生 Python GUI 单进程方案，而不是前后端分离（HTTP 服务 + 浏览器渲染）。** 原生 GUI 只用一种语言、一个进程，不需要同时维护前后端两套逻辑，代码量更小、生成更省 token，也方便直接按需调用本地 WPS/Excel COM 接口。

---

## GUI 框架选型（默认优先 CustomTkinter）

| 框架 | 什么情况下选它 | 依赖 | 打包体积/复杂度 |
|---|---|---|---|
| **CustomTkinter**（默认） | 绝大多数场景：要现代圆角深浅双模式 UI，同时开发快、打包快 | `pip install customtkinter` | 小，打包简单 |
| Tkinter | 用户明确要求“零第三方 GUI 依赖”“内网装不了包” | 标准库自带 | 最小 |
| PySide6（优先于 PyQt6） | 界面复杂（多停靠面板/树形专业表格），或要求商业软件级质感 | `pip install pyside6`（LGPL 可商用） | 较大（60~120MB） |
| Flet | 想要类似移动端 Material Design 质感 | `pip install flet` | 中等 |
| DearPyGui | 大量实时曲线刷新、高频渲染仪表盘 | `pip install dearpygui` | 小，GPU 加速 |
| wxPython | 要求 100% 原生 Windows 系统标准控件外观 | `pip install wxpython` | 较大 |

### 什么时候切换到 Web 模式

只有当用户明确要**浏览器访问 / 局域网多人同时协同 / 云端链接分享**时，才切换到：
- **生产级现代浏览器 Web 工作台**：读取 `references/web_workbench_mode.md` + `references/web_ui_glassmorphism.md`。
- **单脚本快速局域网上传下载**：若环境装有 `local-to-flask-web` 技能则直接用它。

---

## 开场提问：输出「结构化点选确认卡」（必须执行）

```markdown
做桌面小工具前，请确认以下关键选项（带 `●` 为为你预设的推荐默认项，直接回复 **“默认”** 或 **“1A 2B”** 即可）：

**1. 输入方式与数据源结构**
- `●` **A. 选择本地 Excel/CSV 文件批量解析处理（推荐默认）**
- `○` **B. 界面表单手动录入 + 选择 Excel 文件混合处理**
- `○` **C. 整个文件夹批量扫描处理**

**2. 参数字典库与本地记忆需求**
- `●` **A. 需要本地自学习字典库/配置记忆（推荐默认）**：支持界面新增/修改映射词条，采用跨进程文件锁 + `.bak` 备份原子落盘 `data/*.json`
- `○` **B. 纯粹“打开 → 计算 → 导出”无状态工具**：无需生成本地持久化字典文件

**3. 多表联动与本地 WPS/Excel 引擎策略**
- `●` **A. 纯 Python 极速内存模式（推荐默认）**：`fastexcel`/`python-calamine` 读取 + Python 核心计算 + `openpyxl`/`xlsxwriter` 输出，不依赖本地是否安装 Office
- `○` **B. Python 核心 + WPS 可选增强（`required=False`）**：Python 算完回填后，若本机有 WPS/Excel 则唤醒重算公式，没装则平稳降级交付纯 Python 结果
- `○` **C. Python 核心 + WPS 强依赖终审（`required=True`）**：必须刷新跨工作簿外部链接（`ChangeLink`）或原生公式重算成功才算完成，失败必须弹窗阻断告警

**4. GUI 框架与交付形态**
- `●` **A. CustomTkinter 现代深浅自适应界面 + 附带 PyInstaller 无控制台防误报打包配置 `build.spec`（推荐默认）**
- `○` **B. PySide6 专业级复杂表格工作台**
- `○` **C. 仅本机源码运行，无需打包 EXE 配置**
```

---

## 架构铁律（不可协商，生成代码前必须全部满足）

1. **模块化多文件工程**，固定分层：
   ```
   项目根/
   ├── main.py            # 入口：顶部 SafeWriter 重定向 stdout/stderr → 启动 GUI
   ├── config/             # 路径自适应（源码与 PyInstaller frozen 通用）与常量配置
   ├── core/               # ⭐ 核心业务逻辑（纯 Python，严禁 import win32com，方便单测与 Web 复用）
   ├── data_engine/        # 跨进程安全原子写入 atomic_io.py + 两趟严格表头匹配 excel_io.py
   ├── office_engine/      # 可选 Office 增强适配器（WPS COM A/B/C/D 四层唤醒驱动）
   ├── ui/                 # 界面模块（主窗口、事件防抖与 try/except 弹窗保护）
   ├── data/               # 本地字典库与 .bak 备份（仅在有状态需求时生成）
   ├── test_suite.py       # 独立单元测试（直接测 core/ 与并发原子写入，不依赖 GUI/Office）
   └── build.spec          # PyInstaller 打包配置（默认 upx=False 防杀软误报 + 英文内部构建名）
   ```
2. **耗时任务不阻塞主线程**：所有文件读写、批量计算、WPS COM 调用必须丢进后台 daemon 线程，通过 `app.after(0, ...)` 回到主线程更新 UI，且执行期间禁用按钮防连点重入。
3. **路径自适应**：统一走 `config/paths.py` 的 `get_base_dir()`（兼容 `getattr(sys, "frozen", False)`）。
4. **防崩溃加固**：① `main.py` 顶部用 `SafeWriter` 重定向 `sys.stdout`/`sys.stderr`（防止 `console=False` 下 `print` 引发 `AttributeError` 闪退）；② 每个 GUI 事件回调必须包 `try/except`，出错弹窗提示并写入日志。
5. **表头两趟严格全等匹配**：先精确匹配，再做 `NFKC` 全半角/去首尾空格归一化匹配；严禁用子串包含（防止“单价”误匹配“单价(含税)”），且遇到重复表头或归一化后冲突的表头直接报错阻断。
6. **字典库跨线程 + 跨进程并发安全**：`atomic_write_json` 必须同时持有 `threading.Lock()` 与基于 `.lock` 文件的跨进程系统文件锁（Windows `msvcrt.locking` / Unix `fcntl.flock`），写 `.tmp` → 备份 `.bak` → `os.replace` 原子替换（防用户多开两个 EXE 实例写坏字典库）。
7. **PyInstaller 防杀软误报与路径兼容**：`build.spec` 默认设置 `upx=False`（UPX 压缩壳是国内杀毒软件误报木马的头号诱因），EXE 内部构建名称使用英文 ASCII 标识符（交付说明里指导用户重命名或建中文快捷方式）。
8. **多表自动化核心解耦**：`core/` 严禁 `import win32com`；WPS 增强通过 `office_engine/wps_engine.py` 的 `apply_wps_enhancement(required=True/False)` 显式区分“锦上添花”与“强依赖”。

---

## 代码生成流程与输出格式

用户对开场点选卡回复后：
1. 先按 `references/risk_premortem.md` 输出**完整版逆向推演风险评估 + 开发方案 + 方案拍板点选卡**；
2. 用户确认方案后，读取 `references/desktop_app_architecture.md`，按以下顺序输出完整工程：
   - **① 依赖安装命令**（如 `pip install customtkinter openpyxl pandas fastexcel pywin32 pyinstaller`）
   - **② 需求与逆向推演防翻车落地对照表**（`R1~Rn → 具体落点文件与函数`）
   - **③ 完整工程文件**（按 `config/ → core/ → data_engine/ → office_engine/ → ui/ → main.py → test_suite.py → build.spec` 顺序给出）
   - **④ 运行、单测与防误报打包说明**
