#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""观猹卡片（guancha-card）：与扎克卡片同一话题（Gemini 4 Argon 的长输出）"""
import json, os, subprocess, sys

SKILL = "../engine/guancha/generator.py"
OUT = "../out/guancha"
IMG = "./img"

cfg = {
    "hero": f"{IMG}/cover_sq.png",
    "sections": [
        f"{IMG}/p02.png",
        f"{IMG}/p04.png",
        f"{IMG}/p05.png",
        f"{IMG}/p06.png",
    ],
    "title": "一百万个 token",
    "subtitle": "长输出正在改写我的工作方式",
    "content": [
        {"num": "01", "label": "SCALE", "img_idx": 0, "paragraphs": [
            ["以前一次只能吐六万多 token，", "写长东西得切开", "、分几次接上。"],
            ["现在它一口气吐到一百万，中文五十万字上下。整份合同、整个项目，", "一次递过去", "就行。"],
            ["", "省掉的不是时间，是你当搬运工的次数。", ""],
        ]},
        {"num": "02", "label": "PRICE", "img_idx": 1, "paragraphs": [
            ["介绍期每百万输入两美元、输出十美元，", "十一月底翻到四和二十", "。"],
            ["输出单价一直是输入的五倍，而它现在偏偏最能吐。", "成本大头从「你喂了多少」挪到了「它吐了多少」。", ""],
            ["所以我的选型表里多了一列：", "单次输出上限。", ""],
        ]},
        {"num": "03", "label": "WORK", "img_idx": 2, "paragraphs": [
            ["长任务没有检查点。它跑四十分钟，在九成的地方偏了，", "你损失的是整段时间和整笔钱。", ""],
            ["所以我不让它一上来就许大愿：", "先在小件上把方向跑对", "，再放它去干长活。"],
            ["", "工具越强，越考验你会不会提问。", ""],
        ]},
        {"num": "04", "label": "USAGE", "img_idx": 3, "paragraphs": [
            ["长文档、长重构，一次给全材料，别切碎。", "", ""],
            ["交付前设三个检查点：结构、关键段、收尾。", "卡住就停", "，别让它硬跑到底。"],
            ["短活用便宜的小模型，", "长活才放它上", "。"],
        ]},
    ],
    "footer_title": "长输出的正确用法",
    "footer_body": ["省下的每一次往返，都要靠一开始那句需求换回来。"],
    "date": "2026.10.18",
    "day": "Sunday",
    "gap": 80,
    "output": f"{OUT}/guancha-20261018-v4.png",
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cfg_path = f"{OUT}/config.json"
    json.dump(cfg, open(cfg_path, "w"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, SKILL, "--config", cfg_path], capture_output=True, text=True)
    print(r.stdout.strip()[-300:])
    print(r.stderr.strip()[-800:])
