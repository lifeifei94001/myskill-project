# 笔记本官方白底图检索与质量校验指南 (Image Search & Quality Guidelines)

本指南旨在规范笔记本机型官方标准化白底建档图的检索、筛选与排版输出，与配置参数紧密配套，用于 3C 数码回收（爱回收、转转、找靓机等）及电商后台标准商品库建档。

---

## 一、 双图标准定义与视角去重铁律

系统必须且仅需输出 **2 张官方标准化白底图**，必须严格符合以下构图规范，**绝对禁止两张图使用同一视角或同一 URL**：

### 1. 图 1：正视展开完整白底图 (Front-facing Open View)
- **视角要求**：正面 90° 直视展开（垂直或微仰角）；
- **画面元素**：
  - B 面屏幕（点亮状态展示官方默认壁纸，或纯白屏）；
  - C 面键盘区域、触摸板及掌托完整呈现；
  - 机身左右边缘与底边完整居中，**严禁边缘截断**；
- **背景要求**：纯白色底色（RGB 接近 255,255,255），无阴影或仅有自然悬浮浅阴影；
- **严禁事项**：严禁倾斜俯视过大导致屏幕被压扁、严禁自媒体桌面实拍、严禁带有电商大促促销标签或打光杂乱。

### 2. 图 2：背面/斜侧展开完整白底图 (Rear Three-Quarter / Back View)
- **视角要求**：斜后视约 30°~45°，俯角约 15°~30°（严禁直接拿正面图充数！）；
- **画面元素**：
  - A 面顶盖完整展示（清晰呈现品牌与产品线 LOGO，如 `LEGION`、`ROG`、`ThinkPad` 等）；
  - 清楚展示转轴结构、尾部散热出风口格栅、尾部接口群（如果有）；
  - 机身侧面或底部轮廓线条清晰完整；
- **背景要求**：纯白底，清晰无遮挡；
- **视角去重红线（重大反例）**：**绝对禁止正视展开图与背面/斜侧展开图使用完全相同的图片或 URL！** 若背面图暂时缺失，宁可标注直达官方图库，也绝不能复制正面图来滥竽充数！

---

## 二、 三级检索信源梯队与精准指令

检索时必须严格按照以下三级梯队依次查找：

### 梯队 1：品牌官方商城与技术支持库（最高保真度）
- **特点**：官方 3D CAD 工业级高精度渲染图或影棚官方摄制，100% 纯白底，无任何水印；
- **典型渠道**：
  - 联想官网商城 / 联想 PSREF 规格图库：`psref.lenovo.com`、`shop.lenovo.com.cn`
  - 华硕 ROG 玩家国度官网：`rog.asus.com.cn`
  - 戴尔 Dell 官网产品技术规格：`dell.com/zh-cn/shop/`
  - 苹果 Apple 官网技术规格库：`apple.com.cn/macbook-pro/specs/`
- **检索模板**：
  - `[品牌 机型完整名称] (官网 OR 官方商城) 产品图集`
  - `[机型英文型号] official render white background`

### 梯队 2：中关村在线 (ZOL) 产品图库（最全机型库）
- **特点**：国内收录最为完备的 3C 垂直图库，按 Tab 系统化分门别类：
  - **正面展示 Tab**：对应图 1（正视展开）；
  - **背面/接口 Tab**：对应图 2（背面顶盖或斜侧出风口）；
- **定位方式**：
  - 访问 `detail.zol.com.cn/picture_index/indexXXXX.shtml`；
  - 必须分别点击“正面图”和“背面图/侧面图”提取两张不同视角的直链。

### 梯队 3：京东自营 / 天猫官方旗舰店（高清晰度主图）
- **特点**：主流在售型号覆盖全，主图前 1~3 张通常符合天猫/京东白底规则（800×800 以上，纯白底）；
- **筛选准则**：
  - 第 1 张主图：通常为正面展示；
  - 第 2~3 张轮播图：通常为背面顶盖、侧面接口或微张开视角。

---

## 三、 Chrome DevTools / 浏览器自动化精准提取指引

当使用 Chrome DevTools 或浏览器插件时，可直接向浏览器发送 DOM 查询，同时实现**参数精准抓取**与**图片视角彻底隔离**：

### 1. ZOL 图库定向提取脚本（避免正反混淆）
```javascript
// 在 ZOL 产品图库页面执行
const frontImg = document.querySelector('.pic-tab-front img, .photo-list li:nth-child(1) img')?.src;
const rearImg = document.querySelector('.pic-tab-back img, .pic-tab-side img, .photo-list li:nth-child(2) img')?.src;
console.log({ frontImg, rearImg });
```

### 2. ZOL 官方参数精准解析脚本（避免第三方商家魔改参数）
```javascript
// 在 ZOL param.shtml 页面提取官方出厂原版参数
const specs = {};
document.querySelectorAll('table.param-table tr').forEach(row => {
    const th = row.querySelector('th')?.innerText?.trim();
    const td = row.querySelector('td')?.innerText?.trim();
    if (th && td) specs[th] = td;
});
// 提取出的 CPU、内存、显卡、硬盘、上市时间 均为原厂官方白纸黑字数据
```

---

## 四、 核心红线：防假图链接（Zero URL Hallucination）与防盗链解决标准

1. **绝对严禁凭空编造/拼接图片直链**：各大品牌 CDN（如 `lefile.cn`、`360buyimg.com`、`zol-img.com.cn`）均使用内部 Hash 命名，严禁凭空构造虚假路径。
2. **必须添加 `referrerpolicy="no-referrer"` 防盗链指令**：
   ```html
   <img src="真实图片URL" referrerpolicy="no-referrer" width="300" alt="展开白底图" />
   ```
3. **双轨交付机制 (Direct Image + Official Gallery Fallback)**：必须同时交付真实图片与官方图库直达链接。
