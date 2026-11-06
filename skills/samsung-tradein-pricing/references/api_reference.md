# 三星商城以旧换新（闪回收合作通道）API 接口技术文档

本文档记录了三星商城官网（中国）以旧换新服务（由第三方“闪回收 SHANHS”提供支持）的底层 RESTful API 规范，用于免浏览器无头自动化高速估价。

---

## 1. 基础信息

- **API 域名**：`https://p1-smz-api-cdn.shop.samsung.com.cn`
- **服务提供商编码**：`SHANHS`
- **基准目标置换机型 SKU**：`SM-A5760DBBCHC`（Galaxy A57 5G，可用于通用置换基准）

---

## 2. 接口列表与规范

### 2.1 机型树查询（层级过滤）
- **接口路径**：`GET /tokocommercewebservices/v2/cn/tradeIn/services/filterDevicesV2`
- **参数说明**：
  - `q`：层级查询表达式。格式为 `category:value[:category:value...]`
    - `q=`：返回顶级设备类别（手机 `1`、平板 `2`、智能手表 `5`、手环 `33`）
    - `q=deviceType:1`：返回品牌列表（苹果 `10`、三星 `20`、小米 `110`、华为 `100` 等）
    - `q=deviceType:1:brand:10`：返回品牌下系列列表（数字系列 `27_SE`、X系列 `26_SE`、SE系列 `25_SE`）
    - `q=deviceType:1:brand:10:series:27_SE`：返回该系列下所有具体机型（包含 `code` 和 `displayName`）
  - `mainProductCode`：新机 SKU 编码（例如 `SM-A5760DBBCHC`）
  - `provider`：`SHANHS`

---

### 2.2 机型问答树与成色选项查询
- **接口路径**：`POST /tokocommercewebservices/v2/cn/servicesv2/assessment/TRADE_IN?q=code:{phoneId}&provider=SHANHS`
- **请求体（JSON）**：`{"imei": ""}`
- **响应说明**：
  返回该机型对应的全部评估问题列表（`questions`），包含：
  - `title`：题目名称（型号、内存、颜色、开机、ID锁、保修、购买渠道、边框背板、摄像头镜片、机身弯曲情况、屏幕外观、屏幕显示、电池健康度、原装屏、摄像头、其他情形等）
  - `code`：题目唯一编码
  - `multichoice`：是否多选（`true` 为其他异常情形；`false` 为必选单选）
  - `answers`：选项列表，每个选项包含 `code`（选项值编码）和 `label`（显示文案）

---

### 2.3 估价值计算与生成
- **接口路径**：`POST /tokocommercewebservices/v2/cn/assessment/TRADE_IN/json`
- **请求体（JSON）**：
```json
{
  "productCode": "<phoneId>",
  "selectionResponses": [
    {"key": "provider", "value": "SHANHS"},
    {"key": "phoneId", "value": "<phoneId>"},
    {"key": "options", "value": "<逗号分隔的选项code字符串>"},
    {"key": "renewPhoneSku", "value": "SM-A5760DBBCHC"},
    {"key": "renewPhoneSkuName", "value": "Galaxy A57 5G"},
    {"key": "renewPhoneSkuPrice", "value": "4399"},
    {"key": "isSupportSubsidy", "value": false}
  ]
}
```
- **响应说明**：
  在 `result.additionalParameters.entry` 中返回：
  - `price` / `discountAmount`：基础折抵估价金额（浮点数）
  - `discountAmountFormattervalue`：格式化价格字符串（如 `¥3400`、`¥1647` 等）

---

## 3. 标准评估选项映射基准（“过保 + 完美机况”）

对于“完美成色 + 过保”的标准设定：
1. **型号**：匹配全网通国行 A 编码（如 A3635）
2. **内存 & 颜色**：匹配实际容量与色彩名称
3. **保修**：选择包含“过保（保修期≤1个月）”的选项
4. **渠道**：国行
5. **硬件状况**：
   - 开机：能开机 / 正常开机
   - ID锁：无锁或已解锁
   - 边框背板：外观完美无划痕/磕碰
   - 摄像头镜片：正常
   - 机身弯曲情况：机身无弯曲
   - 屏幕外观：屏幕完美无划痕
   - 屏幕显示：显示完美无瑕疵
   - 电池健康度：最高档（>90% / 95%-100%）
   - 原装屏：屏幕无维修 / 原装
   - 摄像头：摄像头正常
   - 其他异常问题项（多选）：不勾选任何项
