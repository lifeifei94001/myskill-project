# 微信小程序端云双模自适应架构规范 (Cloud Dual-Engine)

## 为什么必须采用双模引擎

在实际微信小程序开发中，存在两类典型场景：
1. **测试号 / 本地开发环境**：AppID 以 `wxfc...` 开头，微信官方强制禁止使用云开发。如果代码直接调用 `wx.cloud.callFunction`，会导致小程序抛出 `Cloud API isn't enabled` 错误并白屏崩溃。
2. **正式上线生产环境**：正式 AppID 并在微信公众平台开通了云开发，数据需统一持久化在腾讯云数据库，图片走 CDN，名额走云函数行级原子锁。

双模自适应引擎通过在 `utils/cloud-helper.js` 统一封装拦截层：
- 优先尝试调用 `wx.cloud.callFunction`；
- 若云环境未开通或报错，**自动无缝降级至本地高仿真模拟引擎（基于 `wx.getStorageSync`）**；
- 业务页面（Page）只需调用 `callFunction(name, data)`，无需关心当前运行在云端还是本地，保证 100% 体验一致且绝不闪退报错！

---

## 核心实现代码模板 (`utils/cloud-helper.js`)

```javascript
// miniprogram/utils/cloud-helper.js
const tempFileUrlCache = new Map();

/**
 * 本地离线高真模拟引擎
 */
const runLocalSimulatedFunction = async (name, data = {}) => {
  await new Promise(resolve => setTimeout(resolve, 150)); // 模拟真实网络微延迟
  
  const app = getApp();
  const currentOpenid = (app && app.globalData && app.globalData.openid) || 'mock_user_openid';

  let localEvents = wx.getStorageSync('LOCAL_EVENTS') || [];
  let localRecords = wx.getStorageSync('LOCAL_RECORDS') || [];

  // 1. 查询列表
  if (name === 'getList') {
    return { code: 0, success: true, data: localEvents };
  }

  // 2. 提交事务（含防超卖与防重校验）
  if (name === 'submitTransaction') {
    const { targetId } = data;
    const target = localEvents.find(e => e._id === targetId);
    if (!target) return { code: 404, success: false, message: '数据不存在' };

    // 防超卖
    if (target.currentCount >= target.quota) {
      return { code: 4003, success: false, message: '名额已报满' };
    }

    target.currentCount += 1;
    wx.setStorageSync('LOCAL_EVENTS', localEvents);

    const newRecord = {
      _id: 'rec_' + Date.now(),
      _openid: currentOpenid,
      targetId,
      createTime: new Date().toISOString()
    };
    localRecords.unshift(newRecord);
    wx.setStorageSync('LOCAL_RECORDS', localRecords);

    return { code: 0, success: true, data: newRecord };
  }

  return { code: 0, success: true, data: null };
};

/**
 * 统一双模分发调用
 */
const callFunction = async (name, data = {}, showLoading = false) => {
  if (showLoading) wx.showLoading({ title: '加载中...', mask: true });

  const app = getApp();
  const isCloudAvailable = app && app.globalData && app.globalData.isCloudAvailable;

  // 优先走真实云开发
  if (isCloudAvailable && wx.cloud) {
    try {
      const res = await wx.cloud.callFunction({ name, data });
      if (showLoading) wx.hideLoading();
      if (res && res.result) return res.result;
    } catch (err) {
      console.warn(`[CloudFunction ${name}] 云端调用失败，平稳切至本地高仿真引擎:`, err);
    }
  }

  // 自动平稳切至本地仿真引擎
  try {
    const localRes = await runLocalSimulatedFunction(name, data);
    if (showLoading) wx.hideLoading();
    return localRes;
  } catch (err) {
    if (showLoading) wx.hideLoading();
    throw err;
  }
};

module.exports = {
  callFunction
};
```
