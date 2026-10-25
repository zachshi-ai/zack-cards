#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扎克卡片（field-note-layout）：1 封面 + 6 内容 + 1 封底 = 8 页"""
import os, subprocess, sys

SKILL = "../engine/field-note/generator.py"
OUT = "../out/field-note"
IMG = os.environ.get("CARD_IMG_DIR", "./img")
COVER_BG = f"{IMG}/fn-cover-bg.png"
HERO = f"{IMG}/fn-hero-longoutput.png"
TOTAL = 8
THEME = "长输出"

PAGES = [
    # (num, type, theme_keyword, content_blocks, hero)
    (1, "cover", "", [
        '<div class="cat">KNOWLEDGE / FIELD NOTES</div>',
        '<h1 class="title">一百万个 token</h1>',
        '<p class="sub">长输出这件事，正在改写我的工作方式</p>',
    ], COVER_BG),
    (2, "content", "量级", [
        '<div class="st">先说清楚有多长</div>',
        '<p class="prose">一百万 token，大约七十多万英文单词，中文能装下五十万字上下。过去的模型一次最多吐六万多，写长一点的东西，中途得切开、分几次接上，还要自己当那个把碎片粘回去的人。</p>',
        '<p class="prose">现在它一口气能吐完。这听着像参数游戏，但用起来差别很直接：整份合同、一整个项目、一本书的目录，你可以一次递过去。</p>',
    ], None),
    (3, "content", "风险", [
        '<div class="st">一次跑完，省事也放大代价</div>',
        '{HERO}',
        '<p class="prose">长任务没有检查点。它跑四十分钟，在九成的地方偏了，你损失的是整段时间，还有整笔钱。</p>',
        '<p class="prose">所以我现在不让它一上来就许大愿：先在小件上把方向跑对，再放它去干长活。</p>',
    ], HERO),
    (4, "content", "成本", [
        '<div class="st">账要重算一遍</div>',
        '<p class="prose">介绍期每百万输入两美元、输出十美元，十一月底之后翻到四和二十。输出单价一直是输入的五倍，而它现在偏偏最能吐。</p>',
        '<p class="prose">这意味着成本的大头，从「你喂了多少」挪到了「它吐了多少」。我的选型表里因此多加了一列：单次输出上限。</p>',
        '<div class="list-item">同样的活，吐得越长，单次越贵，但也越省往返</div>',
        '<div class="list-item">中途偏掉的代价，跟着输出长度一起变大</div>',
    ], None),
    (5, "content", "强项", [
        '<div class="st">它真正的强项，是长流程的活</div>',
        '<p class="prose">官方基准里，软件工程那项拿到七十七点九，综合智力指数五十出头。换一套聚合口径，排名又能反过来。</p>',
        '<p class="prose">两边的权重都不透明，所以我现在只看一件事：它能不能一口气把一段长流程干完，中间不用我接手。</p>',
    ], None),
    (6, "content", "类比", [
        '<div class="st">把它想成一个不休假的实习生</div>',
        '<div class="analogy-box">他很能熬，能连轴转四十小时，不用交接、不用讲背景。麻烦的是，他走偏了也不会主动问你——只会一路走到底，还很有信心。</div>',
        '<p class="prose">所以我的做法是给他定检查点：结构对不对、关键段像不像、收尾有没有跑偏。三个点看一眼，比他跑完再返工便宜得多。</p>',
    ], None),
    (7, "content", "用法", [
        '<div class="st">我现在怎么用它</div>',
        '<div class="list-item">长文档、长重构，一次给全材料，别切碎</div>',
        '<div class="list-item">交付前设三个检查点，卡住就停，别让它硬跑</div>',
        '<div class="list-item">短活用便宜的小模型，长活才放它上</div>',
        '<p class="prose">能力越强，越考验你会不会提问。这句话在长输出时代更明显：你省下的每一次往返，都要靠一开始那句需求换回来。</p>',
    ], None),
    (8, "back", "", [
        '<p class="prose">工具变强的时候，真正稀缺的是把话说清楚的能力。</p>',
    ], None),
]

def run(num, typ, theme, blocks, hero):
    content = "|".join(blocks)
    html = f"{OUT}/p{num:02d}.html"
    png = f"{OUT}/p{num:02d}.png"
    cmd = [sys.executable, SKILL, "--type", typ, "--num", str(num), "--total", str(TOTAL),
           "--content", content, "--output", html, "--screenshot", png]
    if theme:
        cmd += ["--theme", theme]
    if typ == "cover" and hero:
        cmd += ["--cover-bg", hero]
    if typ == "content" and hero:
        cmd += ["--hero", hero]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = os.path.exists(png) and os.path.getsize(png) > 20000
    print(f"p{num:02d} {'OK' if ok else 'FAIL'} {r.stdout.strip()[-80:]} {r.stderr.strip()[-120:]}")
    return ok

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ok = all([run(*p) for p in PAGES])
    print("ALL OK" if ok else "SOME FAILED")
