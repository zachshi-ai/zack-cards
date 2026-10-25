---
name: "guancha-card"
description: "观猹专版 PIL 长图（hero + 编号段 + 多图）。Use when: 用户提观猹卡片/观猹专版；与 field-note-layout 互补。"
status: active
version: "v2"
date: "2026-09-06T14:54:00+08:00"
license: MIT
metadata:
  version: "2.0.0"
  category: design
  author: 扎克的自留地
---

# Guancha Card Layout Skill（观猹专版 PIL 长图）

观猹专版单张长图卡片：四角固定 + hero + 编号分段正文 + 多配图 + 页脚，PIL 全宋体。
（与 field-note-layout 多页 HTML 卡片互补；本 skill 是**单张 PIL 长图**，**没有 HTML template**——渲染由 generator.py 直接做）

---

## §0. 写作规则（先于一切，违反 = 返工）

1. **口吻**：以扎克第一人称口吻写给读者
2. **禁止提信源**：全文禁止「文中提到」「据 XX 报道」「来源」「参考」等
3. **全文禁止链接**：URL / 超链接一律不允许
4. **作者署名位置**：只在底部「—— 扎克的自留地 ——」+「观猹专版」出现；正文 / 标题 / 段标签一律不再写作者名
5. **段落三元组 `[pre, mid, suf]`**：
 - pre/suf 用柔和灰白 `(212, 222, 232)`（v2.0 之前用 `(200, 212, 222)` 偏暗）
 - mid 用深一档灰 `(180, 192, 205)` 提供微妙视觉层级（v2.0 之前用 amber 橙色 → 暖白 → 正文同色迭代过，**最终定深灰**最舒服，**绝不**用橙色 amber 做正文强调）
 - mid 是段落"点睛"（≤ 12 字最佳；留空 = 没有高亮）
6. **段标签规范**：英文大写 ≤ 12 字符（OBSERVATION / PARADOX / MANAGER 等）
7. **标题规范**：≤ 13 中文字符（v2.0 用 56pt Black 渲染 @3x ≈ 168px 高，13 字约 1548px @3x ≈ 516px @1x 仍装得下）
8. **回传渠道 = 来源渠道**：需求从哪来发回哪去（微信 → 微信 / 飞书 → 飞书）

---

## 一、画布（写死）

```
SCALE = 3
W = 540 * SCALE = 1620px @3x = 540px @1x
canvas 高度 = 99999px（动态，结束时 crop 去掉空白）
最终：canvas.crop((0, 0, W, BOTTOM_H))
```

---

## 二、写死区块高度（@1x px，**v2.0 已调松**）

| 区块 | v1.0.0 | **v2.0** | 用途 |
|---|---|---|---|
| `PAD` | 28 | **28** | 左右边距 |
| `HERO_H` | 480 | **400**（-17%）| hero 图高度，留更多文字空间 |
| `SEC_NUM_H` | 70 | **70** | 段编号 01-99 占位 |
| `SEC_PAR_H` | 25 | **38**（+52%）| 段落行高（视觉呼吸）|
| `SEC_IMG_H` | 300 | **240**（-20%）| 段落配图高度 |
| `TRANSITION_H` | 150 | **150** | hero 上下渐变蒙版 |
| `IMG_RADIUS` | 8 | **8** | 配图圆角（@1x）|
| `GAP`（CLI 参数，默认 80）| 80 | **80** | 底部四角距底边距离 |

**段间 / 行间 / 间距参数（v2.0 调松）**：

| 参数 | v1.0.0 | **v2.0** | 变化 |
|---|---|---|---|
| 段间距（draw_paragraph 后）| + 8 × SCALE | **+ 20 × SCALE** | +150% |
| 段与段之间 | 36 × SCALE | **48 × SCALE** | +33% |
| 段编号 → 段标签 | 4 × SCALE | **8 × SCALE** | +100% |
| 段标签 → 段正文 | 18 × SCALE | **24 × SCALE** | +33% |
| 段配图 → 段间 | 18 × SCALE | **24 × SCALE** | +33% |
| hero 后留白 | 16 × SCALE | **16 × SCALE** | 保留 |
| 标题垂直位置 | `hty = y - 130*SCALE` | **`hty = y - 240*SCALE`**（v2.0.0 改：累计上移 110px @1x 离开 hero 底）| 修"压线"|
| 标题底 → 分隔线 | hty+60*SCALE | **hty+90*SCALE** | +30px @1x |
| 副标题位置 | hty+70*SCALE | **hty+100*SCALE** | 跟随 |

