---
name: huishoubao-pricing
description: "Query recycled phone and device buyback prices from Huishoubao (回收宝, ka.huishoubao.com & WeChat Mini Program). Use when the user wants to check recycle prices, base valuations, or batch quotes for smartphones (iPhone, Android) on 回收宝, especially for '过保' (out-of-warranty) and '完美' (flawless) conditions. Triggers on: '回收宝价格', '回收宝查价', '回收宝估价', '爬取回收宝', 'huishoubao pricing'."
---

# Huishoubao (回收宝) Device Pricing Skill

## 0. ⚡ 新会话极速执行路径 (Fast-Path)

当用户在新会话中要求**查询回收宝微信小程序（C 端散客，过保+完美不加券）价格**时，**禁止重复抓包或额外编写内存/参数测试脚本**，直接执行以下步骤即可在 **~1 分钟内**完成全部 18 款报价：

1. 确认用户已在电脑微信中打开“回收宝”小程序（已登录即可，不需手动开启代理）；
2. **直接运行一体化脚本**：
   ```bash
   python d:\APP\development_projects\evaluate_all_18_miniprogram.py
   ```
   - 脚本内置 `0.5 秒`极速微信进程 `token` & 版本号探测、本地问卷参数缓存（[`mp_params_cache.json`](file:///d:/APP/development_projects/.agents/skills/huishoubao-pricing/scripts/mp_params_cache.json)）以及当日结果断点续传；
   - 默认不请求冗余查券接口，仅发起 18 次直连估价，约 **55~65 秒**一次性输出全部报价与 CSV/JSON 文件。
3. （可选）仅校验新机型或更新问卷参数时使用：`python d:\APP\development_projects\evaluate_all_18_miniprogram.py --dry-run --refresh-params`（不消耗每日估价额度）。

---

## 1. 概述与双渠道架构 (Overview & Dual-Channel Architecture)

回收宝官方目前存在两套估价价格体系，价格差异显著：

| 渠道分类 | 业务定位 | 核心域名与标识 | 价格特征 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **渠道 A：KA 商户渠道** | B2B 大客户/批发渠道结算 | `ka.huishoubao.com`<br>`platform: 1`, `pid: 1004` | **批发底价**（无补贴券，价格较低） | 商家批量结算、回收商同行批发底线 |
| **渠道 B：微信小程序端** | B2C 面向普通散客零售回收 | `wx8b5362b3e90cd150`<br>`platform: 2`, `pid: 1196` | **零售溢价 + 补贴券**（纯本机估价高出 **17%~33%**，平均高出 **20.5%**，外加 100~450 元不等的平台加价券） | C 端散客比价、客户前端参考价 |

### 典型机型两端价格对比样例（过保 + 完美成色）

- **iPhone 16e 128G 黑色**：
  - KA 商户底价：**¥1,483.00**
  - 微信小程序纯本机估价：**¥1,883.00**（相比商户溢价 **+¥400.00 / +27.0%**）
  - 微信小程序加券总价：**¥2,003.00**（含平台回收补贴券 ¥120.00）
- **iPhone 16e 512G 黑色**：
  - KA 商户底价：**¥2,734.00**
  - 微信小程序纯本机估价：**¥3,394.00**（相比商户溢价 **+¥660.00 / +24.1%**）
- **iPhone 15 Plus 512G 粉色**：
  - KA 商户底价：**¥2,250.00**
  - 微信小程序纯本机估价：**¥2,632.00**（相比商户溢价 **+¥382.00 / +17.0%**）
- **iPhone 17 Pro Max 256G 银色**：
  - 微信小程序纯本机估价：**¥5,362.00**
  - 微信小程序加券总价：**¥5,792.00**（含平台回收补贴券 ¥430.00）

---

## 2. 微信小程序端核心接口与逆向协议 (WeChat Mini Program API)

### 2.1 协议基础信息
- **加盐密钥 (Secret)**: `'b7cab12b2b81385dd2cccb8ce67e4998'`
- **AppID**: `wx8b5362b3e90cd150`
- **版本号 (Version)**: 默认 `V5.17.16`（脚本运行时自动从 `WeChatAppEx.exe` 内存探测当前最新活跃版本与 `token`）
- **平台标识 (Platform)**: `'2'`
- **渠道商编号 (PID)**: `'1196'`
- **网关主机**: `https://api.huishoubao.com`

### 2.2 核心接口
1. **获取机型评估问卷参数**:
   - `POST https://api.huishoubao.com/api/product/getEvaluateParam`
   - 参数：`productId=<pid>`
2. **提交评估并计算估价**:
   - `POST https://api.huishoubao.com/api/product/evaluate`
   - 参数：`productId=<pid>`, `select=<json_array_str>`
   - 返回：`evaluateid`（估价单号）、`quotation`（纯本机报价，单位：分）
3. **获取券后总价与补贴详情**:
   - `POST https://api.huishoubao.com/api/product/getEvaluateResult`
   - 参数：`evaluateid=<evaluateid>`
   - 返回：`total`（券后到手总价）、`couponMoney`（回收补贴加价券金额）

### 2.3 必须携带的客户端请求头
小程序后端对来源 Referer 和 User-Agent 进行严格检验，脚本必须携带：
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat',
    'Referer': 'https://servicewechat.com/wx8b5362b3e90cd150/148/page-frame.html',
    'Content-Type': 'application/x-www-form-urlencoded'
}
```

### 2.4 签名算法 (SHA1 Signature)
1. 合并 Query 参数与 Form Body 参数，补充毫秒时间戳 `t` 与 `timestamp`、随机 32 位十六进制 `ukey`；
2. 过滤掉 `sign`、`images` 与空值字段；
3. 将所有键名按 ASCII 字典升序排列，拼接成字符串 `k1v1k2v2...`；
4. 末尾追加 `Secret`（`b7cab12b2b81385dd2cccb8ce67e4998`）；
5. 计算 SHA1 哈希并转换为小写十六进制字符串，赋值给 `sign`。
> **注意**：`select` 字段中的 JSON 字符串严禁包含空格，必须采用 `json.dumps(ids, separators=(',', ':'))`。

---

## 3. 风控防爬与账号配额保护 (Anti-Bot & Account Quota)

- **账号级/单日配额限制**：回收宝的 `api/product/evaluate` 对同一用户账号（`uid`）在短时间内的连续批量评估设有严格次数上限，且**微信小程序端（`pid=1196`）与 KA 网页端（`pid=1004`）共享同一账号的风控状态**；
- **风控兜底表现**：
  - 接口层面：`api/product/evaluate` 仍返回 `_errCode: "0"`，但内容变为兜底报废响应 `evaluateid: "0", quotation: "5"`；
  - 小程序 UI 层面：页面带着 `evaluateid=0` 跳转到报价页后调用 `getEvaluateResult`，会触发弹窗报错 **`提示：参数evaluateid不能为空或者有误`**（即使手动操作小程序也会被拦截，单靠在 UI 内重新点击“查看预估价格”无法解除风控）；
- **规避与恢复方式**：
  - 请求间隔建议拉长至 **3.5~5 秒以上**，并在**仅查不加券纯本机价**时跳过冗余的 `getEvaluateResult` 请求、按 `productId` 缓存 `getEvaluateParam`，可将单次批量 18 款的请求总量减半（实测 **18/18 全部稳定通过**，未触发风控）；
  - 若当前账号已触发限制，需**切换另一个未受限的微信/手机号登录**，或等待服务端风控冷却（通常按自然日/24 小时重置）；
- **按日增量断点续查机制**：评估脚本内置按当日日期（`huishoubao_miniprogram_prices_<YYYYMMDD>.json`）的实时增量缓存，每评估完一款立即落盘，已成功获取今日报价的机型自动跳过，绝不混用往日价格或重复消耗配额。

---

## 4. 运行脚本 (Execution)

### 执行小程序 C 端批量估价
```bash
python d:\APP\development_projects\evaluate_all_18_miniprogram.py
```
- **输出成果**：
  - JSON 结构化数据：`huishoubao_miniprogram_prices_<YYYYMMDD>.json`
  - 带 UTF-8 BOM 的 Excel 兼容比价表：`huishoubao_miniprogram_prices_<YYYYMMDD>.csv`
