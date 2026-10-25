---
name: field-note-layout
description: |
  生成自媒体长文的多页设计图（Field Note 风格排版）。午夜深蓝氛围，Noto Serif SC + Cormorant Garamond，
  固定 layout schema（四角坐标 + 主内容区），封面/内容/封底三类页面分开。
  Use when: 用户提到「field note」、「做一个 field note」、「扎克卡片」、
  「生成封面 + 内容页 + 封底」、或要求按 field-note 格式生成 X 主题内容时。
  （「笔记/手记/notion」等泛词不触发本 skill——那是 obsidian/notion 等笔记技能的触发词，
  避免撞车；「卡片」只有在搭配 field note / 扎克卡片 / 多页时才触发本 skill）
  生成后输出 PNG 并发回需求来源渠道（微信来的发微信、飞书来的发飞书，见 §4.3），
  HTML 源文件保留供本机浏览。
  注意：这是自媒体文章卡片生成 skill（扎克的口吻、面向读者的长文），不是田野笔记。
license: MIT
metadata:
  version: "2.2.4"
  category: design
  author: 扎克的自留地
---

# Field Note Layout Skill

生成自媒体长文的多页设计图（Field Note 风格排版）。午夜深蓝氛围，Noto Serif SC + Cormorant Garamond，无 emoji。

---

## §0. 写作规则（先于一切，违反 = 返工）

1. **口吻**：以扎克的第一人称口吻，从扎克的思考出发写文章给读者看，像亲口跟读者讲一个想法。
2. **禁止提信源**：读者不知道任何信源，全文禁止出现「文中提到」「在链接里」「据 XX 报道」「来源/参考」这类话，也禁止引用他人观点署名。直接写内容本身。
3. **全文禁止任何链接**：正文、脚注、引文、封底一律不允许 URL 或超链接；引文块只用文字。
4. **作者名与日期只允许出现在两处**：四角 corner（左下角由 generator 自动生成）和封底 .sign-off 落款。正文/副标题下方禁止再写作者名或日期。
5. **正文只用 Noto Serif SC**，禁止花体字、斜体、书法体（详见 §二）。
6. **回传渠道 = 来源渠道**：需求从哪个渠道来就发回哪个渠道（微信来的发微信、飞书来的发飞书），禁止默认发微信、禁止跨渠道发送（详见 §4.3）。

---

## 一、Layout Schema（布局规范）

所有坐标写死，内容只允许填充进指定区域。

### 1.1 页面尺寸
```
body: width 540px, height 960px
layer: height 960px
```

### 1.1b 页数下限（硬规则）

```
总页数 = 1 封面 + N 内容页 + 1 封底，N ≥ 6
即 TOTAL ≥ 8（例：11 页 = 1 封面 + 9 内容 + 1 封底；8 页 = 1 + 6 + 1）
```

- **内容页少于 6 页 = 内容不完整，禁止交付**
- 内容页超过 6 页正常（按内容量分页），上限以每页内容不溢出为准
- check.py 会校验 `--total ≥ 8` 和页码 01..TOTAL 齐全

### 1.2 固定坐标（所有页通用）

```
四角坐标（corner 元素）：
  左上 top-left:    top 28px,  left 28px
  右上 top-right:   top 28px,  right 28px
  左下 bottom-left: bottom 60px, left 28px
  右下 bottom-right: bottom 60px, right 28px

  字体: Noto Serif SC, 9px, z-index 20
  行高: line-height 1.5
  换行: white-space: nowrap（禁止自动换行，只允许 <br> 显式分行）
  页码: 一律两位数字（01 / 02 / 10 / 11 / 13），总数也两位（→ 03/11）

主内容区（main 元素）：
  padding: 0 44px 44px
  flex column + justify-content: center + align-items: flex-start（垂直居中）
  layer padding-top: 52px（避让四角）
```

> 页码格式是硬规则：`{page:02d}`，任何一位数的 1 / 2 / 9 都是错误。

