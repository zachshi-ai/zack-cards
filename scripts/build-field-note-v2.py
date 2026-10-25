#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扎克卡片 v2：每页配 MiniMax 生成插图，1 封面 + 6 内容 + 1 封底 = 8 页"""
import os, subprocess, sys

SKILL = "../engine/field-note/generator.py"
OUT = "../out/field-note"
IMG = "./img"
TOTAL = 8

PAGES = [
    (1, "cover", "", [
        '<div class="cat">KNOWLEDGE / FIELD NOTES</div>',
        '<h1 class="title">一百万个 token</h1>',
        '<p class="sub">长输出这件事，正在改写我的工作方式</p>',
    ], f"{IMG}/cover.png"),
    (2, "content", "量级", [
        '<div class="st">先说清楚有多长</div>',
        '{HERO}',
        '<p class="prose">一百万 token，中文能装下五十万字上下。过去的模型一次最多吐六万多，写长东西得切开、分几次接上，自己当那个粘碎片的人。</p>',
        '<p class="prose">现在它一口气吐完。整份合同、整个项目，一次递过去。</p>',
    ], f"{IMG}/p02.png"),
    (3, "content", "风险", [
        '<div class="st">一次跑完，代价也被放大</div>',
        '{HERO}',
        '<p class="prose">长任务没有检查点。它跑四十分钟，在九成的地方偏了，你损失的是整段时间，还有整笔钱。</p>',
        '<p class="prose">所以我先在小件上把方向跑对，再放它去干长活。</p>',
    ], f"{IMG}/p03.png"),
    (4, "content", "成本", [
        '<div class="st">账要重算一遍</div>',
        '{HERO}',
        '<p class="prose">介绍期每百万输入两美元、输出十美元，十一月底翻到四和二十。输出单价一直是输入的五倍，而它现在偏偏最能吐。</p>',
        '<p class="prose">成本大头从「你喂了多少」挪到了「它吐了多少」。</p>',
    ], f"{IMG}/p04.png"),
    (5, "content", "强项", [
        '<div class="st">强项是长流程的活</div>',
        '{HERO}',
        '<p class="prose">官方基准里软件工程那项七十七点九，换个聚合口径排名又反过来。</p>',
        '<p class="prose">两边的权重都不透明，我现在只看一件事：它能不能一口气把一段长流程干完，中间不用我接手。</p>',
    ], f"{IMG}/p05.png"),
    (6, "content", "类比", [
        '<div class="st">把它想成不休假的实习生</div>',
        '{HERO}',
        '<div class="analogy-box">他很能熬，连轴转四十小时不用交接。麻烦的是走偏了也不会问你，只会一路走到底，还很有信心。</div>',
    ], f"{IMG}/p06.png"),
    (7, "content", "用法", [
        '<div class="st">我现在怎么用它</div>',
        '{HERO}',
        '<p class="prose">· 长文档、长重构，一次给全材料，别切碎</p>',
        '<p class="prose">· 交付前设三个检查点，卡住就停</p>',
        '<p class="prose">· 短活用便宜的小模型，长活才放它上</p>',
    ], f"{IMG}/p07.png"),
    (8, "back", "", [
        '<p class="prose">工具变强的时候，真正稀缺的是把话说清楚的能力。</p>',
    ], None),
]

STYLE = '<style>.hero-contain{width:100%!important;height:auto!important;max-height:none!important;max-width:100%!important;object-fit:cover!important;margin:0 0 16px!important;}.prose{color:#eef3f9!important;}.analogy-box p{color:#eef3f9!important;}.corner-bl,.corner-tl{color:rgba(255,255,255,0.90)!important;}.corner-br,.corner-tr{color:rgba(255,208,155,1)!important;}</style>'

def run(num, typ, theme, blocks, hero):
    content = "|".join([STYLE] + blocks)
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
    print(f"p{num:02d} {'OK' if ok else 'FAIL'} :: {r.stdout.strip()[-90:]} {r.stderr.strip()[-150:]}")
    return ok

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    res = [run(*p) for p in PAGES]
    print("ALL OK" if all(res) else "SOME FAILED")
