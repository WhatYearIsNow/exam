#!/usr/bin/env bash
# 真题分类汇编离线包——环境安装脚本（macOS / Linux）
# 把 vendor/ 里的 exam-zh 与补装字体装到 TeX Live 用户树（TEXMFHOME），
# 只补缺失组件，不动系统 TeX。Windows 用户请看 PDF/离线包说明。
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

command -v kpsewhich >/dev/null || { echo "错误：未找到 kpsewhich，请先安装 TeX Live（见 README.md）"; exit 1; }
TEX_TREE=$(kpsewhich -var-value=TEXMFHOME)
[ -n "$TEX_TREE" ] || { echo "错误：无法确定 TEXMFHOME"; exit 1; }
echo "TEXMFHOME = $TEX_TREE"

missing() { ! kpsewhich "$1" >/dev/null 2>&1; }

if missing exam-zh.cls; then
  mkdir -p "$TEX_TREE/tex/latex/exam-zh"
  cp vendor/exam-zh/* "$TEX_TREE/tex/latex/exam-zh/"
  echo "已安装 exam-zh"
else
  echo "exam-zh 已存在，跳过"
fi

if missing ulem.sty; then
  mkdir -p "$TEX_TREE/tex/latex/ulem"
  cp vendor/ulem/ulem.sty "$TEX_TREE/tex/latex/ulem/"
  echo "已安装 ulem"
else
  echo "ulem 已存在，跳过"
fi

if missing STIXTwoMath-Regular.otf; then
  mkdir -p "$TEX_TREE/fonts/opentype/stix2"
  cp vendor/STIXTwo/*.otf "$TEX_TREE/fonts/opentype/stix2/"
  echo "已安装 STIXTwo 字体"
else
  echo "STIXTwo 已存在，跳过"
fi

if missing Asana-Math.otf; then
  mkdir -p "$TEX_TREE/fonts/opentype/asana"
  cp vendor/Asana-Math/*.otf "$TEX_TREE/fonts/opentype/asana/"
  echo "已安装 Asana-Math 字体"
else
  echo "Asana-Math 已存在，跳过"
fi

command -v mktexlsr >/dev/null && mktexlsr "$TEX_TREE" || true
echo
echo "完成。试试生成概率论第一章样章："
echo "  python3 tools/make_book.py --subject probability --chapter 1 --build"
