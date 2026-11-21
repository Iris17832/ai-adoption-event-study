#!/bin/bash
# run_final_chain.sh — 等待 GLM 全量打分完成后，自动重跑"最终样本"全链路
# 与旧 run_full_sample.sh 的区别：监控独立日志 llm_scoring_resume_log.txt，避免误触发
set -u
BASE="/Users/a1234/WorkBuddy/2026-11-17-18-33-48/research-package"
CODE="$BASE/code"
LOG="$BASE/results/final_chain_log.txt"
SCORE_LOG="$BASE/data/processed/llm_scoring_resume_log.txt"
cd "$CODE"

echo "[chain] $(date '+%H:%M:%S') 等待全量打分完成..." > "$LOG"
# 等待 04 脚本输出"公司级聚合"完成标志（最多 3 小时）
OK=0
for i in $(seq 1 180); do
  if grep -q "公司级聚合" "$SCORE_LOG" 2>/dev/null; then OK=1; break; fi
  sleep 60
done
if [ "$OK" -ne 1 ]; then
  echo "[chain] $(date '+%H:%M:%S') ⚠ 等待超时，改用当前缓存继续" >> "$LOG"
fi
echo "[chain] $(date '+%H:%M:%S') 打分阶段结束，开始最终样本全链路" >> "$LOG"

# 1) 从缓存稳健重建段落级/公司级表（12 脚本处理旧格式缓存与 FAILED 容错，优于 04 自带聚合）
python3 12_aggregate_partial.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 缓存聚合完成" >> "$LOG"

# 2) 补拉新进样本行情（已存在的自动跳过）
python3 05_fetch_prices.py --codes-from sample >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 行情补拉完成" >> "$LOG"

# 3) 主分析 + 横截面 + 图表 + 稳健性 + 诊断
{ echo "=== 06 CAR ==="; python3 06_car_analysis.py; \
  echo "=== 07 横截面 ==="; python3 07_cross_section.py; \
  echo "=== 09 图表 ==="; python3 09_make_figures.py; \
  echo "=== 10 稳健性 ==="; python3 10_robustness.py; \
  echo "=== 13 诊断 ==="; python3 13_diagnostics.py; } >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') 主链路完成" >> "$LOG"

# 4) 生成可直接粘贴进论文的数字快照
python3 14_final_report.py >> "$LOG" 2>&1
echo "[chain] $(date '+%H:%M:%S') ✅ 全链结束，数字快照 -> results/final_numbers.md" >> "$LOG"