### 1.3 配色板（写死）
```
背景: #0d1117
amber强调: rgba(255,180,80,0.38) / rgba(255,180,80,0.6) 等
柔蓝强调: rgba(88,166,255,0.35) / rgba(88,166,255,0.4) 等
正文灰: #d6dde6
标题白: #ffffff
背景渐变: body::after radial-gradient
```

### 1.4 页面类型与四角内容

#### 封面（type: cover）
```
top_left:  "Field Notes"
top_right: "{PAGE_NUM}"              # 例: 01, 格式两位数字
bottom_left: "{AUTHOR}\\n{DATE_STR} / {DAY_STR}"  # 两行
bottom_right: "→ {NEXT_PAGE_NUM}/{TOTAL}"         # 例: → 02/11

layer 背景：生图能力按文章主题生成的写实风格图 + 半透明黑色蒙版
  蒙版: linear-gradient(rgba(13,17,23,0.5), rgba(13,17,23,0.8))  // 0.5→0.8 中间值，不能太重
  background-size: cover; background-position: center;
  调用方式: python3 generator.py --type cover --cover-bg "<生图产出的本地文件路径>" ...
  生图要求:
    - 必须调用生图能力（mmx-cli / minimax 生图），根据文章主题生成写实风格图片
    - 禁止使用示例图 / 随便找的网图 / Unsplash 图片（旧版曾内置示例图，已废弃）
    - 生图产出的是本地文件，--cover-bg 传本地路径即可（generator 自动转 file://）

main 布局：垂直居中
  justify-content: center
  align-items: flex-start
  flex-direction: column
  padding-top: 0（不走 .layer 的 52px 顶部偏移）
  text-shadow: 0 1px 12px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9)  // 底图背景下保证可读

主内容区（严格，只有这三块，按顺序）：
  category 标签 → 大标题 → 副标题
  - **必须用 skill 提供的三个标准 class**（v2.3.0 起，CSS 写死）：
    - category 标签 → `<div class="cat">KNOWLEDGE / FIELD NOTES</div>`
    - 大标题       → `<h1 class="title">…</h1>`
    - 副标题       → `<p class="sub">…</p>`
  - 禁止手写 inline style 代替 class、禁止自创其他 class（class 不存在 = 文字直接消失）
  - 副标题就是封面的最后一行，**下面禁止再放任何东西**（引言、金句、作者、日期一律禁止）
  - 禁止 border-left 竖线引言块（旧版引言区已废弃）
```

#### 内容页（type: content）
```
top_left:  "{THEME_KEYWORD}"          # 极度精炼的主题词，禁止换行
top_right: "{PAGE_NUM}"               # 例: 02, 两位数字
bottom_left: "{AUTHOR}\\n{DATE_STR}" # 两行
bottom_right: "→ {NEXT_PAGE_NUM}/{TOTAL}"         # 例: → 03/11
```

#### 封底（type: back）
```
top_left:  "Field Notes"
top_right: "{PAGE_NUM}"              # 例: 13, 两位数字
bottom_left: "{DATE_STR} / {DAY_STR}" # 两行
bottom_right: ""                     # 空白

主内容区：水平居中 + 垂直居中（唯一允许的页面布局）
  justify-content: center; align-items: center; text-align: center

内容限制（严格）：
  - 只允许一段结束语（一两句话收尾，居中）
  - 落款固定用 .sign-off 组件（generator 自动生成）：
    <div class="sign-off">—— {AUTHOR} ——</div>
    位置：结束语下方 36px，Cormorant Garamond italic 11px，rgba(255,255,255,0.32)
  - 禁止额外写作者名 / 再写一遍作者 / 加日期（作者只允许出现在 .sign-off 和左下角 corner）
  - 禁止任何链接 / URL
```

---

## 二、字体规范

- **中文正文/标题**: Noto Serif SC, font-weight 400/700（**唯一允许的正文字体**，2026-09-05 起去掉 300 浅重，对比度优先）
- **英文/标签/页码**: Cormorant Garamond, italic, 9-10px（仅限四角英文标签与页码）
- **category标签**: Cormorant Garamond, italic, uppercase, font-size 17px, letter-spacing 7px, color #ffb450 实色
- **正文标题/段标题**: Noto Serif SC 700 实色 #ffffff，封面 .title 46px / 内容页 .st 30px
- **正文**: Noto Serif SC 400 实色 #d6dde6，.prose 18px
- **pullquote / analogy-box / research-box / engineer-box 正文**: Noto Serif SC 400 实色 #f0f4f8，18px
- **封底落款**: Cormorant Garamond italic 11px（.sign-off 组件，唯一例外）

