#!/bin/bash
# 微信图片每日处理 - WSL wrapper for Hermes cron
export PYTHONIOENCODING=utf-8

WIN_PYTHON="/mnt/c/Users/lk/AppData/Local/Programs/Python/Python312/python.exe"
D="/mnt/d/ClaudeCode"

echo "=== 微信图片每日处理 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# Step 1: 导出图片
echo ""
echo "--- Step 1: 导出图片 ---"
"$WIN_PYTHON" "$D/wechat_image_export.py" 2>&1

# Step 2: AI 摘要
echo ""
echo "--- Step 2: AI 图片摘要 ---"
"$WIN_PYTHON" "$D/kimi_image_summary.py" 2>&1

# Step 3: 生成报告
echo ""
echo "--- 日报汇总 ---"
"$WIN_PYTHON" "$D/wechat_daily_report.py" 2>&1

echo ""
echo "完成: $(date '+%Y-%m-%d %H:%M:%S')"
