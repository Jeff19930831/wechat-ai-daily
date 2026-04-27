#!/usr/bin/env python3
"""微信图片每日处理 - Hermes cron script"""
import subprocess
import os
import sys
from datetime import datetime

WIN_PYTHON = "/mnt/c/Users/lk/AppData/Local/Programs/Python/Python312/python.exe"
SCRIPTS_DIR = "/mnt/d/ClaudeCode/wechat-ai-daily/src"

print(f"=== 微信图片每日处理 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

# Step 1: 导出图片
print("\n--- Step 1: 导出图片 ---")
r1 = subprocess.run(
    [WIN_PYTHON, f"{SCRIPTS_DIR}/wechat_image_export.py"],
    capture_output=True, text=True, timeout=3600,
    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
)
print(r1.stdout)
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

# Step 2: AI 摘要
print("\n--- Step 2: AI 图片摘要 ---")
r2 = subprocess.run(
    [WIN_PYTHON, f"{SCRIPTS_DIR}/kimi_image_summary.py"],
    capture_output=True, text=True, timeout=3600,
    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
)
print(r2.stdout)
if r2.stderr:
    print(r2.stderr, file=sys.stderr)

# Step 3: 生成报告
print("\n--- 日报汇总 ---")
r3 = subprocess.run(
    [WIN_PYTHON, f"{SCRIPTS_DIR}/wechat_daily_report.py"],
    capture_output=True, text=True, timeout=60,
    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
)
print(r3.stdout)
if r3.stderr:
    print(r3.stderr, file=sys.stderr)

print(f"\n完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if r1.returncode != 0 or r2.returncode != 0:
    sys.exit(1)
