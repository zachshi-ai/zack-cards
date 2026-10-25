#!/usr/bin/env python3
"""
guancha-card generator v1.0
生成单张长图格式的自媒体卡片：四角固定 + 多图 + 分段正文，PIL 全宋体。
用法:
  python3 generator.py --hero /path/to/cover.png \
      --sections /path/to/p02.png /path/to/p03.png ... \
      --title "标题" --subtitle "副标题" \
      --content "01,DEAL,pre,mid,suf,img_idx|02,SIGNAL,..." \
      --footer-title "页脚标题" --footer-body "正文段落" \
      --date "2026.08.18" --day "Tuesday" \
      --gap 80 --output /tmp/guancha-card.png
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import argparse
import json

SCALE = 3
W = 540 * SCALE

FONT_SONG = '/System/Library/Fonts/Supplemental/Songti.ttc'
FONT_EN   = '/System/Library/Fonts/Helvetica.ttc'
# Linux 兼容回退：Noto Serif CJK SC（macOS 上仍优先宋体，不受影响）
FONT_SONG_FALLBACK = [
    '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc',
    '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]

def load_font(size_pt, weight="regular"):
    """weight: "regular"/"bold"/"black"。Songti.ttc index=6=Regular, 1=Bold, 0=Black（最粗）"""
    if weight == "black":
        paths_idx = [
            (FONT_SONG, 0),  # Songti SC Black（最粗）
            (FONT_EN, 1),    # Helvetica Bold fallback
        ]
    elif weight == "bold":
        paths_idx = [
            (FONT_SONG, 1),  # Songti SC Bold
            (FONT_EN, 1),    # Helvetica Bold
        ]
    else:  # regular
        paths_idx = [
            (FONT_SONG, 6),  # Songti SC Regular
            (FONT_EN, 0),    # Helvetica Regular
        ]
    for p, idx in paths_idx:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size_pt * SCALE, index=idx)
            except:
                pass
    # Linux 兼容回退：Noto Serif/Sans CJK SC（index=2 为简体中文）
    for p in FONT_SONG_FALLBACK:
        if os.path.exists(p):
            for idx in (2, 0):
                try:
                    return ImageFont.truetype(p, size_pt * SCALE, index=idx)
                except:
                    continue
    return ImageFont.load_default()

def draw_paragraph(drawer, x, y, parts, max_w, line_h, font):
    """逐字渲染段落，支持高亮三元组 (pre, mid, suf)"""
    colors = [(212, 222, 232), (180, 192, 205), (212, 222, 232)]
    cur_x, cur_y = x, y
    for (text, color) in zip(parts, colors):
        for ch in text:
            bbox = drawer.textbbox((0, 0), ch, font=font)
            cw = bbox[2] - bbox[0]
            if cur_x + cw > x + max_w:
                cur_x = x
                cur_y += line_h
            drawer.text((cur_x, cur_y), ch, fill=color, font=font)
            cur_x += cw
    return cur_y + line_h


def wrap_text_centered(drawer, text, max_w, font):
    """按 max_w 把 text 切成多行，每行水平居中绘制。返回 (final_y_after, lines_count)"""
    color = (212, 222, 232)
    if not text:
        return 0, 0
    # 先切分成多行（逐字累积）
    lines = []
    cur_line = ''
    for ch in text:
        test = cur_line + ch
        bbox = drawer.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and cur_line:
            lines.append(cur_line)
            cur_line = ch
        else:
            cur_line = test
    if cur_line:
        lines.append(cur_line)
    # 每行居中绘制（让出外层 y 增量）
    return len(lines), lines

# === 字体实例 ===
font_corner   = load_font(18)
font_title    = load_font(56, weight="black")  # 2026-09-06 反馈"加粗"，用 Black 最粗字重
font_sub      = load_font(26, weight="bold")
font_sec_num  = load_font(64)
font_sec_lbl  = load_font(15)
font_body     = load_font(24)
font_footer_t = load_font(28)
font_footer_b = load_font(22)
font_sign     = load_font(22)

PAD          = 28 * SCALE
HERO_H       = 400 * SCALE
SEC_NUM_H     = 70 * SCALE
SEC_PAR_H     = 38 * SCALE
SEC_IMG_H     = 240 * SCALE
TRANSITION_H  = 150 * SCALE
IMG_RADIUS   = 8 * SCALE  # 配图圆角 @1x = 8px

def parse_sections(content_str, sec_imgs):
    """解析 content_str: 'num,label,pre,mid,suf,img_idx|num,label,...'
    返回 [(num, label, [(pre,mid,suf), ...], img_idx), ...]
    """
    sections = []
    for entry in content_str.split('|'):
        parts = entry.split(',')
        num = parts[0]
        label = parts[1]
        img_idx = int(parts[-1])
        pre = parts[2]
        suf = parts[-2]
        mid = ','.join(parts[3:-2])
        paras = [(pre, mid, suf)]
        sections.append((num, label, paras, img_idx))
    return sections

def load_config(args):
    """从 --config JSON 加载参数，覆盖 CLI 默认值"""
    if args.config:
        with open(args.config) as f:
            cfg = json.load(f)
        for k, v in cfg.items():
            setattr(args, k, v)
        if 'content' in cfg and isinstance(cfg['content'], list):
            # JSON list 格式: [{num,label,paragraphs,img_idx}, ...]
            sections = []
            for item in cfg['content']:
                num = item['num']
                label = item['label']
                img_idx = item.get('img_idx', 0)
                paras = [tuple(p) for p in item['paragraphs']]
                sections.append((num, label, paras, img_idx))
            args._sections_parsed = sections
        else:
            args._sections_parsed = None
    else:
        args._sections_parsed = None
    return args

def build(args):
    # 解析 sections（优先用 JSON 加载的，否则 CLI 字符串解析）
    if hasattr(args, '_sections_parsed') and args._sections_parsed is not None:
        sections = args._sections_parsed
    else:
        sections = parse_sections(args.content, args.sections)

    canvas = Image.new('RGB', (W, 99999), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    y = 100 * SCALE

    # === HERO: 保持原图比例，高度按 HERO_H，宽度按比例（不拉伸）===
    hero_full = Image.open(args.hero).convert('RGB')
    scale = HERO_H / hero_full.height
    new_w = int(hero_full.width * scale)
    new_h = HERO_H
    hero_resized = hero_full.resize((new_w, new_h), Image.LANCZOS)
    region = Image.new('RGB', (W, HERO_H), (13, 17, 23))
    if new_w >= W:
        # 图比视口宽 → 居中裁切左右
        left = (new_w - W) // 2
        region.paste(hero_resized.crop((left, 0, left + W, new_h)), (0, 0))
    else:
        # 图比视口窄 → 居中，背景色填充两侧
        paste_x = (W - new_w) // 2
        region.paste(hero_resized, (paste_x, 0))
    overlay = Image.new('RGBA', (W, HERO_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for ty in range(TRANSITION_H):
        a = int(((TRANSITION_H - ty) / TRANSITION_H) ** 1.2 * 255)
        od.line([(0, ty), (W, ty)], fill=(13, 17, 23, a))
    for ty in range(TRANSITION_H):
        yp = HERO_H - TRANSITION_H + ty
        a = int((ty / TRANSITION_H) ** 1.2 * 255)
        od.line([(0, yp), (W, yp)], fill=(13, 17, 23, a))
    hero_final = Image.alpha_composite(region.convert('RGBA'), overlay).convert('RGB')
    canvas.paste(hero_final, (0, y))
    y += HERO_H + 16 * SCALE

    draw2 = ImageDraw.Draw(canvas)
    hty = y - 240 * SCALE  # 2026-09-06 v1.1.2 再上移 70px @1x，累计向上 110px @1x，离开 hero 底部边缘
    draw2.text((32*SCALE, hty), args.title, fill=(240,244,248), font=font_title)
    draw2.line([(32*SCALE, hty+90*SCALE), (72*SCALE, hty+90*SCALE)], fill=(255,180,80), width=2*SCALE)  # 2026-09-06 v1.1.2 标题底+24px @1x 留白后再分隔线
    draw2.text((32*SCALE, hty+100*SCALE), args.subtitle, fill=(220,226,235), font=font_sub)  # 2026-09-06 v1.1.2 跟随分隔线

    # === SECTIONS ===
    for (num, label, paras, img_idx) in sections:
        y += 48 * SCALE
        draw2.text((PAD, y), num, fill=(255,180,80), font=font_sec_num)
        y += SEC_NUM_H + 8*SCALE
        draw2.text((PAD, y), label, fill=(255,180,80), font=font_sec_lbl)
        y += 18*SCALE
        for parts in paras:
            y = draw_paragraph(draw2, PAD, y, parts, W-2*PAD, SEC_PAR_H, font_body) + 20*SCALE
        img_path = args.sections[img_idx] if img_idx < len(args.sections) else None
        if img_path and os.path.exists(img_path):
            src = Image.open(img_path)
            sw, sh = src.size
            # 图片左右留 PAD 边距（与正文对齐），不拉满全宽
            IMG_W = W - 2 * PAD  # 1452px @3x = 484px @1x
            scaled = src.resize((IMG_W, int(IMG_W*sh/sw)), Image.LANCZOS).convert('RGB')
            sec_crop = scaled.crop((0, 0, IMG_W, SEC_IMG_H))
            # 配图加圆角（IMG_RADIUS）
            round_mask = Image.new('L', (IMG_W, SEC_IMG_H), 0)
            md = ImageDraw.Draw(round_mask)
            md.rounded_rectangle((0, 0, IMG_W-1, SEC_IMG_H-1), radius=IMG_RADIUS, fill=255)
            canvas.paste(sec_crop, (PAD, y), round_mask)
        y += SEC_IMG_H + 24*SCALE

    # === FOOTER ===
    y += 40 * SCALE
    div_y = y + 30 * SCALE
    draw2.line([(W//2-50*SCALE, div_y), (W//2-10*SCALE, div_y)], fill=(255,180,80), width=SCALE)
    draw2.ellipse([(W//2-3*SCALE, div_y-3*SCALE), (W//2+3*SCALE, div_y+3*SCALE)], fill=(255,180,80))
    draw2.line([(W//2+10*SCALE, div_y), (W//2+50*SCALE, div_y)], fill=(255,180,80), width=SCALE)
    y += 70 * SCALE

    bbox_t = draw2.textbbox((0,0), args.footer_title, font=font_footer_t)
    draw2.text(((W-(bbox_t[2]-bbox_t[0]))//2, y), args.footer_title, fill=(255,180,80), font=font_footer_t)
    y += 40 * SCALE

    # 兼容 footer_body 为 list 或字符串
    # 页脚正文：每个 list 元素内部按宽度 wrap + 居中绘制（修 2026-09-06 扎劳斯反馈"结尾没按宽度换行"）
    footer_items = args.footer_body if isinstance(args.footer_body, list) else args.footer_body.split('\n')
    footer_max_w = W - 2 * PAD
    for item in footer_items:
        wrapped_count, wrapped_lines = wrap_text_centered(draw2, item, footer_max_w, font_footer_b)
        if wrapped_count == 0:
            continue
        for wl in wrapped_lines:
            bbox = draw2.textbbox((0, 0), wl, font=font_footer_b)
            draw2.text(((W-(bbox[2]-bbox[0]))//2, y), wl, fill=(212,222,232), font=font_footer_b)
            y += 32*SCALE  # 加大行距（font_footer_b=22pt × 3 = 66px，行距 96px，约 45% 额外）
        # 段间额外空白
        y += 12*SCALE

    y += 30 * SCALE
    bbox_s = draw2.textbbox((0,0), '—— 扎克的自留地 ——', font=font_sign)
    draw2.text(((W-(bbox_s[2]-bbox_s[0]))//2, y), '—— 扎克的自留地 ——', fill=(190,195,205), font=font_sign)
    y += 24*SCALE
    bbox_sub = draw2.textbbox((0,0), '观猹专版', font=font_corner)
    draw2.text(((W-(bbox_sub[2]-bbox_sub[0]))//2, y), '观猹专版', fill=(255,180,80), font=font_corner)
    y += 24*SCALE

    # === 底部黑底 + 四角 ===
    y += 60 * SCALE
    BOTTOM_H = y + 60 * SCALE
    canvas_final = canvas.crop((0, 0, W, BOTTOM_H))
    df = ImageDraw.Draw(canvas_final)

    # 顶部四角
    df.text((24*SCALE, 24*SCALE), 'AI INFRASTRUCTURE', fill=(255,180,80), font=font_corner)
    rt = '扎克的自留地（观猹专版）'
    br = df.textbbox((0,0), rt, font=font_corner)
    df.text((W-24*SCALE-(br[2]-br[0]), 24*SCALE), rt, fill=(240,244,248), font=font_corner)

    # 底部四角（descent 精确 baseline）
    gap_px = args.gap * SCALE
    bbox_date = font_corner.getbbox(args.date)
    bbox_day  = font_corner.getbbox(args.day)
    date_baseline = BOTTOM_H - gap_px - bbox_date[3]
    df.text((24*SCALE, date_baseline), args.date, fill=(190,195,205), font=font_corner)
    day_baseline  = BOTTOM_H - gap_px - bbox_day[3]
    bd = df.textbbox((0,0), args.day, font=font_corner)
    df.text((W-24*SCALE-(bd[2]-bd[0]), day_baseline), args.day, fill=(255,180,80), font=font_corner)

    os.makedirs(os.path.dirname(args.output) or '/tmp', exist_ok=True)
    canvas_final.save(args.output, optimize=True)
    print(f'生成: {W}x{BOTTOM_H} @3x = {W//3}x{BOTTOM_H//3} @1x → {args.output}')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='guancha-card generator v1.0')
    p.add_argument('--config', help='JSON 配置文件路径（推荐；完整示例见 example/stripe-20260817.json）')
    p.add_argument('--hero', help='封面图路径')
    p.add_argument('--sections', nargs='+', help='配图路径列表（顺序对应 img_idx）')
    p.add_argument('--title', help='封面标题')
    p.add_argument('--subtitle', help='封面副标题')
    p.add_argument('--content', help='章节内容（CLI 简化字符串格式：num,label,pre,mid,suf,img_idx|num,...）')
    p.add_argument('--footer-title', help='页脚标题')
    p.add_argument('--footer-body', help='页脚正文（\\n 分行）')
    p.add_argument('--date', help='左下角日期')
    p.add_argument('--day', help='右下角星期')
    p.add_argument('--gap', type=int, default=80, help='底部四角距底边 px @1x')
    p.add_argument('--output', default='/tmp/guancha-card.png', help='输出路径')
    p.add_argument('--footer-body-list', nargs='+', dest='footer_body_list', help='页脚正文多行（CLI 模式推荐，与 --footer-body 二选一）')
    args = p.parse_args()
    # 必填校验：要么 --config 要么所有 CLI 参数
    if not args.config:
        required = ['hero','sections','title','subtitle','content','footer-title','date','day']
        missing = [r for r in required if not getattr(args, r.replace('-','_'), None)]
        if missing:
            p.error(f'缺少参数: {", ".join(missing)}（或用 --config 一次性提供）')
    if args.config:
        args = load_config(args)
    elif args.footer_body_list:
        args.footer_body = '\n'.join(args.footer_body_list)
    build(args)
