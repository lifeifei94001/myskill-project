# Web 工作台 · Vercel + GitHub + Turso（+ 按需 Cloudflare R2）云端双模九条避坑铁律

适用：Web 工作台需要**零成本上云**（GitHub 推送 → Vercel 自动部署 → Turso 云数据库 + 按需 Cloudflare R2 对象存储），或把本地项目迁移上云。

同一套代码自适应两种运行形态：

| 形态 | 触发条件 | 结构化数据库 | 文件处理与存储 |
|---|---|---|---|
| **本地 / 局域网** | 未配置 `TURSO_DATABASE_URL` | `SQLite WAL`（`backend/app.db`，带 `shm` 探针容错） | 默认 `BytesIO` 内存流；需归档时存本地 `storage/` |
| **Vercel 云端** | 检测到 `VERCEL` 环境变量 + 配置了 Turso | `Turso HTTP /v2/pipeline`（零编译纯 Python 驱动） | 临时中转写 `/tmp/storage`；需永久归档且配置了 `R2_*` 时自动直传 **Cloudflare R2** |

---

## 九条云端避坑铁律（不可协商）

### 铁律 1：零编译纯 Python Turso HTTP (`/v2/pipeline`) 驱动 + SQLite WAL 探针防呆
- **原因**：`sqlalchemy-libsql` / `libsql-experimental` 依赖 Rust C 扩展，Windows 缺 wheel 装不上，Vercel Python 3.12+ 容器也常触发 Cargo 编译失败；此外部分 Docker 挂载卷不支持 `shm` 共享内存，强开 `WAL` 会抛 `disk I/O error`。
- **做法**：`requirements.txt` 严禁写这两个包；在 `backend/database.py` 内置基于 `requests.Session()`（Keep-Alive 复用）的 PEP 249 驱动 `TursoHttpConnection` + `TursoHttpCursor`（配 `poolclass=NullPool`）；本地 SQLite 开启 `WAL` 时加入探针异常捕获，若报 `OperationalError` 自动降级为 `DELETE` 日志模式。

### 铁律 2：时间字段一律 `Optional[str]`，严禁使用 `datetime`
- **原因**：SQLite/Turso 底层存文本，读回时 SQLAlchemy 解析成无时区 `NaiveDatetime`，新版 `sqlmodel`/`pydantic` 校验崩溃会导致**所有查询接口报 HTTP 500**。
- **做法**：
  ```python
  def utc_now_str() -> str:
      return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

  created_at: Optional[str] = Field(default_factory=utc_now_str)
  ```

### 铁律 3：批量写入 = 多值 `INSERT VALUES` 展开（上限 900 参数）+ 单条真实 `lastrowid` + `_pending_writes` 单事务原子缓冲
- **原因**：1,500 条单行 `INSERT` 在 Turso 是 1,500 次网络往返（耗时 15~25s）；若先 `DELETE` 旧数据再超时，线上表会被清空归零；同时若单条 ORM `INSERT` 使用伪造的合成 ID，`session.refresh(obj)` 会读回错误行。
- **做法**：
  1. `executemany` 用正则 `_MULTI_INSERT_RE` 识别 `INSERT [OR ...] INTO t (...) VALUES (?, ...)`，按块合并为 `VALUES (...), (...)`。**每块行数严格统一为 `max(1, min(120, 900 // cols_per_row))`**（兼容 SQLite 999 绑定参数上限，严禁写成 1800）。
  2. 同一请求内的 `DELETE / UPDATE` 与 `executemany` 批量插入暂存于 `_pending_writes`；**单条 `INSERT` 连同已缓冲写入一起包裹在 `BEGIN … COMMIT` 中 1 次 POST 提交**，以拿到服务端真实 `last_insert_rowid` 供 `session.refresh(obj)` 使用；遇到 `SELECT` 或 `session.commit()` 时自动将缓冲队列打包为 **1 次 HTTP POST** 原子提交。

