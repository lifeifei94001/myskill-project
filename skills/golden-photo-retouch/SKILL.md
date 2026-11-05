---
name: golden-photo-retouch
description: "Use when the user wants to retouch photos, edit portraits, enhance image quality, remove background/objects, or apply aesthetic styles. Handles face restoration, lighting enhancement, artistic style transfer, and super-resolution upscaling in a 3-stage golden pipeline. Triggers on: '修图', 'P图', '黄金修图', '人像精修', '照片美化', '消除路人', '更换背景', '调色', '胶片风', '港风', '赛博朋克', '泡泡玛特', '图片超分', '清晰度修复', '弄好看点', 'photo retouch', 'image edit', 'face restore', 'upscale image'."
---

# 黄金修图组合 (Golden Photo Retouch Suite)

## 概述 (Overview)
`golden-photo-retouch` 是专为 AI Agent 设计的端到端高级修图与视觉重构工作流。它将业界顶尖的深度视觉模型（`fal-restore` 面部修复 + `fal-image-edit` 语境编辑/风格迁移 + `fal-upscale` 超分辨率无损放大）融合成标准化的“黄金三阶段流水线”，并内置专业摄影美学提示词引擎与七维交付自检，确保 Agent 面对用户模糊的“帮我弄好看点”需求时，能自主输出影楼级、大师级视觉效果。

---

## 核心修图模式矩阵 (Retouch Modes)

在接触用户图片与诉求时，首先快速匹配以下 5 类模式：

| 模式编号 | 核心诉求 | 典型操作 | 推荐风格预设 |
| :--- | :--- | :--- | :--- |
| **Mode A** | **人像精修与微瑕修复** | 皮肤通透、五官提亮、去暗光噪点、发丝重构 | `natural-beauty` |
| **Mode B** | **氛围感与胶片调色** | 情绪感光影、复古颗粒、冷暖光斑、电影色调 | `vintage-film` / `hk-cinema` |
| **Mode C** | **空间重构与杂物消除** | 抹除路人、背景抠图替换、构图延展扩图 | 结合指定环境 Context |
| **Mode D** | **高级商业与影室棚拍** | 极简静奢灰调、柔光箱布光、商业肖像质感 | `quiet-luxury` / `japanese-airy` |
| **Mode E** | **潮玩/次元跨界变身** | 3D 黏土盲盒、Pop Mart 手办化、萌趣头像 | `pop-mart` |

> 详细风格关键词与调色参数见：[style_presets.md](references/style_presets.md)

---

## 黄金三步法流水线 (The 3-Stage Pipeline)

```
[原始图片] 
    │
    ▼
【阶段 1: 画质除瑕与五官修复 (fal-restore)】── 消除噪点、去模糊、重建瞳孔高光与发丝
    │
    ▼
【阶段 2: 语境编辑与美学重塑 (fal-image-edit)】── 风格迁移、定向布光、消除路人、背景置换
    │
    ▼
【阶段 3: 超分辨率与质感增强 (fal-upscale)】── 2x~4x 生成式超分、微观肌理与织物纤维拉满
    │
    ▼
[高定级成品大片]
```

### 阶段 1：画质除瑕与五官修复 (Phase 1: Restore & Clean)
* **核心目标**：解决“底子问题”。去除运动模糊、夜景噪点，修复失焦人脸与暗光欠曝。
* **推荐参数**：
  * 保真度 (`fidelity`): `0.70 ~ 0.80`（既重构清晰五官，又保留本人骨骼辨识度，严禁过度磨皮假面）。
  * 脚本辅助：运行 `python scripts/retouch_helper.py inspect <image>` 快速诊断欠曝、低对比度或低清问题。

