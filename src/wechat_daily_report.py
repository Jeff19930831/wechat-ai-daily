"""微信图片日报报告生成 - 被 wechat_daily.sh 调用"""
import json, glob, os
from datetime import datetime

total_imgs = sum(
    len(glob.glob(os.path.join("D:/Wechat_File/Wechat_Image", "**", f"*.{e}"), recursive=True))
    for e in ("jpg", "png", "webp", "gif")
)
total_summs = 0
groups = {}
for f in sorted(glob.glob(os.path.join("D:/Wechat_File/Wechat_Image", "*", "_image_summary.json"))):
    name = os.path.basename(os.path.dirname(f))
    with open(f, "r", encoding="utf-8") as fp:
        c = len(json.load(fp))
    groups[name] = c
    total_summs += c

report = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "total_images": total_imgs,
    "total_summaries": total_summs,
    "groups": groups,
}
print("HERMES_REPORT=" + json.dumps(report, ensure_ascii=False))