### 铁律 4：Vercel 只读文件系统防护，写操作一律走 `/tmp`
- **做法**：`IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))`，临时目录路由至 `/tmp/storage`，未配 Turso 时的兜底 SQLite 指向 `/tmp/app.db`（注意 `/tmp` 实例回收即丢，需持久化的数据必须进 Turso 或 R2）。

### 铁律 5：Serverless 依赖极简瘦身（剔除 165MB+ 的 `pandas/numpy` 与 `boto3`）
- **做法**：常规业务 Excel/CSV 导入导出固定 7 个核心包（`<25MB`）：
  ```txt
  fastapi>=0.110.0
  uvicorn>=0.28.0
  sqlmodel>=0.0.16
  python-multipart>=0.0.9
  openpyxl>=3.1.2
  requests>=2.31.0
  python-dotenv>=1.0.0
  ```
  读取用 `openpyxl.load_workbook(BytesIO(raw), read_only=True, data_only=True)`；导出用 `BytesIO` + `StreamingResponse` + RFC 5987 UTF-8 文件名头 `make_download_headers(filename)`。

### 铁律 6：环境变量与 Turso JWT 唯一防呆清洗函数（且不在报错中回显 Token 字符）
- **做法**：全局仅在 `backend/database.py` 维护**唯一一份** `_get_clean_env`、`_normalize_turso_host` 与 `_extract_clean_jwt`（其他模块如 `r2_storage.py` 直接 `from database import _get_clean_env`，避免两份实现不一致）；自动剥离反引号、引号、空格；HTTP 400/401/403 时抛出中文排障提示（仅输出“是否以 `eyJ` 开头 + 长度”，**绝不回显 Token 任何字符**）。

### 铁律 7：全局 JSON 异常拦截 + `sys.path` 注入 + `lifespan` 幂等冷启动自检
1. `main.py`、`database.py` 顶部注入 `sys.path.insert(0, str(Path(__file__).resolve().parent))`。
2. 使用 `@asynccontextmanager async def lifespan(app: FastAPI):`（替代已弃用的 `@app.on_event("startup")`）并在 `lifespan` 与 `get_session()` 中双保险调用幂等 `ensure_db_ready()`（先查 `sqlite_master` 表数量，仅空库首次启动时建表+批量预热种子数据）。

### 铁律 8：算法防超时 + 查询合并 + `vercel.json` 路由规范
- 双重循环内禁止重复正则清洗或新建 `SequenceMatcher`（清洗函数加 `@lru_cache(maxsize=16384)`、循环外按品牌分桶预计算候选池、复用 `set_seq2()`）；
- `frontend/package.json` 的 `"build"` 写为 `"vite build"`（将 `vue-tsc --noEmit` 拆到 `"type-check"`）。

### 铁律 9：5GB 数据库存储配额红线 + 按需启用零依赖 Cloudflare R2 对象存储
- **为什么默认用 Turso 而不是 Cloudflare D1**：从 Vercel 外部调 D1 只能走 REST API（受全局频率限制且免费版每天限写 10 万行，超限当天直接停服）；Turso 支持 `/v2/pipeline` 单次请求打包上千条 SQL，故**结构化数据库默认首选 Turso**。
- **5GB 配额保护**：Turso 免费空间仅 **5GB**，**严禁将原始 Excel 二进制（BLOB）或图片存入数据库**；重复上传刷新的数据表提供按批次覆盖或旧批次清理接口。
- **Cloudflare R2 按需介入准则（非必要不启用）**：
  - **常规场景（90% 项目）**：上传 Excel 解析入库 → 导出新表，全程用 `io.BytesIO` 内存流处理，**不生成 `r2_storage.py`**。
  - **必要场景（需留存原始文件凭证/历史归档包）**：仅当业务明确要求原样留档上传文件或附件时，生成 `backend/r2_storage.py`（使用标准库 `hmac/hashlib` 实现 AWS SigV4 签名直传 Cloudflare R2 免费 10GB 存储，零 `boto3` 依赖）。