**2026-09-05 字号+颜色规范升级（v2.2.4）**：
- 全部字号上调 2-8px（标题 38→46 / 段标题 25→30 / 正文 13.5→18）
- 全部 rgba 半透明改为 hex 实色（对比度大幅提升）
- 字号/颜色不再写死在 SKILL.md 文字描述里，以本文 §五 CSS 模板和 generator.py line 99-116 为唯一权威来源
- **禁止**:
  - Ma Shan Zheng 等书法体、花体、装饰体
  - 正文（含 prose / pullquote / box 内文字）出现任何斜体、花体、非 Noto Serif SC 字体
  - 用字体变化代替排版（如用斜体做强调——用 `.em` 加粗即可）

---

## 三、内容区规则

### 3.1 主内容区（main）
- padding: 72px 44px（固定，不允许改）
- 布局：**垂直居中** = `justify-content: center` + `align-items: flex-start`（内容页/封面）
- 内容溢出：截断或分页，不撑开布局
- 内容不足：靠 justify-content: center 居中，**不要用 space-between 撑开**

### 3.2 左上角主题词（左上角内容页）
- 必须极度精炼（建议不超过8个中文字）
- 超长 = 提炼不够，不接受换行
- 如需分行，强制另起一页

### 3.3 封面主内容区（v2.2.3 起无引言区）
- 只允许三块，按顺序：category 标签 → 大标题 → 副标题
- **副标题下方禁止任何内容**：引言/金句/作者/日期一律不要（旧版 border-left 引言区已废弃）
- 封面不要用 border-left 竖线装饰

### 3.4 正文页配图（hero）
- **必须通过 `--hero <图片路径/URL>` 参数生成**，禁止手写 img 标签、禁止自己改图片版式
- 版式由 generator 按图片宽高比自动判定（写死，不用模型操心）：
  - 宽图/方图（宽:高 ≥ 1.1）→ 固定高度 110px + object-fit: cover（裁剪填充，防止撑爆页面）
  - 长图/截图（宽:高 < 1.1）→ 高度自适应 + max-height 300px + 宽度按比例 + object-fit: contain，水平居中（**完整显示，绝不裁剪**）
- 想要图出现在指定位置：在 content 字符串里放 `{HERO}` 占位符
- **配图下方禁止加 caption / 图注 / 任何描述文字**：正文页配图只允许图片本身，不允许 `<figcaption>`、`.img-caption`、图注文字、图片说明。skill 与 generator 均不再提供 caption 支持（2026-08-21 扎劳斯确认）。

### 3.5 空缺填充
- 主内容区图片：无图片时用纯色渐变背景
- img 加 `background:rgba(255,255,255,0.05)` 防止加载失败裂开
- **封面背景图不允许空缺时放示例图**：必须生图（见 §1.4 封面）

---

## 四、生成流程

### 4.1 Python 生成脚本

```bash
# 封面（背景图 = 生图产出的本地文件；生图命令见 4.4）
python3 generator.py --type cover --num 1 --total 13 \
  --cover-bg "/tmp/cover-gen.png" \
  --content "..." --output /tmp/p01.html

# 正文页（配图自动判定版式，{HERO} 控制位置）
python3 generator.py --type content --num 2 --total 13 \
  --theme "主题词" --content "<div class=\"st\">...</div>|{HERO}|<p class=\"prose\">...</p>" \
  --hero "/tmp/screenshot.png" \
  --output /tmp/p02.html

# 封底（结束语 + .sign-off 落款自动生成）
python3 generator.py --type back --num 13 --total 13 \
  --content "<p class=\"prose\">结束语</p>" --output /tmp/p13.html
```

页码/总数格式（写死）：`{page_num:02d}` / `{total:02d}` → 01、02、10、11、13；右下角 `→ {next:02d}/{total:02d}`。