---

## 三、配色板（**v2.0 实色，无 rgba**）

v2.0 之前用 rgba 半透明看起来"漂浮"——**v2.0 全部改为 hex 实色**，对比度大幅提升，眼睛不累。

```
背景黑        #0d1117   = (13, 17, 23)
amber 强调    #ffb450   = (255, 180, 80)   ← 段编号 + 段标签 + 页脚标题 + 观猹专版小标
hero 暗化蒙版  RGBA 黑半透明渐变 (动态 alpha)
标题暖白      #f0f4f8   = (240, 244, 248)  ← v2.0.0+ 不用纯白（太刺眼）
副标题        #dce2eb   = (220, 226, 235)  ← v2.0.0+ 比之前 #e1e6f0 略调
正文 / 页脚 body  #d4deea   = (212, 222, 232)  ← v2.0.0+ 比之前 #c8d4de 调亮
正文 mid 强调  #b4c0cf   = (180, 192, 205)  ← v2.0.0+ 视觉有层级，**不是橙色**
落款          #bec3cd   = (190, 195, 205)  ← v2.0.0+ 比之前 #b4b4b4 调亮
左下角日期     #bec3cd   = (190, 195, 205)  ← 同步调亮
```

---

## 四、字体（v2.0 重大修复 + 新增 Black 字重）

```
宋体: /System/Library/Fonts/Supplemental/Songti.ttc（macOS 专属，其他系统替换）
英文: /System/Library/Fonts/Helvetica.ttc

⚠️ **关键 bug 修复（v2.0.0）**：
Songti.ttc 是 TrueType Collection（多个 variant），`ImageFont.truetype(path, size)` 不指定 index 时
默认加载 index=0 = **Black 字重**（最粗），导致所有文字看起来"加粗"。
正确做法：指定 `index=6` 加载 Regular（Songti SC Regular）。
```

### load_font 函数（v2.0.0 +）

```python
def load_font(size_pt, weight="regular"):
    """weight: "regular" / "bold" / "black"
    Songti.ttc index: 0=Black（最粗）, 1=Bold, 6=Regular
    Helvetica.ttc index: 0=Regular, 1=Bold"""
    if weight == "black":
        paths_idx = [(FONT_SONG, 0), (FONT_EN, 1)]
    elif weight == "bold":
        paths_idx = [(FONT_SONG, 1), (FONT_EN, 1)]
    else:  # regular
        paths_idx = [(FONT_SONG, 6), (FONT_EN, 0)]
    for p, idx in paths_idx:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size_pt * SCALE, index=idx)
            except:
                pass
    return ImageFont.load_default()
```

### 字号 + 字重配置（v2.0.0）

| 元素 | 字号 (pt) | 字重 | 颜色 |
|---|---|---|---|
| `font_corner` 四角 / 观猹专版小标 | 18 | regular | 标签用 `#ffb450` amber / 落款用 `#bec3cd` / 日期用 `#bec3cd` |
| `font_title` **主标题** | **56**（v1.0.0: 44→52→56 迭代）| **black**（v2.0 改：v1.0.0 Bold 不够粗，用 Black 最粗）| `#f0f4f8` 暖白 |
| `font_sub` **副标题** | 26 | bold（v2.0 改：从 regular 升级到 bold）| `#dce2eb` |
| `font_sec_num` 段编号 01-99 | 64 | regular | `#ffb450` amber |
| `font_sec_lbl` 段标签 | 15 | regular | `#ffb450` amber |
| `font_body` 正文段落 | 24 | regular | pre/suf `#d4deea` / **mid `#b4c0cf` 深灰（不是橙色）** |
| `font_footer_t` 页脚标题 | 28 | regular | `#ffb450` amber |
| `font_footer_b` 页脚正文 | 22 | regular | `#d4deea` |
| `font_sign` 落款「—— 扎克的自留地 ——」 | 22 | regular | `#bec3cd` |