---

## 核心代码模板（唯一权威实现，已通过端到端冒烟测试）

### 1. `backend/database.py` — 双模自适应存储引擎（本地 SQLite WAL 探针 + 云端 Turso HTTP Pipeline）

```python
import base64
import os
import re
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

import requests
from sqlalchemy import event, insert as sa_insert, text
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
STORAGE_DIR = Path("/tmp/storage") if IS_VERCEL else (BASE_DIR / "storage")
try:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    STORAGE_DIR = Path("/tmp/storage")
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

_JWT_RE = re.compile(r"(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)")
_MULTI_INSERT_RE = re.compile(
    r"^\s*(INSERT\s+(?:OR\s+\w+\s+)?INTO\s+[^\(\s]+\s*\([^\)]+\)\s*VALUES\s*)\(([^\)]+)\)\s*;?\s*$",
    re.IGNORECASE | re.DOTALL,
)


def _strip_clean(v: str) -> str:
    return (v or "").strip().strip("`'\"").strip()


def _get_clean_env(key_name: str) -> str:
    """全局唯一环境变量提纯函数：兼容变量名或值误带反引号、引号、空格的情况"""
    if key_name in os.environ:
        val = _strip_clean(os.environ[key_name])
        if val:
            return val
    for k, v in os.environ.items():
        if _strip_clean(k) == key_name:
            return _strip_clean(v)
    return ""


def _normalize_turso_host(raw_url: str) -> str:
    u = _strip_clean(raw_url)
    for prefix in ("sqlite+libsql://", "libsql://", "turso://", "wss://", "ws://", "https://", "http://"):
        if u.lower().startswith(prefix):
            u = u[len(prefix):]
            break
    if "?" in u:
        u = u.split("?", 1)[0]
    for suffix in ("/v2/pipeline", "/v2", "/"):
        if u.endswith(suffix):
            u = u[: -len(suffix)]
    return u.strip("/")


def _extract_clean_jwt(raw_token: str) -> str:
    t = _strip_clean(raw_token)
    m = _JWT_RE.search(t)
    return m.group(1) if m else t