### 4.2 截图
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 每次截图前杀掉残留Chrome进程（防止缓存导致空白图）
pkill -f "Chrome.*headless" 2>/dev/null
sleep 1

# 本机 Chrome 必须带 swiftshader/no-sandbox，否则 GPU 进程崩溃无法截图（2026-08-16 确认）
"$CHROME" --headless \
  --disable-gpu --use-angle=swiftshader --disable-software-rasterizer --no-sandbox \
  --screenshot="/tmp/output.png" \
  --window-size=540,960 \
  --force-device-scale-factor=3 \
  --virtual-time-budget=5000 \
  "file:///path/to/page.html"
```

### 4.3 回传：发回需求来源渠道（不是默认发微信）

**核心规则：需求从哪个渠道来，就发回哪个渠道。** 从当前会话上下文判断来源渠道、账号、目标，禁止写死账号/目标，禁止默认发微信。

```bash
# 微信来的需求 → 用微信专门发图能力（message send --media 发图片消息，不是发文件/文档）：
openclaw message send \
  --channel openclaw-weixin \
  --account "<来源会话的微信账号 id>" \
  --target "<来源会话的 peer id>" \
  --media "/tmp/output.png" \
  --message "{标题}"

# 飞书来的需求 → 发回飞书（chat_id 或 open_id）：
openclaw message send \
  --channel feishu \
  --account "<飞书应用账号 id>" \
  --target "<chat_id 或 open_id>" \
  --media "/tmp/output.png" \
  --message "{标题}"

# 其他渠道（telegram / discord / qqbot ...）→ 同样用对应 --channel + 来源会话的 --account/--target
# 本地 / CLI 直接调用 → 只保存 PNG，不发送
```

也支持一行脚本直接发（--send 配合渠道参数）：

```bash
python3 generator.py ... --screenshot /tmp/output.png \
  --send "{标题}" --channel feishu --account "<账号>" --target "<chat_id>"