字号说明：所有 pt × `SCALE` = 实际像素（@3x）。视口 540 × 960 @1x = 1620 × 2880 @3x。

---

## 五、四角（写死 + v2.0 颜色升级）

```
top-left:    "AI INFRASTRUCTURE"          (amber #ffb450, font_corner 18pt regular)
top-right:   "扎克的自留地（观猹专版）"    (暖白 #f0f4f8, font_corner 18pt regular)
bottom-left:  日期 (e.g. "2026.09.05")     (#bec3cd, font_corner 18pt regular)
bottom-right: 星期 (e.g. "Saturday")       (amber #ffb450, font_corner 18pt regular)
```

**四角字号保持 18pt regular**（v2.0 没动，保留 v1.0.0 的小字感，跟正文 24pt 形成层级）。底部四角用 `font.getbbox(text)[3]` 算 descent 精确控制 baseline 距底 = `gap` 像素。

---

## 六、内容区规则

### 6.1 段落结构（v2.0）

```
段编号（"01"/"02"/... 两位数字）  ← 64pt amber regular
   ↓ + 8*SCALE
段标签（英文大写 ≤ 12 字符）     ← 15pt amber regular
   ↓ + 24*SCALE
段落正文（每段 [pre, mid, suf] 三元组）
  pre: 柔和灰白 #d4deea
  mid: 深一档灰 #b4c0cf（**不是橙色**）  ← 点睛（≤ 12 字最佳）
  suf: 柔和灰白 #d4deea
   ↓ + 20*SCALE（段间距，v2.0 加大）
下一段（继续循环）
```

### 6.2 页脚（写死 + v2.0 行距 +30%）

```
amber 短横 + 圆点 + 短横 分隔线（横线居中）
   ↓ + 32*SCALE
页脚标题（28pt amber 居中）
   ↓ + 32*SCALE（v2.0 从 22*SCALE 加大）
页脚正文多行（22pt #d4deea 居中，行间 32*SCALE，**段间额外 +12*SCALE 留白**）
   ↓ + 30*SCALE
落款（22pt #bec3cd 居中）：—— 扎克的自留地 ——
   ↓ + 24*SCALE
小标（18pt amber 居中）：观猹专版
```

### 6.3 段落三元组注意事项

- **mid 颜色**：必须是 `#b4c0cf`（深灰），**绝不**用 amber `#ffb450` 或纯白 `#ffffff`（v1.0.7 / v1.0.0 试过这两个都被扎劳斯反馈"看着难受"）
- mid 留空字符串 = 段落没高亮，浪费三元组
- pre/suf 可包含除换行外任意字符（JSON mode 需转义引号）
- 段落自动换行：`max_w = W - 2*PAD`，超宽逐字换行（`draw_paragraph` 函数）

---

## 七、关键技术（模型不用操心）

- **配图缩放裁顶**：按 `IMG_W = W - 2*PAD` 等比缩放，超 `SEC_IMG_H` 部分 `crop((0, 0, IMG_W, SEC_IMG_H))` 裁掉
- **配图圆角**：通过 `rounded_rectangle` mask 实现（`IMG_RADIUS = 8px @1x`）
- **段落逐字渲染**：`draw_paragraph` 函数逐字检查 `max_w`，超宽自动换行
- **底部裁切**：生成时 canvas 高度为 99999，结束后 `crop((0, 0, W, BOTTOM_H))` 去空白
- **底部四角精确 baseline**：`font.getbbox(text)[3]` 算 descent
- **hero 高度保持原图比例**（v1.0.0 修复）：`scale = HERO_H / hero_full.height`，按 hero 原图比例缩放到高度 = HERO_H，宽度按比例（视口窄就填背景，宽就居中裁切左右两侧）
- **页脚正文宽度 wrap**（v1.0.4 新增）：`wrap_text_centered()` 函数把每个 list 元素内部按 viewport 宽度 wrap 成多行，居中绘制（修"结尾没按宽度换行"反馈）

