"""微信群聊图片自动下载 - PyAutoGUI 屏幕自动化

仅处理当天新消息中的图片，不滚动历史记录。
打开群聊后，点击当前可见的图片触发下载，然后移到下一个群。

防封号策略:
- 点击间隔随机 3~8 秒
- 鼠标移动带随机偏移
"""
import time
import random
import os
import sys
import hashlib
import win32gui
import win32con
import pyautogui
import pyperclip
from datetime import datetime

ATTACH_DIR = "D:/Wechat_File/xwechat_files/jiangfeng667593_e026/msg/attach"
TARGET_GROUPS = [
    ("【VIP】建龙北京", "35041202724@chatroom"),
    ("中国矿产市场报告联系人群", "39849185461@chatroom"),
    ("建龙集团市场分析交流群", "20025531116@chatroom"),
    ("Mysteel-铁矿石矿工群（正式）", "34987209659@chatroom"),
    ("Mysteel铁矿石资讯SVIP正式2群", "22679121706@chatroom"),
]

CLICK_DELAY_MIN = 3.0
CLICK_DELAY_MAX = 8.0
GROUP_GAP_MIN = 5.0
GROUP_GAP_MAX = 10.0

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def rand_delay(lo, hi):
    d = random.uniform(lo, hi)
    time.sleep(d)
    return d


def human_click(x, y):
    ox, oy = random.randint(-3, 3), random.randint(-3, 3)
    dur = random.uniform(0.15, 0.35)
    pyautogui.moveTo(x + ox, y + oy, duration=dur * 0.6)
    pyautogui.click()
    time.sleep(random.uniform(0.05, 0.15))


def count_today_missing(group_hash):
    """Count today's month dir files missing originals."""
    today = datetime.now().strftime("%Y-%m")
    gd = os.path.join(ATTACH_DIR, group_hash, today, "Img")
    if not os.path.isdir(gd):
        return 0, 0
    files = os.listdir(gd)
    origs = {f for f in files if f.endswith(".dat") and not f.endswith("_t.dat") and not f.endswith("_h.dat")}
    thumbs = {f.replace("_t.dat", ".dat") for f in files if f.endswith("_t.dat")}
    missing = thumbs - origs
    return len(origs), len(missing)


def scan_new_files(group_hash, known):
    """Check for new .dat originals across all months."""
    gd = os.path.join(ATTACH_DIR, group_hash)
    if not os.path.isdir(gd):
        return set()
    current = set()
    for root, dirs, files in os.walk(gd):
        for f in files:
            if f.endswith(".dat") and not f.endswith("_t.dat") and not f.endswith("_h.dat"):
                current.add(f)
    return current - known


def process_group(group_name, group_hash, wechat_rect):
    """Open group chat and click visible images to trigger downloads."""
    print(f"\n--- {group_name} ---")

    origs, missing = count_today_missing(group_hash)
    if missing == 0:
        print(f"  当月无缺失 ({origs} 张)")
        return 0

    print(f"  当月缺原图: {missing} 张")

    # Open chat via search
    pyautogui.hotkey("ctrl", "f")
    rand_delay(0.5, 1.0)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("backspace")
    time.sleep(0.2)
    pyperclip.copy(group_name)
    pyautogui.hotkey("ctrl", "v")
    rand_delay(1.5, 2.5)
    pyautogui.press("down")
    time.sleep(0.3)
    pyautogui.press("enter")
    rand_delay(1.0, 2.0)
    pyautogui.press("escape")
    rand_delay(1.5, 2.0)

    rect = wechat_rect
    chat_cx = (rect[0] + 310 + rect[2] - 15) // 2
    chat_top = rect[1] + 80
    chat_bottom = rect[3] - 200

    # Record known files before clicking
    known = set()
    for root, dirs, files in os.walk(os.path.join(ATTACH_DIR, group_hash)):
        for f in files:
            if f.endswith(".dat") and not f.endswith("_t.dat") and not f.endswith("_h.dat"):
                known.add(f)

    clicked = 0
    max_clicks = 20  # Only click a few times for recent messages

    for _ in range(4):  # 4 rounds of clicking
        for _ in range(random.randint(2, 5)):
            if clicked >= max_clicks:
                break
            x = random.randint(chat_cx - 120, chat_cx + 120)
            y = random.randint(chat_bottom - 300, chat_bottom)  # Focus on bottom (recent)
            human_click(x, y)
            rand_delay(0.5, 1.5)
            clicked += 1

        rand_delay(3, 5)

    # Final check
    time.sleep(2)
    new = scan_new_files(group_hash, known)
    if new:
        print(f"  新下载 {len(new)} 张")
    else:
        print(f"  点击 {clicked} 次, 未检测到新文件")
    return len(new)


def main():
    print(f"\n{'='*50}")
    print(f"微信图片自动下载 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标群: {len(TARGET_GROUPS)}")
    print(f"{'='*50}")

    hwnd = win32gui.FindWindow("Qt51514QWindowIcon", "微信")
    if not hwnd:
        print("微信窗口未找到，请先打开微信")
        sys.exit(1)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.3)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    rect = win32gui.GetWindowRect(hwnd)

    total_new = 0
    for name, uname in TARGET_GROUPS:
        gh = hashlib.md5(uname.encode()).hexdigest()
        new = process_group(name, gh, rect)
        total_new += new
        rand_delay(GROUP_GAP_MIN, GROUP_GAP_MAX)

    print(f"\n{'='*50}")
    print(f"完成: 新下载 {total_new} 张")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
