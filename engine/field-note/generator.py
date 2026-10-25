#!/usr/bin/env python3
"""
Field Note Layout Generator
自媒体长文多页卡片（Field Note 风格排版）生成器

用法:
  python3 generator.py --type cover --num 1 --total 13 --output /tmp/page.html
  python3 generator.py --type content --num 5 --total 13 --theme "AI工厂·范式转移" --content "..." --hero "/path/img.png" --output /tmp/page.html
  python3 generator.py --type back --num 13 --total 13 --content "..." --output /tmp/page.html
"""

import argparse
import datetime
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

# ============ 固定配置 ============
AUTHOR = "扎克的自留地"
TOTAL = 11  # 默认总页数
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def _resolve_chrome(explicit=None):
    """按 显式参数 → CHROME_BIN 环境变量 → 各平台常见路径 顺序找一个可用的 Chrome/Chromium"""
    if explicit:
        return explicit
    env = os.environ.get("CHROME_BIN")
    if env and os.path.exists(env):
        return env
    candidates = [
        CHROME,
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/local/bin/chromium",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Playwright 缓存中的 chromium
    import glob
    for pat in ("/root/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell",
                os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell"),
                "/root/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
                os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return CHROME

CHROME = _resolve_chrome()
HERO_COVER_MAX_H = 220   # 普通宽图固定高度（防止撑爆页面）
HERO_CONTAIN_MAX_H = 240 # 长截图完整显示的最大高度（超出按 contain 缩放）

# ============ Layout Schema ============

LAYOUT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&family=Cormorant+Garamond:ital,wght@0,300;1,300&display=swap');

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
.corner {
  position: absolute;
  font-family: 'Noto Serif SC', serif;
  font-size: 9px;
  z-index: 20;
  line-height: 1.5;
  letter-spacing: 2px;
  white-space: nowrap;  /* 四角禁止自动换行；仅允许 <br> 显式分行 */
}
.corner-tl { top: 28px; left: 28px; color: rgba(255,255,255,0.55); }
.corner-tr { top: 28px; right: 28px; color: rgba(255,200,140,0.7); text-align: right; text-shadow: 0 0 6px rgba(255,180,80,0.45); }
.corner-bl { bottom: 60px; left: 28px; color: rgba(255,255,255,0.45); text-shadow: 0 0 6px rgba(88,166,255,0.4); }
.corner-br { bottom: 60px; right: 28px; color: rgba(255,200,140,0.7); text-align: right; text-shadow: 0 0 6px rgba(255,180,80,0.45); }
.layer {
  position: relative;
  z-index: 1;
  height: 960px;
  display: flex;
  flex-direction: column;
  padding-top: 52px;
  background: #0d1117;
}
.layer::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(ellipse 70% 60% at 85% 15%, rgba(255, 180, 88, 0.22) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 15% 85%, rgba(88, 166, 255, 0.18) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
.main {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;      /* 所有页面统一垂直居中（生成器按页型注入 MAIN_STYLE） */
  align-items: flex-start;
  padding: 0 44px 44px;
}
/* ===== 封面专用三块（v2.3.0 起） ——
   category 标签 → .cat（Cormorant Garamond italic uppercase）
   大标题       → .title（Noto Serif SC 700 大字）
   副标题       → .sub（Noto Serif SC 300 中字）
   封面 main 必须按这个顺序含这三块，禁止用其他 class 或手写 inline style */
.cat   { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 17px; letter-spacing: 7px; text-transform: uppercase; color: #ffb450; margin-bottom: 28px; }
.title { font-family: 'Noto Serif SC', serif; font-weight: 700; font-size: 46px; line-height: 1.4; letter-spacing: 2px; color: #ffffff; margin: 0 0 26px 0; }
.sub   { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 22px; line-height: 1.75; letter-spacing: 1px; color: #e6edf3; margin: 0; }

.st { font-family: 'Noto Serif SC', serif; font-weight: 700; font-size: 30px; letter-spacing: 1px; color: #ffffff; margin-bottom: 14px; }
.prose { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.85; color: #d6dde6; margin-bottom: 14px; }
.prose .em { color: #ffffff; font-weight: 700; }
.pullquote { border-left: 3px rgba(255,180,80,0.4); background: rgba(255,180,80,0.06); padding: 12px 16px; margin: 10px 0; }
.pullquote-text { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.75; color: #f0f4f8; }

.analogy-box { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 12px 16px; margin: 10px 0; }
.analogy-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }

.research-box { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07); border-radius: 6px; padding: 14px 16px; margin: 10px 0; }
.research-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }

.engineer-box { background: rgba(88,166,255,0.05); border: 1px solid rgba(88,166,255,0.15); border-radius: 6px; padding: 13px 16px; margin: 10px 0; }
.engineer-box p { font-family: 'Noto Serif SC', serif; font-weight: 400; font-size: 18px; line-height: 1.8; color: #f0f4f8; }

/* ===== 配图组件 =====
   规则（写死，禁止手写 img 标签改版式）：
   - 宽图/方图（宽:高 >= 1.1）→ .hero-cover：固定高度 110px，object-fit cover 裁剪填充
   - 长图/截图（宽:高 <  1.1）→ .hero-contain：宽度 100%，高度自适应，max-height 240px，
     object-fit contain 完整显示，绝不裁剪
   由 generator.py --hero 自动判定，模型只传图片路径/URL。
   注意：main 是 flex 容器，figure 必须显式 width:100%（否则宽度被内容反推）。
*/
.hero-wrap { width: 100%; margin: 0; }
.hero-img {
  width: 100%;
  display: block;
  border-radius: 4px;
  margin-bottom: 12px;
  background: rgba(255,255,255,0.04);
}
.hero-cover { height: 110px; object-fit: cover; }
.hero-contain { height: auto; max-height: 300px; width: auto; max-width: 100%; margin: 0 auto 12px; object-fit: contain; }
/* 注：v2.4.0 起移除 .img-caption 与 figcaption —— 正文页配图禁止加图注 */

/* 封底落款（唯一作者出现处，写死） */
.sign-off {
  margin-top: 36px;
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  font-size: 11px;
  color: rgba(255,255,255,0.32);
  letter-spacing: 3px;
  text-align: center;
}

/* 脚注/来源类元素一律隐藏：全文禁止链接、禁止提信源 */
cite { display: none; }

"""


def fmt_page_num(n):
    """页码格式化为两位数字"""
    return f"{n:02d}"


def generate_corners(page_type, page_num, total, theme_keyword="", author=AUTHOR):
    today = datetime.date.today()
    date_str = today.strftime("%Y.%m.%d")
    day_str = today.strftime("%A")

    # 页码一律两位：01 / 02 / 10 / 11 / 13（总数也两位，右下角统一 → 03/11 样式）
    pn = fmt_page_num(page_num)
    total_pn = fmt_page_num(total)
    next_pn = fmt_page_num(page_num + 1) if page_num < total else ""

    if page_type == "cover":
        top_left = "Field Notes"
        top_right = pn
        bottom_left = f"{author}<br>{date_str} / {day_str}"
        bottom_right = f"→ {next_pn}/{total_pn}" if page_num < total else ""

    elif page_type == "content":
        top_left = theme_keyword
        top_right = pn
        bottom_left = f"{author}<br>{date_str}"
        bottom_right = f"→ {next_pn}/{total_pn}"

    elif page_type == "back":
        top_left = "Field Notes"
        top_right = pn
        bottom_left = f"{date_str} / {day_str}"
        bottom_right = ""

    return {
        "top_left": top_left,
        "top_right": top_right,
        "bottom_left": bottom_left,
        "bottom_right": bottom_right,
    }


# ============ 图片工具 ============

def fetch_image(src):
    """把图片 URL 下载到本地临时文件；本地路径原样返回。返回本地路径或 None。"""
    if not src:
        return None
    if src.startswith(("http://", "https://")):
        try:
            ext = os.path.splitext(urllib.parse.urlparse(src).path)[1] or ".jpg"
            fd, path = tempfile.mkstemp(suffix=ext)
            os.close(fd)
            urllib.request.urlretrieve(src, path)
            return path
        except Exception as e:
            print(f"WARN: 图片下载失败 {src}: {e}", file=sys.stderr)
            return None
    if os.path.exists(src):
        return src
    print(f"WARN: 图片文件不存在 {src}", file=sys.stderr)
    return None


def image_size(path):
    """读取图片宽高。优先 PIL，回退 macOS sips。返回 (w, h) 或 None。"""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except ImportError:
        pass
    try:
        out = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
            capture_output=True, text=True, timeout=15,
        )
        w = h = None
        for line in out.stdout.splitlines():
            line = line.strip()
            if line.startswith("pixelWidth:"):
                w = int(line.split(":")[1].strip())
            elif line.startswith("pixelHeight:"):
                h = int(line.split(":")[1].strip())
        if w and h:
            return (w, h)
    except Exception:
        pass
    return None


def hero_block(image_src):
    """根据图片宽高比自动选版式，生成 <img> 块（禁止手写 img 标签改版式）。
    v2.4.0 起：不再支持 caption 参数，配图下禁止加图注。"""
    if not image_src:
        return ""
    path = fetch_image(image_src)
    if not path:
        return ""
    cls = "hero-cover"
    size = image_size(path)
    if size:
        w, h = size
        if h > 0 and w / h < 1.1:
            cls = "hero-contain"  # 长图/截图：完整显示，不裁剪
        print(f"hero: {path} {w}x{h} -> {cls}")
    else:
        print(f"WARN: 无法读取图片尺寸 {image_src}，按宽图处理", file=sys.stderr)
    return f'<figure class="hero-wrap"><img class="hero-img {cls}" src="{html_escape_path(image_src)}" alt=""></figure>'


def html_escape_path(src):
    """HTML 属性安全：本地路径转 file:// 且转义，URL 转义引号。"""
    if src.startswith(("http://", "https://")):
        return src.replace("&", "&amp;").replace('"', "&quot;")
    return "file://" + urllib.parse.quote(os.path.abspath(src))


def cover_bg_style(cover_bg_url):
    """封面底图：支持生图输出的本地文件路径或 http URL。返回 layer 背景样式。"""
    if not cover_bg_url:
        return "background:#0d1117;"
    path = fetch_image(cover_bg_url)
    src = html_escape_path(path) if path else cover_bg_url.replace("&", "&amp;").replace('"', "&quot;")
    return (
        f"background-color:#0d1117;"
        f"background-image:linear-gradient(rgba(13,17,23,0.5), rgba(13,17,23,0.7)), url('{src}');"
        f"background-size:100% 100%, cover;"
        f"background-position:center, center;"
        f"background-repeat:no-repeat, no-repeat;"
    )


def make_page(page_type, page_num, total, content_blocks, theme_keyword="", cover_bg_url="",
              hero_image="", output_path=None):
    """
    生成单页HTML

    page_type: "cover" | "content" | "back"
    page_num: 当前页码（1起始）
    total: 总页数
    content_blocks: 主内容区HTML字符串（可含 {HERO} 占位符，hero 图插到该位置）
    theme_keyword: 内容页左上角主题词（精炼，禁换行）
    cover_bg_url: 封面底图（生图产出的本地文件路径或URL，封面专用）
    hero_image: 正文页配图（本地路径或URL），宽高比自动决定 cover/contain 版式
    output_path: 输出文件路径
    """
    corners = generate_corners(page_type, page_num, total, theme_keyword)

    # 封面：居中 + 底图（生图）；内容/封底：垂直居中
    if page_type == "cover":
        LAYER_BG_BEFORE = cover_bg_style(cover_bg_url)
        MAIN_STYLE = "justify-content:center; align-items:flex-start; flex-direction:column; padding-top:0; text-shadow: 0 1px 12px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9);"
    elif page_type == "back":
        # 封底：水平居中 + 垂直居中，只允许一段结束语 + .sign-off 落款
        LAYER_BG_BEFORE = "background:#0d1117;"
        MAIN_STYLE = "justify-content:center; align-items:center; flex-direction:column; text-align:center; padding-top:0"
    else:  # content
        # 正文页：垂直居中 + 左对齐
        LAYER_BG_BEFORE = "background:#0d1117;"
        MAIN_STYLE = "justify-content:center; align-items:flex-start; flex-direction:column; padding-top:0"

    # hero 图：插到 {HERO} 占位符，无占位符则放最前
    hero = hero_block(hero_image)
    if hero:
        if "{HERO}" in content_blocks:
            content_blocks = content_blocks.replace("{HERO}", hero)
        else:
            content_blocks = hero + content_blocks

    # 封底：自动追加 .sign-off 落款（唯一作者出现处，模型禁止手写/重复）
    if page_type == "back" and "sign-off" not in content_blocks:
        content_blocks = content_blocks + f'<div class="sign-off">—— {AUTHOR} ——</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Field Note</title>
<style>
{LAYOUT_CSS}
</style>
</head>
<body>
<div class="layer" style="{LAYER_BG_BEFORE}">
  <div class="corner corner-tl">{corners['top_left']}</div>
  <div class="corner corner-tr">{corners['top_right']}</div>
  <div class="corner corner-bl">{corners['bottom_left']}</div>
  <div class="corner corner-br">{corners['bottom_right']}</div>
  <div class="main" style="{MAIN_STYLE};">
    {content_blocks}
  </div>
</div>
</body>
</html>"""

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"Generated: {output_path}")

    return html


def screenshot(page_path, output_png, chrome=CHROME):
    """截图（自动清理Chrome残留进程 + 等待网络资源加载）"""
    os.system("pkill -f 'Chrome.*headless' 2>/dev/null")
    import time
    time.sleep(2)  # 杀进程后等 2s

    # 本机 Chrome 需要 swiftshader/no-sandbox 才能 headless 截图（GPU 进程会崩）
    cmd = (f'"{chrome}" --headless --disable-gpu '
           f'--no-sandbox --disable-dev-shm-usage --no-zygote --hide-scrollbars '
           f'--screenshot="{output_png}" --window-size=540,960 '
           f'--force-device-scale-factor=3 --virtual-time-budget=5000 "file://{page_path}"')
    ret = os.system(cmd + " >/dev/null 2>&1")
    if ret != 0:
        print(f"Screenshot failed with code {ret}", file=sys.stderr)
    else:
        print(f"Screenshot: {output_png}")


def send_back(image_path, message, channel="", account="", target=""):
    """发回需求来源渠道（微信/飞书/其他，channel/account/target 从来源会话获取，禁止写死）"""
    if not channel or not target:
        print(f"WARN: 缺少回传信息（channel={channel!r} target={target!r}），跳过发送。"
              f"请从来源会话获取渠道/账号/目标后再发。", file=sys.stderr)
        return
    cmd = (f'openclaw message send '
           f'--channel "{channel}" '
           f'--media "{image_path}" '
           f'--message "{message}"')
    if account:
        cmd += f' --account "{account}"'
    cmd += f' --target "{target}"'
    ret = os.system(cmd)
    if ret != 0:
        print(f"Send failed with code {ret}", file=sys.stderr)
    else:
        print(f"Sent to {channel}: {message}")


# ============ CLI ============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Field Note Layout Generator")
    parser.add_argument("--type", choices=["cover", "content", "back"], required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--total", type=int, default=TOTAL)
    parser.add_argument("--theme", default="")
    parser.add_argument("--content", default="", help="Content blocks HTML (use | for newlines)")
    parser.add_argument("--cover-bg", default="", help="封面底图：生图产出的本地文件路径或URL（禁止 Unsplash 示例图）")
    parser.add_argument("--hero", default="", help="正文页配图（本地路径或URL），自动判定版式")
    parser.add_argument("--output", default="/tmp/field_note.html")
    parser.add_argument("--screenshot", default="", help="Output PNG path (optional)")
    parser.add_argument("--send", default="", help="发送标题/消息（配合 --channel/--account/--target）")
    parser.add_argument("--channel", default="", help="回传渠道：openclaw-weixin / feishu / ...（= 需求来源渠道）")
    parser.add_argument("--account", default="", help="渠道账号 id（来源会话的账号）")
    parser.add_argument("--target", default="", help="回传目标（来源会话的 peer / chat id）")

    args = parser.parse_args()

    content = args.content.replace("|", "\n")

    make_page(
        page_type=args.type,
        page_num=args.num,
        total=args.total,
        content_blocks=content,
        theme_keyword=args.theme,
        cover_bg_url=args.cover_bg,
        hero_image=args.hero,
        output_path=args.output
    )

    if args.screenshot:
        screenshot(args.output, args.screenshot)

    if args.send:
        send_back(args.screenshot or args.output, args.send, args.channel, args.account, args.target)