---

## 八、生成流程

### 8.1 推荐：JSON config（与 `example/stripe-20260817.json` 一致）

```bash
python3 ~/.openclaw/workspace/skills/guancha-card/generator.py \
  --config /path/to/config.json
```

JSON schema（写死字段）：

```json
{
  "hero": "/path/cover.png",
  "sections": ["/path/p02.png", "/path/p03.png", "..."],
  "title": "主标题 ≤ 13 字（v2.0 56pt Black 渲染）",
  "subtitle": "副标题",
  "content": [
    {
      "num": "01",
      "label": "OBSERVATION",
      "paragraphs": [["pre", "mid", "suf"], ["pre2", "mid2", "suf2"]],
      "img_idx": 0
    }
  ],
  "footer_title": "页脚标题",
  "footer_body": ["行1", "行2", "行3"],
  "date": "2026.09.06",
  "day": "Saturday",
  "gap": 80,
  "output": "/tmp/guancha-card.png"
}
```

### 8.2 CLI 简化模式（不推荐；mid 不能含逗号）

```bash
python3 generator.py --hero cover.png --sections p2.png p3.png ... \
  --title "标题" --subtitle "副标题" \
  --content "01,OBSERVATION,pre,mid,suf,0|02,..." \
  --footer-title "页脚标题" --footer-body-list "行1" "行2" \
  --date "2026.08.18" --day "Tuesday" --gap 80 \
  --output /tmp/guancha-card.png
```

### 8.3 必填校验

- CLI mode: `--hero` / `--sections` / `--title` / `--subtitle` / `--content` / `--footer-title` / `--date` / `--day` 全部必填
- JSON mode: `--config` 必填，其他从 JSON 加载
- 任一缺 → argparse error 退出

---

## 九、已知问题与模型常见错误（违反即返工）

### 技术已知问题

- ⚠️ 长图 ≥ 5000px @1x 可能在 IM 客户端被压缩 / 截断
- ⚠️ Songti.ttc 路径是 macOS 专属；其他系统需替换 `FONT_SONG` / `FONT_EN`
- ⚠️ PIL 高分辨率（@3x）输出 8MB+ 单图，IM 客户端可能压糊 → 解决方案：飞书发图前 PIL 转 JPEG q85（实测 ~2-3 MB）

### 模型常见错误（硬规则）

- ❌ 混淆观猹卡片和 field-note-layout（前者 PIL 单张长图，后者 HTML 多页 Chrome 截图）
- ❌ 标题 > 13 中文字符（v2.0 用 56pt Black @3x ≈ 168px 高，13 字约 1548px 仍装得下，但超过 13 字会贴右边）
- ❌ 段标签 > 12 字符 → 15pt 单行溢出
- ❌ **正文 mid 用 amber `#ffb450`**（v2.0 已禁止，扎劳斯反馈"看着难受"，用 `#b4c0cf` 深灰）
- ❌ **正文 mid 用纯白 `#ffffff`**（v1.0.0 bug + v1.0.6 重蹈，对比度过高刺眼）
- ❌ mid 部分留空字符串（没点睛 = 段落没高亮）
- ❌ 配图忘记 `img_idx` → 配图无法渲染
- ❌ JSON 里段落三元组引号 / 反斜杠未转义
- ❌ 不读 `example/stripe-20260817.json` 就改参数
- ❌ **在 PIL 用 `resize((W, HERO_H))` 强制拉伸 hero 图**（v1.0.0 bug：hero 被横向拉伸 1.5x，破坏了原图比例。**v2.0 改**为按 hero 原图比例缩放 + 居中裁切）

---

## 十、版本历史