### 阶段 2：语境编辑与美学重构 (Phase 2: Context Edit & Styling)
* **核心目标**：解决“好看与氛围感问题”。
* **核心红线：严禁“换头换人”与“凭空脑补虚拟脸”（Identity Locking & Zero-Hallucination Protocol）**：
  P图（修图）的最底层红线是**必须是本人，人物改变不大**！严禁把真实人物P成AI模特或另一个人。
  1. **面部非完整可见时严禁虚拟人脸（铁律：低头就保持原来低头）**：
     若原图人物处于低头、侧颜、背影、发丝遮挡或面部未露出状态，**绝对严禁强行指令人物抬头或转正脸**，严禁让模型无中生有凭空捏造一张虚拟人脸！原图低头就保留原本低头姿态，仅对光影、氛围、发丝光泽、服饰质感和背景景深进行美化提升，人物本体保持最小变动（Minimal Subject Mutation）。
     提示词强制锁定姿态：
     `"Keep the subject's exact posture, downward gaze angle, head orientation, and natural silhouette from the reference photo. Do NOT fabricate, invent, or hallucinate an artificial front face. Preserve the original head tilt and pose with minimal alteration to the person."`
  2. **整理乱发与露眼使用“减法修图”，严禁扩散重绘换脸（Subtractive Retouching Rule）**：
     当用户提出“整理遮脸刘海/拨开碎发露出清澈眼睛”等诉求时，**绝对禁止**将该指令直接丢给通用扩散生成模型（如 Canva AI 生图或通用全图 img2img）！扩散模型在被遮挡处因缺失原始眼睛先验，必定从训练集随机脑补一张假脸。
     **正确执行方案**：必须采用“局部像素减法（Inpainting/Patch-Match）”，仅剔除横跨眼鼻的杂乱发丝线条，搭配局部阴影提亮（Dodge & Burn 唤醒眼神光），**100% 沿用原图底层真实五官肌理**。
  3. **动环境、不动真人隔离原则（Subject-Environment Decoupling）**：
     风格迁移、丁达尔光线、Komorebi 树影斑驳、大光圈背景虚化只允许作用于环境、背景与整体光影，人物主体面容骨骼实施**像素级锁定（Pixel-Lock）**。
  4. **显式身份锚定前置**：提示词开头必须强声明：
     `"Photo retouch of the exact same person from reference image. Strict high-fidelity facial identity preservation: retain identical facial features, bone structure, eyes, nose, lips, jawline, and skin tone. Do not replace the subject with a different model or generic AI face; maintain 100% facial recognition and likeness."`
  5. **特征锚点锁定（Anchor Features）**：明确锁定人物原生不可变特征（发型弧度、发箍、耳廓、特定痣/斑、原生眉形）。
  6. **抑制过度磨皮假面**：提示词明确要求 `authentic skin texture with visible natural pores, unedited natural feel`，拒绝“千人一面网红脸”。
* **自主美化提示词法则**：
  用户如果只说“弄好看点”，Agent **严禁**只输入 `"beautiful, nice"` 等空洞词汇，必须结合摄影三要素进行翻译增强：
  1. **光影（Lighting）**：`Rembrandt lighting, golden hour warm rim light, soft volumetric diffusion`
  2. **色彩（Color Grading）**：`Kodak Portra warm undertones, soft pastel tones, cinematic contrast`
  3. **景深与构图（Optics）**：`85mm portrait lens, f/1.8 shallow depth of field, creamy bokeh`
* **推荐强度 (`strength`)**：
  * 轻度微调与打光：`0.30 ~ 0.40`
  * 风格迁移/胶片化：`0.45 ~ 0.55`
  * 潮玩/二次元重塑：`0.70 ~ 0.80`

### 阶段 3：超分辨率无损放大 (Phase 3: Super Resolution & Polish)
* **核心目标**：解决“清晰度与质感问题”。
* **参数建议**：
  * 放大倍数 (`scale`): `2x`（常用）或 `4x`（大屏/打印）。
  * 创意度 (`creativity`): `0.15 ~ 0.25`（通过扩散模型细化毛孔与织物细节，避免死板放大）。

> 详细 API 端点与 CLI 语法参见：[pipeline_endpoints.md](references/pipeline_endpoints.md)

---

## 执行步骤与工具支持 (Execution SOP)

### 步骤 1：分析输入并制定修图方案
1. 确认图片路径与用户核心意图。
2. 运行脚本生成分析报告与参数计划：
   ```bash
   python scripts/retouch_helper.py plan "path/to/image.jpg" --style vintage-film --custom "去掉背后杂物，突出人像笑容"
   ```
3. 向用户清晰呈现执行方案与风格预期。

### 步骤 2：执行各阶段处理
根据用户环境可用工具执行流水线：
- **方式 A（CLI 工具）**：通过 `genmedia` 或 `fal` CLI 依序执行各个阶段端点。
- **方式 B（API/Python）**：通过请求端点传递 `retouch_helper.py` 规划的参数。
- **方式 C（轻量本地辅助）**：对于基础剪裁或对比度微调，可直接使用 Python PIL 执行。

---

## 交付前七维美学自检标准 (7-Dimension Aesthetic Self-Check)

在将处理后的图片交付给用户前，必须从以下 7 个维度进行视觉自检闭环：

1. **五官真实度与姿态守恒**：是否保留了人物原有五官骨骼？若原片低头、侧颜或看不到脸，是否严格保持原有姿态，坚决杜绝凭空捏造虚拟正面脸？是否避免了“橡皮人假面”过度磨皮？
2. **光影一致性**：若更换了背景或重绘局部，主体受光面与新背景主光源角度是否完全契合？
3. **边缘融合度**：发丝、肩膀轮廓与背景交界处是否自然？有无白色切边或生硬羽化痕迹？
4. **消除干净度**：若执行了杂物/路人抹除，抹除区域的纹理与透视是否平滑，有无鬼影或异常色块？
5. **影调与对比**：暗部是否死黑？高光是否过曝死白？色彩过渡是否通透层次分明？
6. **质感清晰度**：放大至原倍率观察，眼睛瞳孔、发丝与衣物细节是否清晰立体？
7. **审美原创性**：成片是否摆脱了廉价“AI 塑料感”，具备摄影级或电影级的高级情绪表达？