```

- **禁止**：默认发微信 / 跨渠道发送（微信来的发到飞书）/ 写死账号与 target（每次从来源会话取）
- 微信渠道发图必须走 `--media`（图片消息），不要用发文件/文档的方式

### 4.4 封面背景图：必须生图（v2.1.0 起）

```bash
# 用生图能力（mmx-cli / minimax 生图）按文章主题生成写实风格图，例如：
mmx image "写实风格，{文章主题}，深夜氛围，深蓝色调，细节丰富" --output /tmp/cover-gen.png
# 再把本地文件传给 generator（自动转 file://，不需要手动处理路径）：
python3 generator.py --type cover ... --cover-bg "/tmp/cover-gen.png"
```

- 生图 prompt 必须包含文章核心主题 + 写实风格要求
- **禁止**：Unsplash 示例图 / 随手网图 / 旧版推荐主题图（已废弃）
- 封面底图只做氛围背景（上面有 0.5→0.8 蒙版），不需要图里出现文字

### 4.5 出图前强制检查（最后一道闸，必须执行）

**生成全部页面后、回传之前，必须运行 check.py；有任何 FAIL 就修复并重跑，全部 PASS 才允许继续。**

```bash
python3 check.py --total 13 p01.html p02.html ... p13.html
```

check.py 逐页校验 15 项（任一 FAIL 即 exit 1）：
1. 四角元素齐全
2. 右上角页码两位数字（01/02/10/11/13）
3. 右下角 `→ 03/13` 格式（cover/content），封底为空白
4. 左下角作者归属（cover/content 有作者，封底无）
5. 左上角主题词非空且不换行；封面/封底 = "Field Notes"
6. 封面带生图背景（非 unsplash/网图）
7. main 一律 justify-content:center（垂直居中）
8. 封底水平+垂直居中、恰一个 .sign-off、正文无额外作者
9. cover/content 正文区禁止作者名
10. 封面 main 内禁止日期
11. img 必须带 hero-img class 且无 style（禁止手写版式）
12. 字体白名单（Noto Serif SC / Cormorant Garamond），正文组件禁斜体
13. 全文禁止链接（<a> / href / http(s):// / www.）
14. 无 <cite>（信源禁止）
15. 最后一页（页码 == total）必须是封底
16. 页数下限与完整性：TOTAL ≥ 8（1 封面 + ≥6 内容 + 1 封底），页码 01..TOTAL 齐全不重复

流程：生成所有页 → `check.py` → 全 PASS → 截图 → 回传来源渠道（§4.3）。FAIL 必须先修。

---

## 五、CSS 模板（写死的 layout.css）

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  width: 540px;
  min-height: 960px;
  background: #0d1117;
  font-family: 'Noto Serif SC', serif;
  position: relative;
  overflow: hidden;
}

body::after {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(ellipse 70% 60% at 85% 15%, rgba(255, 180, 88, 0.12) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 15% 85%, rgba(88, 166, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* ===== 四角坐标（写死）===== */
.corner {
  position: absolute;
  font-family: 'Noto Serif SC', serif;
  font-size: 9px;
  z-index: 20;
  line-height: 1.5;
  letter-spacing: 2px;
  white-space: nowrap;   /* 禁止自动换行，只允许 <br> */
}
.corner-tl { top: 28px; left: 28px; color: rgba(255,255,255,0.28); }
.corner-tr { top: 28px; right: 28px; color: rgba(255,180,80,0.38); text-align: right; }
.corner-bl { bottom: 60px; left: 28px; color: rgba(255,255,255,0.18); }
.corner-br { bottom: 60px; right: 28px; color: rgba(255,180,80,0.38); text-align: right; }

/* ===== 主内容区（写死）===== */
.layer {
  position: relative;
  z-index: 1;
  height: 960px;
  display: flex;
  flex-direction: column;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;  /* 垂直居中（生成器按页型注入 MAIN_STYLE） */
  align-items: flex-start;
  padding: 0 44px 44px;
}

/* ===== 内容组件（可复用）===== */
.st { font-family: 'Noto Serif SC', serif; font-weight: 700; font-size: 30px; letter-spacing: 1px; color: #ffffff; margin-bottom: 14px; }
.prose { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.85; color: #d6dde6; margin-bottom: 14px; }
.prose .em { color: #ffffff; font-weight: 700; }
.pullquote { border-left: 3px rgba(255,180,80,0.4); background: rgba(255,180,80,0.06); padding: 12px 16px; margin: 10px 0; }
.pullquote-text { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.75; color: #f0f4f8; }
.pullquote cite { display: none; }  /* 来源一律隐藏：全文不提信源 */
.analogy-box { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 12px 16px; margin: 10px 0; }
.analogy-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }
.research-box { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07); border-radius: 6px; padding: 14px 16px; margin: 10px 0; }
.research-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }
.engineer-box { background: rgba(88,166,255,0.05); border: 1px solid rgba(88,166,255,0.15); border-radius: 6px; padding: 13px 16px; margin: 10px 0; }
.engineer-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }

/* ===== 配图（写死，由 --hero 自动判定，禁手写 img 改版式）===== */
.hero-wrap { width: 100%; margin: 0; }   /* main 是 flex 容器，figure 必须显式 width:100% */
.hero-img { width: 100%; display: block; border-radius: 4px; margin-bottom: 12px; background: rgba(255,255,255,0.04); }
.hero-cover { height: 110px; object-fit: cover; }        /* 宽图/方图：固定高度防撑爆 */
.hero-contain { height: auto; max-height: 300px; width: auto; max-width: 100%; margin: 0 auto 12px; object-fit: contain; }  /* 长截图：完整显示不裁剪，居中 */
.img-caption { font-family: 'Noto Serif SC', serif; font-size: 8.5px; letter-spacing: 2px; color: rgba(255,180,80,0.38); margin-bottom: 10px; }

/* 封底落款（唯一作者出现处，写死） */
.sign-off { margin-top: 36px; font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 11px; color: rgba(255,255,255,0.32); letter-spacing: 3px; text-align: center; }
```

---

## 六、多页结构参考

