# 本地工具链与插件协同检索指南 (Toolchain & Plugin Integration)

为了彻底解决“图片打不开、404、500 Whitelabel 报错、图片链接幻觉”等问题，`laptop-specs-collector` 与本地反重力环境中的工具及插件进行深度联动，构建自动化图片探测与抓取链路。

---

## 一、 推荐协同插件与 Skill 矩阵

| 工具/Skill 名称 | 类型 | 适用场景 | 核心调用命令与能力 |
|---|---|---|---|
| **`tavily-search-pro`** | 搜索增强 Skill | 快速批量抓取真实图片 CDN | `python {tavily}/lib/tavily_search.py search "<机型> 官网/ZOL" --images`<br>👉 **自带 `--images` 模式，直接返回真实 CDN 图片 URL 列表** |
| **`chrome-devtools-plugin`** | 官方 MCP 插件 | 真实浏览器直驱，抓取 DOM 真实 `src` | 通过 Chrome DevTools MCP 打开 ZOL 或官网，执行 `evaluate_script` 提取高保真白底大图 |
| **`agent-browser`** | 自动化浏览器 CLI | 高性能无头浏览器交互 | `agent-browser open <url>` + `agent-browser get attr @element "src"` |
| **`anysearch`** | 搜索引擎 Skill | 网页内容与 DOM 抽取 | `python {anysearch}/scripts/anysearch_cli.py extract "<url>"` 直接提取页面图片与内容 |

---

## 二、 自动化采集与验证链路 (Pipeline)

```
用户输入：笔记本机型（如：拯救者 Y9000P 2026）
                │
                ▼
【步骤 1：调用 Tavily --images 或 浏览器工具定位真实图源】
优先执行：
`tavily_search.py search "联想 拯救者 Y9000P 2026 外观白底图" --images`
或通过 Chrome DevTools 直接进入 `detail.zol.com.cn` 产品图库
                │
                ▼
【步骤 2：提取真实带 Hash 的 CDN 图片直链】
从真实页面中提取：
- 正视展开图（包含 B面屏 + C面键盘）
- 斜后/背视展开图（包含 A面LOGO + 尾部出风口）
严禁任何拼凑构造虚假 URL！
                │
                ▼
【步骤 3：注入防盗链保护并格式化】
在 Markdown/HTML 中统一添加 `referrerpolicy="no-referrer"`
                │
                ▼
【步骤 4：交付黄金组合】
成套输出：白底双图预览 + 官方图库直达 + 8列真实配置表 + 上市时间 + 后台录入卡
```

---

## 三、 Tavily Search Pro 联动示范

当配置有 `TAVILY_API_KEY` 时，直接在终端中运行：
```bash
python d:\APP\development_projects\.agents\skills\tavily-search-pro\lib\tavily_search.py search "联想 拯救者 R9000X 2026款 外观 官方渲染图" --images
```
返回输出：
```text
Images:
- https://2b.zol-img.com.cn/product/275_800x600/415/ceLTP4WNBlRg.jpg
- https://img14.360buyimg.com/n1/s800x800_jfs/t1/...
```
这些抓取到的 URL 是搜索引擎从目标页面 DOM 中直接提取的，保证 100% 真实存在，绝无拼凑臆测。
