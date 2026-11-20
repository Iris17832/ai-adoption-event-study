#!/bin/bash
# run_full_sample.sh — 全量样本结果自动接力链
# 等待 GLM 打分完成后，依次重估：词典对比 → 行情补拉 → 事件研究 → 横截面 → 图表
set -u
BASE="/Users/a1234/WorkBuddy/2026-11-17-18-33-48/research-package"
LOG="$BASE/data/processed/full_sample_log.txt"
cd "$BASE/code"

echo "[chain] $(date '+%H:%M:%S') 等待打分完成..." >> "$LOG"
# 等待打分脚本输出完成标志（公司级聚合行，最多等4小时）
for i in $(seq 1 240); do
  if grep -q "公司级聚合" "$BASE/data/processed/llm_scoring_log.txt" 2>/dev/null; then
    break
  fi
  sleep 60
done
if ! grep -q "公司级聚合" "$BASE/data/processed/llm_scoring_log.txt" 2>/dev/null; then
  echo "[chain] $(date '+%H:%M:%S') ⚠ 等待超时，打分未完成，退出" >> "$LOG"
  exit 1
fi
echo "[chain] $(date '+%H:%M:%S') 打分完成，开始全量重估" >> "$LOG"

# 1) 词典基线（与全量 LLM 表对比）
python3 04_dict_baseline.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 词典对比完成" >> "$LOG"

# 2) 行情补拉（新进样本的公司，已存在的自动跳过）
python3 05_fetch_prices.py --codes-from sample >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 行情补拉完成" >> "$LOG"

# 3) 事件研究主分析（DeepSeek + 安慰剂）
python3 06_car_analysis.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') CAR主分析完成" >> "$LOG"

# 4) 横截面回归
python3 07_cross_section.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 横截面回归完成" >> "$LOG"

# 5) 图表重生成
python3 09_make_figures.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 图表重生成完成 ✅ 全链结束" >> "$LOG"
