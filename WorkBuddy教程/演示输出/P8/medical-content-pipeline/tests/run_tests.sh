#!/usr/bin/env bash
# run_tests.sh — medical-content-pipeline 测试运行器
# 仅使用 python3 标准库与 bash，不安装依赖、不联网、不调用外部账号。
# 只在本目录（课程文件）内读写。用法：bash run_tests.sh
set -u
cd "$(dirname "$0")"
SCRIPT="../scripts/check_fnumbers.py"

echo "=== T1 正常教学（模拟签署事实卡 + 编号齐全的稿件）==="
python3 "$SCRIPT" --factcard factcards/signed_demo.csv --input inputs/normal_teaching.md
echo "T1 退出码：$?"

echo
echo "=== T2 缺事实卡（不提供 --factcard）==="
python3 "$SCRIPT" --input inputs/normal_teaching.md
echo "T2 退出码：$?"

echo
echo "=== T3 缺医生签署（未签署事实卡）==="
python3 "$SCRIPT" --factcard factcards/unsigned_demo.csv --input inputs/normal_teaching.md
echo "T3 退出码：$?"

echo
echo "=== T4 换主题（稿件引用事实卡中不存在的编号）==="
python3 "$SCRIPT" --factcard factcards/signed_demo.csv --input inputs/other_topic.md
echo "T4 退出码：$?"

echo
echo "=== T5 语义反例：不能保证根治（编号会通过，语义须人工判否）==="
python3 "$SCRIPT" --factcard factcards/signed_demo.csv --input inputs/unsourced_claim.md
echo "T5 退出码：$?（预期 0：脚本只查编号，检测不出未编号医学句）"

echo
echo "=== T6 不明签署状态：待确认签署（应判为未签署）==="
python3 "$SCRIPT" --factcard factcards/pending_sign_demo.csv --input inputs/normal_teaching.md
echo "T6 退出码：$?"
