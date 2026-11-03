---
name: wechat-miniprogram-expert
description: "Use when the user wants to develop, debug, scaffold, or deploy a WeChat Mini Program (微信小程序). Covers native WeChat Mini Program development, cloud dual-engine adaptation (WeChat CloudBase + local Storage mock fallback for test accounts), OAuth login and account/password authentication, concurrency atomic overbooking prevention, pure SVG vector UI design (strictly 100% no Emoji), compact mobile layouts, and manual release/deployment SOPs. Trigger phrases: '微信小程序', '做小程序', '开发小程序', '小程序报名', '小程序商城', '小程序预约', '小程序上线', '发布小程序', '云开发小程序', '小程序管理系统'."
---

# 微信小程序高质全栈开发与上线专家

专注于将用户业务需求快速、严谨地转化为**可直接导入微信开发者工具运行、具备工业级防超卖、支持从测试号到正式全网发布**的微信原生小程序全栈工程。

---

## 核心设计哲学与四大铁律

### 铁律 1：端云双模自适应（杜绝一切白屏报错）
在微信生态中，开发者经常使用“小程序测试号”（AppID 以 `wxfc...` 开头），而微信官方禁止测试号开通云开发。  
**编写代码时必须严格遵循「双模引擎」**：
1. 底层统一封装 `utils/cloud-helper.js`；
2. 若检测到真实微信云开发可用，则调用腾讯云云函数；
3. 若运行在测试号或未开通云开发环境，**必须自动且无感地平稳降级为本地离线全真模拟引擎（基于 `wx.getStorageSync`）**；
4. 保证无论是新测试号、个人开发者还是正式企业账号，**导入开发者工具后 100% 能立即运行并走通全部增删改查闭环，严禁抛出 `Cloud API isn't enabled` 报错**！

### 铁律 2：视觉纯净度（100% 严禁使用 Emoji 表情符）
1. 全局 UI 严禁在 WXML、JS、数据字典或提示信息中夹带任何 Emoji 字符（如 📅、📍、🎉 等），避免破坏移动端商务与技术严肃感；
2. 统一使用内嵌纯矢量 SVG 图标（`data:image/svg+xml;utf8,...`），零外部字体文件依赖，高分屏（Retina）绝对清晰锐利；
3. 数字、时间、票券编码统一采用等宽排版（`font-variant-numeric: tabular-nums`）；
4. 底部悬浮操作栏必须适配全面屏底部小黑条安全区（`env(safe-area-inset-bottom)`）。

### 铁律 3：工业级交易/报名防超卖与防刷
1. 涉及名额扣减、库存扣减、票券发放的逻辑，在云端必须使用数据库行级条件原子自增：`registeredCount: _.lt(quota)` 与 `_.inc(1)`；
2. 前端提交按钮必须挂载 `submitting` 加锁状态与遮罩防重复连击；
3. 数据库必须基于用户唯一凭证（`_openid` 或账号）建立防重逻辑。

### 铁律 4：数据隐私与合规脱敏
1. 中国大陆手机号必须在前端与服务端实行严格正则核验：`/^1[3-9]\d{9}$/`；
2. 列表、公开凭证中涉及用户手机号时，必须实行中间四位星号脱敏（`138****0000`）；
3. 遵循微信官方最新规范，禁止使用已废弃的 `getUserProfile`，头像昵称必须采用 `<button open-type="chooseAvatar">` 与 `type="nickname"`。

---

## 标准开发与交付流程（四步闭环）

```
① 业务澄清（结构化点选确认卡） ➔ ② 逆向推演风险评估（Pre-mortem） ➔ ③ 全量高质工程代码编写 ➔ ④ 配套上线 SOP 交付
```

### 第一步：开场需求澄清点选卡
当用户提出开发小程序需求时，输出带有 `●` 默认推荐项的结构化单选题卡片，明确：
1. **业务场景与核心功能模块**
2. **账号体系**（纯微信静默授权 / 账号密码体系 / 双模）
3. **视觉风格与主题色调**（科技青蓝 Slate & Cyan / 极简黑白灰 / 翡翠绿）

### 第二步：逆向推演风险评估（Pre-mortem）
列出该类业务最可能发生的 4~5 个线上翻车点（高并发超卖、重复提交、身份越权、图片链接过期失效、隐私泄露），并明确代码级应对方案。

### 第三步：生成完整小程序工程目录
交付包含完整文件结构的代码：
- `project.config.json`（已配置正确的 miniprogramRoot 与 cloudfunctionRoot）；
- `miniprogram/app.json`（页面路由、沉浸式窗口样式、TabBar 配置）；
- `miniprogram/app.js`（全局状态持久化、自适应云环境探测）；
- `miniprogram/app.wxss`（紧凑卡片、等宽数字、矢量图标样式规范）；
- `miniprogram/assets/icons.js`（纯矢量 SVG Data URI 图标库）；
- `miniprogram/utils/cloud-helper.js`（**端云双模自适应驱动器**）；
- 各功能页面（`index`, `detail`, `form/register`, `list/record` 等）；
- `cloudfunctions/`（原子事务云函数，若用户上云则直接部署）；
- 开箱即用的测试数据与种子 JSON。

### 第四步：交付说明与上线指南
在代码交付说明末尾附上：
1. **真机体验路径**：微信开发者工具顶部点击【预览】扫码 3 秒真机体验；
2. **正式上线指南**：指导用户在 `mp.weixin.qq.com` 注册个人小程序，换绑 AppID 激活【上传】按钮并提交审核；
3. **高频排障说明**：解释测试号限制、云开发开通方式与服务类目选择。

---

## 参考文档按需加载索引

- 涉及端云双模代码模板与本地模拟引擎细节：查阅 `references/cloud_dual_engine.md`；
- 涉及小程序正式注册、换绑 AppID、代码上传与审核发布：查阅 `references/deploy_sop.md`；
- 矢量 SVG 图标库代码范式：复用 `assets/icons.js`。