### Page 1：封面
- 左上: `Field Notes`
- 右上: `01`（两位）
- 左下: `扎克的自留地\n{DATE_STR} / {DAY_STR}`
- 右下: `→ 02/11`（页码/总数都两位）
- 主内容区: category标签 + 大标题 + 副标题（副标题是最后一行，**下方禁止任何内容**）
- 背景图: 生图能力按主题生成的写实图（见 §4.4）

### Page 2~N：内容页
- 左上: `{主题提炼短语}`（精炼，不换行）
- 右上: `{PAGE_NUM}`（两位，如 02）
- 左下: `扎克的自留地\n{DATE_STR}`
- 右下: `→ {NEXT:02d}/{TOTAL:02d}`（如 → 03/11）
- 主内容区: st标题 + prose正文 + pullquote/analogy-box/research-box；配图走 `--hero`（自动 cover/contain）

### 最后一页：封底
- 左上: `Field Notes`
- 右上: `{LAST_PAGE_NUM}`（两位数字）
- 左下: `{DATE_STR} / {DAY_STR}`
- 右下: 空白
- 主内容区: **水平居中 + 垂直居中**，只允许一段结束语 + `.sign-off` 落款
- 禁止: 链接 / 额外作者 / 日期

---

## 七、已知问题与模型常见错误（违反即返工）

技术已知问题：
- Chrome headless 截图前必须 `pkill -f "Chrome.*headless"` 杀掉残留进程，否则返回空白缓存图
- 封面有外部图资源时，截图命令必须加 `--virtual-time-budget=5000` 等待网络图加载完再截图
- `body::after` 的 radial-gradient 在某些 headless 环境下有断层，属已知限制，HTML本机浏览正常

模型常见错误清单（v2.1.0 起列为硬规则，禁止再犯）：
- ❌ 封面背景用 Unsplash 示例图/网图 → **必须生图**（§4.4）
- ❌ 副标题下再写一遍作者名、加日期 → **禁止**（作者只在左下角 corner）
- ❌ 页码写 1 / 2 / 9 一位数 → **必须两位**（01 / 02 / 10 / 11 / 13）
- ❌ hero 长截图被裁剪 → 用 `--hero` 自动判定，长图走 contain 完整显示
- ❌ 主内容区不垂直居中 / 用 space-between 撑开 → **统一 center**
- ❌ 正文用花体字、斜体、书法体 → **正文只用 Noto Serif SC**
- ❌ 封底不居中 / 加链接 / 额外写作者 → **只允许结束语 + .sign-off**
- ❌ 文中提信源（"文中提到""在链接里""据 XX"）→ **全文禁止**
- ❌ 手写 img 标签 / 自己调图片版式 → **只走 `--hero` 参数**
- ❌ 配图下加 caption / 图注 / 描述文字 → **禁止**（v2.4.0 起 skill 与 generator 全面移除 caption 支持）
- ❌ 生成完不检查就发送 → **必须跑 check.py（§4.5），全 PASS 才允许**
- ❌ 内容页少于 6 页 / 缺页就交付 → **页数下限 hard rule（§1.1b），check.py 第 16 项拦截**
- ❌ 默认发微信 / 跨渠道发送 / 写死账号和 target → **回传来源渠道**（§4.3），微信发图走 `--media` 图片消息

## 八、标准参考页（p10 三个转折点）

p10 是 2026-06-01 确认的标准布局参考。各参数值固定为：

- .hero-img: 宽图 height 110px / 长图 max-height 300px contain 居中, border-radius 4px, margin-bottom 12px
- .img-caption: Noto Serif SC 8.5px（非斜体）, color rgba(255,180,80,0.35), margin-bottom 10px
- 内容页 main: justify-content: center, align-items: flex-start, flex-direction: column
- .st: Noto Serif SC 700, 21px, letter-spacing 1px, margin-bottom 10px
- .prose: Noto Serif SC 300, 13.5px, line-height 1.85, margin-bottom 10px
- 主角命题区空间：上边距 ≈138px，下边距 ≈130px（960px 页面下居中平衡点）

页脚字段：下三角形 6 个 benchmark、表题—表题结尾。封面不设引言边框（v2.2.3 起）。

任何新生成页低于这个标准 = 变体，不接受。
