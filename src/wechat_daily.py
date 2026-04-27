"""微信图片每日自动处理主控脚本
- Step 1: 导出新图片（wechat_image_export.py）
- Step 2: AI 摘要新图片（kimi_image_summary.py）
- 输出汇总报告供 Hermes 推送
"""
import os
import sys
import json
import glob
import time
import subprocess
from datetime import datetime

LOG_DIR = "D:/ClaudeCode/logs"
os.makedirs(LOG_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(LOG_DIR, f"{today}.log")


class Logger:
    def __init__(self, path):
        self.terminal = sys.stdout
        self.log = open(path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


sys.stdout = Logger(log_file)
sys.stderr = Logger(log_file)

print(f"\n{'='*60}")
print(f"微信图片每日处理 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")


def count_summaries():
    """统计已有摘要数"""
    total = 0
    new_today = 0
    for f in glob.glob("D:/Wechat_File/Wechat_Image/*/_image_summary.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        total += len(data)
    return total


def count_images():
    """统计图片总数"""
    return sum(
        len(glob.glob(f"D:/Wechat_File/Wechat_Image/**/*.{e}", recursive=True))
        for e in ("jpg", "png", "webp", "gif")
    )


def run_step(name, script):
    """运行一个处理步骤"""
    print(f"\n--- {name} ---")
    t0 = time.time()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, encoding="utf-8",
        timeout=3600, env=env, cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    elapsed = time.time() - t0
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"  !! {name} 失败 (exit code {result.returncode})")
        return False
    print(f"  完成 ({elapsed:.0f}s)")
    return True


def main():
    imgs_before = count_images()
    summs_before = count_summaries()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # Step 0: 触发图片下载
    run_step("触发图片下载", os.path.join(SCRIPT_DIR, "wechat_image_downloader.py"))

    # Step 1: 导出图片
    ok1 = run_step("导出图片", os.path.join(SCRIPT_DIR, "wechat_image_export.py"))

    # Step 2: AI 摘要
    ok2 = run_step("AI 图片摘要", os.path.join(SCRIPT_DIR, "kimi_image_summary.py"))

    # 汇总
    imgs_after = count_images()
    summs_after = count_summaries()
    new_imgs = imgs_after - imgs_before
    new_summs = summs_after - summs_before

    report = (
        f"\n{'='*60}\n"
        f"每日处理完成 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'='*60}\n"
        f"新增图片: {new_imgs} 张 (总计 {imgs_after})\n"
        f"新增摘要: {new_summs} 条 (总计 {summs_after})\n"
        f"导出状态: {'成功' if ok1 else '失败'}\n"
        f"摘要状态: {'成功' if ok2 else '失败'}\n"
    )
    print(report)

    # 输出 Hermes 可读取的报告（最后一行 JSON）
    hermes_report = {
        "date": today,
        "new_images": new_imgs,
        "total_images": imgs_after,
        "new_summaries": new_summs,
        "total_summaries": summs_after,
        "export_ok": ok1,
        "summary_ok": ok2,
    }
    report_file = os.path.join(LOG_DIR, f"{today}_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(hermes_report, f, ensure_ascii=False, indent=2)

    print(f"\nHERMES_REPORT: {json.dumps(hermes_report, ensure_ascii=False)}")
    return hermes_report


if __name__ == "__main__":
    main()
