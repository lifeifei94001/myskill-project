# 黄金修图流水线技术端点指南 (Pipeline & API Endpoints)

本文档记录三阶段流水线对应底层模型端点、参数配置范式及 CLI/SDK 调用规范。

---

## 阶段一：面部修复与画质除瑕 (Phase 1: Restore & Clean)

### 1.1 核心端点推荐
* **`fal-ai/image-restore` / `fal-ai/codeformer` / `fal-ai/nafnet`**:
  * 专长：去模糊（Deblur）、夜景去噪点（Denoise）、人脸五官高清重建（Face Restoration）。
  * 优势：在不改变人脸原貌骨骼特征的前提下，精准修复瞳孔高光、睫毛、发丝与平整肤质。

### 1.2 关键参数范例
```json
{
  "image_url": "https://example.com/input.jpg",
  "fidelity": 0.75,              // 保真度：0.0 (过度美颜AI感) ~ 1.0 (接近原图)，建议 0.7~0.8
  "restore_background": true,    // 是否同步去噪背景
  "upscale": 1                   // 本阶段专注修复，超分放大留给阶段三
}
```

---

## 阶段二：风格迁移、光影打光与局部重绘 (Phase 2: Context Edit & Styling)

### 2.1 核心端点推荐
* **`fal-ai/flux/context` / `fal-ai/flux-general/image-to-image`**:
  * 专长：基于 FLUX 的语境理解图生图。可直接按自然语言改变环境氛围、重新布光。
* **`fal-ai/flux/inpainting`**:
  * 专长：消除画面杂物/路人，或局部更换发型、衣服。
* **`fal-ai/bria/background/remove` / `fal-ai/flux/background-replace`**:
  * 专长：发丝级精准抠图与背景替换。

### 2.2 关键参数范例
```json
{
  "image_url": "https://example.com/restored_input.jpg",
  "prompt": "portrait of the same subject with subtle vintage 35mm warm film tone, soft rim lighting, sunset golden hour glow",
  "strength": 0.45,              // 风格重塑强度：0.3~0.5 保持主体轮廓，0.6+ 风格彻底替换
  "guidance_scale": 3.5,
  "enable_safety_checker": false
}
```

---

## 阶段三：超分辨率无损放大与细节增强 (Phase 3: Super Resolution & Polish)

### 3.1 核心端点推荐
* **`fal-ai/clarity-upscaler`**:
  * 专长：通过生成式扩散模型补充微观细节（皮肤纹理、毛孔、织物纤维），避免传统双三次插值的塑料感。
* **`fal-ai/esrgan` / `fal-ai/ccsr`**:
  * 专长：保真度极高的纯几何超分放大，速度极快。

### 3.2 关键参数范例
```json
{
  "image_url": "https://example.com/styled_output.jpg",
  "scale": 2,                    // 放大倍率：通常 2x 或 4x 足够满足打印/壁纸
  "creativity": 0.25,            // 细节想象力：0.1~0.3（低创意=高保真，高创意=重新描摹细节）
  "resemblance": 0.85            // 还原度
}
```

---

## CLI 与环境变量调用方式

### 方式 A：通过 `genmedia` CLI
若环境中已配置 `fal` 或 `genmedia` CLI：
```bash
# 阶段 1：修复
genmedia run fal-ai/image-restore --input image_url="path/to/local.jpg" --output restored.png

# 阶段 2：编辑重绘
genmedia run fal-ai/flux/context --input image_url="restored.png" --input prompt="<STYLE_PROMPT>" --output edited.png

# 阶段 3：超分
genmedia run fal-ai/clarity-upscaler --input image_url="edited.png" --input scale=2 --output final_hd.png
```

### 方式 B：通过 Python `retouch_helper.py`
运行附带脚本生成流水线参数或直接发送请求：
```bash
python scripts/retouch_helper.py inspect input.jpg
python scripts/retouch_helper.py build-pipeline input.jpg --style vintage-film --eliminate-background
```