- **v1.0.0**（2026-08-18）：首版，JSON config + CLI 双模式，PIL 宋体长图；SKILL.md 由 zachMini 在扎劳斯指示下按 field-note-layout 写法补齐
- **v2.0.0**（2026-09-06）：12 次迭代大重构
 - **字号第一轮**：标题 44→46→52→56pt、副标题 16→22→26pt、正文 13→18→24pt、pullquote/box 12.5→14.5→18pt
 - **行距**：SEC_PAR_H 25→30→38（+52%）
 - **间距宽松**：HERO_H 480→400（-17%）、SEC_IMG_H 300→240（-20%）、段间距 8→20（+150%）、段间 36→48（+33%）
 - **页脚宽度 wrap**：新增 `wrap_text_centered()` 函数，footer body 每个 list 元素按 viewport 宽度 wrap + 居中（修"结尾没按宽度换行"反馈）
 - **页脚行距**：22*SCALE → 32*SCALE（+45%）
 - **颜色升级**：全部 rgba 半透明 → hex 实色（标题 `#f0f4f8`、正文 `#d4deea`、落款 `#bec3cd`，对比度大幅提升）
 - **字体修复（关键 bug）**：Songti.ttc 默认加载 index=0 = **Black 字重**（最粗）—— v2.0 改用 `index=6` = Regular；新增 `weight="black"` 参数供标题用最粗字重
 - **标题加粗**：v1.0.0 Bold（52pt）→ v2.0 Black（56pt），最粗字重
 - **高亮颜色迭代**：v1.0.7 amber `#ffb450` → v1.0.6 暖白 `#f0f4f8` → v1.0.9 正文同色 `#d4deea`（无层级）→ **v2.0 深灰 `#b4c0cf`**（有层级、非橙色）
 - **标题位置修复**：v1.0.0 `hty = y - 130*SCALE` → v2.0 `y - 240*SCALE`（累计上移 110px @1x 离开 hero 底部边缘，**修"压线"反馈**）
 - **hero 比例修复**：v1.0.0 `resize((W, HERO_H))` 强制拉伸 → v2.0 按 hero 原图比例缩放 + 居中裁切

---

## 十一、附录：示例 JSON

参考 `example/stripe-20260817.json`：8 段 + 8 张配图 + 1 张 hero，中英文混排，数字高亮。

完整 JSON 范例（v2.0.0 AI Agent 主题实测版）：

```json
{
  "hero": "/tmp/field-note-2026-09-05/imgs/cover-bg.png",
  "sections": [
    "/tmp/field-note-2026-09-05/imgs/p02.png",
    "/tmp/field-note-2026-09-05/imgs/p03.png",
    "/tmp/field-note-2026-09-05/imgs/p04.png",
    "/tmp/field-note-2026-09-05/imgs/p05.png",
    "/tmp/field-note-2026-09-05/imgs/p06.png",
    "/tmp/field-note-2026-09-05/imgs/p07.png",
    "/tmp/field-note-2026-09-05/imgs/p08.png",
    "/tmp/field-note-2026-09-05/imgs/p09.png"
  ],
  "title": "Agent 的幻觉",
  "subtitle": "企业真正需要的不是能自动干活的 AI",
  "content": [
    {"num":"01","label":"OBSESSION","paragraphs":[
      ["2024 到 2026 年，AI Agent 这个词从 OpenAI Assistants API 一路烧到多智能体协作、自主执行。"],
      ["VC 投。媒体吹。开发者建 Demo——一个 Agent 能自动完成整个工作流，另一个能跨平台调 10+ 个 API。", "", ""],
      ["", "两年时间，把「自主执行」这个酷炫技术吹成了新一轮基础设施革命的入场券。", ""]
    ],"img_idx":0}
  ],
  "footer_title": "Agent 真正进入主流，需要 3 到 5 年",
  "footer_body": [
    "企业知识库结构化程度达到某个阈值（现在普遍低于 20%）。",
    "关键业务流程有明确的成功失败标准（很多流程本身就是模糊的）。",
    "容错机制成熟（AI 出错后能快速回滚或补救）。"
  ],
  "date": "2026.09.06",
  "day": "Saturday",
  "gap": 80,
  "output": "/tmp/guancha-card-agent-2026-09-05.png"
}
```

---

> 基于扎克的自留地 harness-fields 方法论。CC BY 4.0。
> Source: https://github.com/zachshi-ai/harness-fields