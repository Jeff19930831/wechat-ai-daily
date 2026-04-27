"""使用 Kimi kimi-2.6 多进程并行分析微信导出图片"""

import os
import json
import glob
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

KIMI_CLI = os.path.expanduser("~/.local/bin/kimi")
MODEL = "kimi-code/kimi-for-coding"
TEMP_DIR = "D:/ClaudeCode/kimi_temp"
OUTPUT_DIR = "D:/Wechat_File/Wechat_Image"
MAX_WORKERS = 8  # 并行 agent 数量


def analyze_image(task):
    """单个图片分析任务（每个进程独立）"""
    img_path, rel_path, worker_id = task
    tmp_path = os.path.join(TEMP_DIR, f"worker_{worker_id}.jpg")

    try:
        shutil.copy2(img_path, tmp_path)
    except Exception:
        return rel_path, None

    prompt = (
        "请用一句话简洁描述这张图片的主要内容（不超过50字），"
        "如果图片包含数据表格请说明是什么数据。"
        "只输出描述文字，不要其他内容。"
        f"图片路径: {tmp_path}"
    )

    try:
        result = subprocess.run(
            [KIMI_CLI, "-m", MODEL, "--quiet", "-p", prompt],
            capture_output=True, text=True, encoding="utf-8",
            timeout=120, env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        output = result.stdout.strip()
        if "To resume this session" in output:
            output = output.split("To resume this session")[0].strip()
        return rel_path, output if output else None
    except subprocess.TimeoutExpired:
        return rel_path, None
    except Exception:
        return rel_path, None


def process_group(group_dir, force=False):
    """处理一个群聊目录"""
    group_name = os.path.basename(group_dir)
    summary_file = os.path.join(group_dir, "_image_summary.json")

    existing = {}
    if os.path.exists(summary_file) and not force:
        with open(summary_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

    images = []
    for ext in ("*.jpg", "*.png", "*.webp", "*.gif"):
        images.extend(glob.glob(os.path.join(group_dir, "**", ext), recursive=True))

    todo = [(img, os.path.relpath(img, group_dir)) for img in sorted(images)
            if os.path.relpath(img, group_dir) not in existing]

    if not todo:
        print(f"  {group_name}: 全部已处理 ({len(images)} 张)")
        return

    print(f"  {group_name}: {len(todo)} 张待处理 / {len(images)} 张总计")

    # 构建任务列表，轮询分配 worker_id
    tasks = [(img, rel, i % MAX_WORKERS) for i, (img, rel) in enumerate(todo)]

    done = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(analyze_image, t): t[1] for t in tasks}
        for future in as_completed(futures):
            rel_path = futures[future]
            done += 1
            try:
                _, desc = future.result()
                if desc:
                    existing[rel_path] = desc
                    fname = os.path.basename(rel_path)
                    print(f"    [{done}/{len(todo)}] {fname}: {desc[:60]}")
                else:
                    print(f"    [{done}/{len(todo)}] {os.path.basename(rel_path)}: 失败")
            except Exception as e:
                print(f"    [{done}/{len(todo)}] {os.path.basename(rel_path)}: 异常 {e}")

            # 每 20 张保存一次
            if done % 20 == 0:
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"  已保存 ({len(existing)} 条): {summary_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for i in range(MAX_WORKERS):
        os.makedirs(os.path.join(TEMP_DIR), exist_ok=True)

    groups = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*")))
    groups = [g for g in groups if os.path.isdir(g)]

    print(f"并行 agent 数: {MAX_WORKERS}")
    print(f"找到 {len(groups)} 个群聊目录\n")

    for group_dir in groups:
        process_group(group_dir, force=args.force)

    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print("\n全部完成！")


if __name__ == "__main__":
    main()
