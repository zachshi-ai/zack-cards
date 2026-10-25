#!/bin/bash
# 用 MiniMax image-01 生成扎克卡片配图（无水印）
set -u
OUT=/root/AIdesign/cards-20261018/img6
mkdir -p "$OUT"
STYLE="高端杂志配图风格，深蓝墨色背景但层次分明、明暗有致，主体清晰明亮并占据画面中央主体区域，青色与琥珀色光效，细节丰富，画面四边都有内容不留纯黑边框，极简高级，无任何文字、无水印、无logo"

gen() {
  local name="$1"; local desc="$2"; local w="$3"; local h="$4"
  for i in 1 2 3; do
    if mmx image generate --prompt "$desc，$STYLE" --width "$w" --height "$h" --out "$OUT/$name.png" >/dev/null 2>&1 && [ -s "$OUT/$name.png" ]; then
      echo "OK   $name"
      return 0
    fi
    sleep 8
  done
  echo "FAIL $name"
}

gen cover "夜色中一条青色与琥珀色的光带在画面下方缓缓流动，上方大片留白，像一本正在被书写的手记" 1248 1872
gen p02 "一条极长的细光带横贯深空，被切成许多段又拼接回去，暗示超长文本与拼接" 1536 1536
gen p03 "一条笔直的长路伸向远方，路尽头有一处微弱的红点警示，两侧全黑，暗示一次跑到底的风险" 1536 1536
gen p04 "悬在黑暗中的精密刻度尺与天平结构，刻度上是青色的光点，暗示重新计价与成本核算" 1536 1536
gen p05 "一段连续不断的长流水线轨迹穿过画面，沿途有若干发光节点依次亮起，暗示长流程任务" 1536 1536
gen p06 "无人值守的机器在深夜持续运转，只有微光勾勒出轮廓，椅子空着，暗示不会主动叫停的执行者" 1536 1536
gen p07 "一条路径上有三个清晰发光的检查点，每个检查点像一扇微开的门，暗示把长任务切成可验收的段落" 1536 1536
echo ALL_IMAGE_DONE