def expand_multi_insert(sql: str, rows: List[Any], max_rows: int = 120) -> List[Tuple[str, List[Any]]]:
    """
    将 executemany 的单行 INSERT 展开为多值 VALUES (...), (...)，
    每块行数严格遵循 max(1, min(120, 900 // cols_per_row))，兼容 SQLite 999 绑定参数上限。
    """
    m = _MULTI_INSERT_RE.match(sql.strip())
    if not m or not rows or isinstance(rows[0], dict):
        return [(sql, list(r) if not isinstance(r, dict) else r) for r in rows]
    prefix_sql = m.group(1)
    placeholders_one = f"({m.group(2).strip()})"
    cols_per_row = max(1, placeholders_one.count("?") or len(rows[0]))
    rows_per_stmt = max(1, min(max_rows, 900 // cols_per_row))
    out: List[Tuple[str, List[Any]]] = []
    for i in range(0, len(rows), rows_per_stmt):
        chunk = rows[i : i + rows_per_stmt]
        multi_sql = prefix_sql + ", ".join([placeholders_one] * len(chunk))
        flat_args = [p for row_params in chunk for p in row_params]
        out.append((multi_sql, flat_args))
    return out


class TursoHttpCursor:
    """PEP 249 兼容游标：支持 900 参数上限多行 VALUES 自动合并、单条真实 lastrowid 与事务写缓冲"""

    def __init__(self, conn: "TursoHttpConnection") -> None:
        self.conn = conn
        self.description: Optional[Tuple[Tuple[Any, ...], ...]] = None
        self.rowcount: int = -1
        self.lastrowid: Optional[int] = None
        self._rows: List[Tuple[Any, ...]] = []
        self._pos: int = 0
        self.arraysize: int = 1

    @staticmethod
    def _encode_arg(val: Any) -> Dict[str, Any]:
        if val is None:
            return {"type": "null"}
        if isinstance(val, bool):
            return {"type": "integer", "value": "1" if val else "0"}
        if isinstance(val, int):
            return {"type": "integer", "value": str(val)}
        if isinstance(val, float):
            return {"type": "float", "value": float(val)}
        if isinstance(val, datetime):
            return {"type": "text", "value": val.strftime("%Y-%m-%d %H:%M:%S")}
        if isinstance(val, date):
            return {"type": "text", "value": val.isoformat()}
        if isinstance(val, (bytes, bytearray, memoryview)):
            return {"type": "blob", "base64": base64.b64encode(bytes(val)).decode("ascii")}
        return {"type": "text", "value": str(val)}

    @staticmethod
    def _decode_cell(cell: Dict[str, Any]) -> Any:
        t = cell.get("type")
        if t == "null" or t is None:
            return None
        if t == "integer":
            return int(cell["value"])
        if t == "float":
            return float(cell["value"])
        if t == "blob":
            return base64.b64decode(cell.get("base64", ""))
        return str(cell.get("value", ""))

    def _build_stmt(self, sql: str, parameters: Any = None) -> Dict[str, Any]:
        stmt: Dict[str, Any] = {"sql": sql}
        if parameters:
            if isinstance(parameters, dict):
                stmt["named_args"] = [{"name": k, "value": self._encode_arg(v)} for k, v in parameters.items()]
            else:
                stmt["args"] = [self._encode_arg(p) for p in parameters]
        return stmt

    def execute(self, sql: str, parameters: Any = None) -> "TursoHttpCursor":
        sql_upper = sql.strip().upper()
        if any(sql_upper.startswith(p) for p in (
            "PRAGMA JOURNAL_MODE", "PRAGMA SYNCHRONOUS", "PRAGMA CACHE_SIZE",
            "PRAGMA BUSY_TIMEOUT", "BEGIN", "COMMIT", "ROLLBACK"
        )):
            self.description = None
            self.rowcount = 0
            self._rows = []
            self._pos = 0
            return self

        stmt = self._build_stmt(sql, parameters)
        no_ret = "RETURNING " not in sql_upper
        if no_ret and sql_upper.startswith(("DELETE ", "UPDATE ")):
            self.conn._pending_writes.append({"type": "execute", "stmt": stmt})
            self.description = None
            self._rows = []
            self._pos = 0
            self.rowcount = 1
            return self

        if no_ret and sql_upper.startswith("INSERT "):
            # 单条 INSERT 必须拿到服务端真实 last_insert_rowid（供 ORM session.refresh 使用）
            batch = (
                [{"type": "execute", "stmt": {"sql": "BEGIN"}}]
                + self.conn._pending_writes
                + [{"type": "execute", "stmt": stmt}, {"type": "execute", "stmt": {"sql": "COMMIT"}}]
            )
            self.conn._pending_writes = []
            all_res = self.conn._send_pipeline(batch)
            res = all_res[-2] if len(all_res) >= 2 else {}
            self.description = None
            self._rows = []
            self._pos = 0
            self.rowcount = int(res.get("affected_row_count") or 0)
            last_id = res.get("last_insert_rowid")
            self.lastrowid = int(last_id) if (last_id is not None and str(last_id) != "") else None
            return self

        if self.conn._pending_writes:
            batch_reqs = (
                [{"type": "execute", "stmt": {"sql": "BEGIN"}}]
                + self.conn._pending_writes
                + [{"type": "execute", "stmt": {"sql": "COMMIT"}}, {"type": "execute", "stmt": stmt}]
            )
            self.conn._pending_writes = []
            all_res = self.conn._send_pipeline(batch_reqs)
            res = all_res[-1] if all_res else {}
        else:
            res = self.conn._send_pipeline([{"type": "execute", "stmt": stmt}])[0]

        cols = res.get("cols") or []
        self.description = tuple((c.get("name", ""), None, None, None, None, None, None) for c in cols) if cols else None
        self._rows = [tuple(self._decode_cell(c) for c in r) for r in (res.get("rows") or [])]
        self._pos = 0
        self.rowcount = int(res.get("affected_row_count") or 0)
        last_id = res.get("last_insert_rowid")
        self.lastrowid = int(last_id) if (last_id is not None and str(last_id) != "") else None
        return self

    def executemany(self, sql: str, seq_of_parameters: Iterable[Any]) -> "TursoHttpCursor":
        params_list = list(seq_of_parameters)
        if not params_list:
            return self
        for chunk_sql, chunk_args in expand_multi_insert(sql, params_list, max_rows=120):
            self.conn._pending_writes.append({"type": "execute", "stmt": self._build_stmt(chunk_sql, chunk_args)})
        self.rowcount = len(params_list)
        return self

    def fetchone(self):
        if self._pos >= len(self._rows):
            return None
        row = self._rows[self._pos]
        self._pos += 1
        return row

    def fetchall(self):
        rows = self._rows[self._pos :]
        self._pos = len(self._rows)
        return rows

    def fetchmany(self, size: Optional[int] = None):
        sz = size if size is not None else self.arraysize
        rows = self._rows[self._pos : self._pos + sz]
        self._pos += len(rows)
        return rows

    def close(self) -> None:
        self._rows = []
        self._pos = 0


class TursoHttpConnection:
    def __init__(self, pipeline_url: str, auth_token: str, http_session: requests.Session) -> None:
        self.pipeline_url = pipeline_url
        self.auth_token = auth_token
        self.http_session = http_session
        self.isolation_level = None
        self._pending_writes: List[Dict[str, Any]] = []

    def _send_pipeline(self, execute_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        payload = {"requests": execute_requests + [{"type": "close"}]}
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        resp = self.http_session.post(self.pipeline_url, json=payload, headers=headers, timeout=45)
        if resp.status_code != 200:
            err_body = resp.text[:300]
            if "JWT" in err_body or resp.status_code in (400, 401, 403):
                token_state = ("已填写且形如 JWT" if self.auth_token.startswith("eyJ") else "已填写但非 eyJ 开头") if self.auth_token else "为空"
                raise sqlite3.OperationalError(
                    f"Turso 认证令牌 (TURSO_AUTH_TOKEN) 校验未通过 (当前状态: {token_state}，长度 {len(self.auth_token)})。"
                    f"请确认填入的是以 eyJ 开头的 Token（而非 libsql:// 数据库地址），修改后需点击 Redeploy！原始响应: {err_body}"
                )
            raise sqlite3.OperationalError(f"Turso 响应异常 (HTTP {resp.status_code}): {err_body}")
        data = resp.json()
        out: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            if item.get("type") == "error":
                raise sqlite3.DatabaseError(f"Turso SQL 错误: {(item.get('error') or {}).get('message')}")
            resp_obj = item.get("response") or {}
            if resp_obj.get("type") == "execute":
                out.append(resp_obj.get("result") or {})
        return out

    def flush_writes(self) -> None:
        if not self._pending_writes:
            return
        writes = self._pending_writes
        self._pending_writes = []
        batch = [{"type": "execute", "stmt": {"sql": "BEGIN"}}] + writes + [{"type": "execute", "stmt": {"sql": "COMMIT"}}]
        self._send_pipeline(batch)

    def cursor(self) -> TursoHttpCursor:
        return TursoHttpCursor(self)

    def commit(self) -> None:
        self.flush_writes()

    def rollback(self) -> None:
        self._pending_writes = []

    def close(self) -> None:
        if self._pending_writes:
            try:
                self.flush_writes()
            except Exception:
                self._pending_writes = []

    def create_function(self, *args: Any, **kwargs: Any) -> None:
        pass


TURSO_DATABASE_URL = _get_clean_env("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = _extract_clean_jwt(_get_clean_env("TURSO_AUTH_TOKEN"))

if TURSO_DATABASE_URL:
    _clean_host = _normalize_turso_host(TURSO_DATABASE_URL)
    _scheme = "http" if _clean_host.startswith(("127.0.0.1", "localhost")) else "https"
    _pipeline_url = f"{_scheme}://{_clean_host}/v2/pipeline"
    _http_session = requests.Session()
    engine = create_engine(
        "sqlite://",
        creator=lambda: TursoHttpConnection(_pipeline_url, TURSO_AUTH_TOKEN, _http_session),
        poolclass=NullPool,
    )
else:
    DB_PATH = Path("/tmp/app.db") if IS_VERCEL else (BACKEND_DIR / "app.db")
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_wal(dbapi_conn: Any, _) -> None:
        cur = dbapi_conn.cursor()
        try:
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("SELECT name FROM sqlite_master LIMIT 1;")
        except sqlite3.OperationalError:
            try:
                cur.execute("PRAGMA journal_mode=DELETE;")
            except Exception:
                pass
        try:
            cur.execute("PRAGMA synchronous=NORMAL;")
            cur.execute("PRAGMA busy_timeout=5000;")
        except Exception:
            pass
        cur.close()


def bulk_insert_models(session: Session, model_cls: Any, records: List[Dict[str, Any]]) -> None:
    if not records:
        return
    for r in records:
        for k, v in r.items():
            if isinstance(v, datetime):
                r[k] = v.strftime("%Y-%m-%d %H:%M:%S")
    session.execute(sa_insert(model_cls), records)


_db_initialized = False


def ensure_db_ready() -> None:
    """幂等冷启动数据库自检：先查 sqlite_master，仅当表不存在时执行建表"""
    global _db_initialized
    if _db_initialized:
        return
    try:
        with Session(engine) as session:
            table_names = list(SQLModel.metadata.tables.keys())
            if table_names:
                placeholders = ", ".join(f"'{name}'" for name in table_names)
                cnt = session.exec(
                    text(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ({placeholders})")
                ).one()
                existing_count = cnt[0] if isinstance(cnt, tuple) else int(cnt)
                if existing_count < len(table_names):
                    SQLModel.metadata.create_all(engine)
            else:
                SQLModel.metadata.create_all(engine)
        _db_initialized = True
    except Exception:
        SQLModel.metadata.create_all(engine)
        _db_initialized = True


def get_session() -> Generator[Session, None, None]:
    ensure_db_ready()
    with Session(engine) as session:
        yield session
```

### 2. `backend/r2_storage.py` — 按需启用的零依赖 Cloudflare R2 对象存储适配器（仅在项目需长期归档原文件时生成）

```python
import datetime
import hashlib
import hmac
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests
from database import STORAGE_DIR, _get_clean_env

R2_ACCOUNT_ID = _get_clean_env("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = _get_clean_env("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = _get_clean_env("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = _get_clean_env("R2_BUCKET_NAME")

R2_ENABLED = bool(R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY and R2_BUCKET_NAME)


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key: str, date_stamp: str, region: str = "auto", service: str = "s3") -> bytes:
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    return _sign(k_service, "aws4_request")


def _r2_request(method: str, object_key: str, data: bytes = b"", content_type: str = "application/octet-stream") -> requests.Response:
    host = f"{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    canonical_uri = f"/{R2_BUCKET_NAME}/{quote(object_key.lstrip('/'), safe='/~_.-')}"
    endpoint = f"https://{host}{canonical_uri}"

    now = datetime.datetime.now(datetime.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(data).hexdigest()

    headers = {
        "Host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
    }
    signed_headers_list = ["host", "x-amz-content-sha256", "x-amz-date"]
    if method in ("PUT", "POST"):
        headers["Content-Type"] = content_type
        signed_headers_list.insert(0, "content-type")

    signed_headers_list.sort()
    canonical_headers = "".join(f"{k}:{headers[[h for h in headers if h.lower() == k][0]]}\n" for k in signed_headers_list)
    signed_headers = ";".join(signed_headers_list)

    canonical_request = f"{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    credential_scope = f"{date_stamp}/auto/s3/aws4_request"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    signing_key = _get_signature_key(R2_SECRET_ACCESS_KEY, date_stamp)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    headers["Authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={R2_ACCESS_KEY_ID}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    return requests.request(method, endpoint, data=data if method in ("PUT", "POST") else None, headers=headers, timeout=30)


def save_archive_file(object_key: str, raw_bytes: bytes, content_type: str = "application/octet-stream") -> str:
    if R2_ENABLED:
        resp = _r2_request("PUT", object_key, data=raw_bytes, content_type=content_type)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Cloudflare R2 上传失败 (HTTP {resp.status_code}): {resp.text[:200]}")
        return f"r2://{R2_BUCKET_NAME}/{object_key}"
    local_path = STORAGE_DIR / Path(object_key).name
    local_path.write_bytes(raw_bytes)
    return str(local_path)


def load_archive_file(object_key: str) -> Optional[bytes]:
    if R2_ENABLED:
        resp = _r2_request("GET", object_key)
        if resp.status_code == 200:
            return resp.content
        return None
    local_path = STORAGE_DIR / Path(object_key).name
    return local_path.read_bytes() if local_path.exists() else None
```

### 3. `vercel.json`（推荐 Preset 选 `Other`）

```json
{
  "version": 2,
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/static-build", "config": { "distDir": "dist" } },
    {
      "src": "backend/main.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 60,
        "excludeFiles": "{frontend/**,node_modules/**,.git/**,storage/**,*.db,*.db-*}"
      }
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/main.py" },
    { "src": "/assets/(.*)", "dest": "frontend/assets/$1" },
    { "src": "/(.*\.(js|css|ico|png|jpg|jpeg|svg|json|woff2?|ttf))", "dest": "frontend/$1" },
    { "src": "/(.*)", "dest": "frontend/index.html" }
  ]
}
```

---

### 4. 黄金搭档自动化部署交付 SOP（无缝联动 `deploy-to-vercel`）

当全栈代码（Vue3 + FastAPI + Turso + `vercel.json`）编写完成且自检通过后，**不再让用户自行手动操作网页控制台**，而是直接激活 **`deploy-to-vercel`** 技能执行端到端交付闭环：

1. **步骤 1：状态与环境探测**
   - 检查 Git 远端：`git remote get-url origin`
   - 检查本地是否已关联项目：`cat .vercel/project.json` 或 `cat .vercel/repo.json`
   - 检查 Vercel CLI 认证：`vercel whoami`
   - 获取可用团队：`vercel teams list --format json`

2. **步骤 2：环境与团队确认**
   - 若关联多个团队，展示点选列表让用户确认；若单账号或已关联则直接推进。
   - 提醒用户在 Vercel 项目环境变量中确认已填入 `TURSO_DATABASE_URL` 与 `TURSO_AUTH_TOKEN`（若用了 Cloudflare R2，还需填入 `R2_*` 配置）。

3. **步骤 3：触发自动化部署**
   - **已关联 Git 仓库**：征询用户确认后执行 `git add . && git commit -m "feat: complete web workbench" && git push`，触发 Vercel 自动化构建。
   - **未关联 Git / 快速预览**：执行 `vercel deploy -y --no-wait --scope <team-slug>` 极速生成 Preview 构建。

4. **步骤 4：域名与健康状态回传**
   - 调用 `vercel ls --format json` 抓取最新构建的 Deployment URL。
   - 若部署失败或需排障，调用 `vercel inspect <url>` 查询构建日志。
   - 最终向用户回传完整的可访问地址与部署交付报告，完成从“需求提出”到“线上可用”的 100% 闭环。
