# 扎克卡片 · 观猹卡片

同一个话题，两套排版。前者是 8 页竖版长图（封面 + 6 内容 + 封底），后者是一张信息密集的专版长图。两者共用一套「先定结构、再灌内容、最后渲染」的引擎。

## 目录

```
engine/
  field-note/   generator.py + template.html + SKILL.md   —— 8 页卡片引擎（固定四角坐标 + 主内容区）
  guancha/      generator.py + SKILL.md                  —— 观猹专版引擎（hero + 编号段 + 多图）
scripts/
  build-field-note.py     旧版调用示例（8 页）
  build-field-note-v2.py  当前版调用示例
  build-guancha.py        观猹专版调用示例
  gen-images.sh           配图生成（16:9 / 3:4 按页型分配，统一质感提示词）
samples/
  field-note/  封面 / 内容页 / 封底
  guancha/     专版整图
```

## 用法

```bash
cd scripts
python3 build-field-note-v2.py   # → ../out/field-note/p01..p08.png
python3 build-guancha.py         # → ../out/guancha/*.png
```

配图放 `scripts/img/`，命名与脚本里的文件名对应；`gen-images.sh` 是生成配图的那一段提示词，可按栏目替换。

## 排版要点

- **一套坐标**：版面全部按 1248×1872 的四角坐标 + 主内容区切分，改版只改坐标不改内容
- **三类页分工**：封面给钩子，内容页给一段一个论点，封底回收 + CTA
- **字体纪律**：标题衬线、正文无衬线，字号只有 3 级，行距固定
- **配图不抢字**：图占中段、四边留白，任何图片不得压住正文区
- **无角标**：所有图不带水印 / AI 标识

## 依赖

- 8 页卡片：`python3` + 本地 chromium（无头渲染 HTML → PNG，脚本会自动找 `/usr/bin/chromium` 或 Playwright 缓存）
- 观猹专版：`python3` + Pillow（PIL 直接绘制，不依赖浏览器）
- 字体：Noto Serif SC / Cormorant Garamond

## 说明

`samples/` 为 2026.10.18 一期成品，话题「一百万个 token」。代码 MIT。
