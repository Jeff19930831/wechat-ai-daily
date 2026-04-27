"""导出微信群聊图片 - 支持 V2 AES+XOR 加密格式，按 群名/年_月/ 组织"""

import os
import sys
import json
import hashlib
import re
import struct
import subprocess
from Crypto.Cipher import AES
from Crypto.Util import Padding

# ---------- 配置 ----------
WECHAT_BASE = "D:/Wechat_File/xwechat_files/jiangfeng667593_e026"
ATTACH_DIR = os.path.join(WECHAT_BASE, "msg/attach")
OUTPUT_DIR = "D:/Wechat_File/Wechat_Image"

# V2 加密密钥 (从微信进程内存提取)
V2_AES_KEY = b"5410f6d49b9e6eda"
V2_XOR_KEY = 0x5c
V2_MAGIC = b'\x07\x08V2\x08\x07'
V1_MAGIC = b'\x07\x08V1\x08\x07'
V1_FIXED_KEY = b"cfcd208495d565ef"
# --------------------------


def get_all_groups():
    """通过 wechat-cli sessions 获取所有群聊"""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        ["wechat-cli", "sessions", "--limit", "500", "--format", "json"],
        capture_output=True, text=True, env=env, encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Error running wechat-cli sessions: {result.stderr}")
        return []

    data = json.loads(result.stdout)
    groups = []
    for s in data:
        if s.get("is_group"):
            name = s["chat"].strip()
            username = s["username"]
            groups.append((name, username))
    return groups


def find_attach_hash(username):
    """用 username 的 MD5 定位 attach 子目录"""
    h = hashlib.md5(username.encode()).hexdigest()
    candidate = os.path.join(ATTACH_DIR, h)
    if os.path.isdir(candidate):
        return h
    return None


def sanitize_folder_name(name):
    """清理文件夹名中的非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def detect_image_format(header):
    """检测图片格式"""
    if header[:3] == b'\xff\xd8\xff':
        return "jpg"
    if header[:4] == bytes([0x89, 0x50, 0x4e, 0x47]):
        return "png"
    if header[:4] == b'RIFF':
        return "webp"
    if header[:4] == b'wxgf':
        return "hevc"
    if header[:3] == b'GIF':
        return "gif"
    return None


def decrypt_v2(data, aes_key, xor_key):
    """解密 V2 格式: AES-ECB + raw + XOR"""
    sig = data[:6]
    aes_size, xor_size = struct.unpack_from('<II', data, 6)
    offset = 15

    aligned = aes_size
    aligned -= ~(~aligned % 16)

    if offset + aligned > len(data):
        return None

    aes_data = data[offset:offset + aligned]
    cipher = AES.new(aes_key[:16], AES.MODE_ECB)
    dec_aes = Padding.unpad(cipher.decrypt(aes_data), AES.block_size)
    offset += aligned

    raw_end = len(data) - xor_size
    raw_data = data[offset:raw_end] if offset < raw_end else b''
    offset = raw_end

    xor_data = data[offset:]
    dec_xor = bytes(b ^ xor_key for b in xor_data) if xor_data else b''

    return dec_aes + raw_data + dec_xor


def extract_image(dat_path):
    """从 .dat 文件中解密图片数据"""
    with open(dat_path, "rb") as f:
        data = f.read()

    if len(data) < 6:
        return None, None

    header6 = data[:6]

    # V2 格式: AES-ECB + XOR
    if header6 == V2_MAGIC:
        try:
            result = decrypt_v2(data, V2_AES_KEY, V2_XOR_KEY)
            if result:
                fmt = detect_image_format(result[:16])
                if fmt:
                    return result, fmt
        except Exception:
            pass
        return None, None

    # V1 格式: 固定 key
    if header6 == V1_MAGIC:
        try:
            result = decrypt_v2(data, V1_FIXED_KEY, V2_XOR_KEY)
            if result:
                fmt = detect_image_format(result[:16])
                if fmt:
                    return result, fmt
        except Exception:
            pass
        return None, None

    # 旧 XOR 格式: 尝试自动检测 key
    for fmt_name, magic in [('jpg', [0xFF, 0xD8, 0xFF]), ('png', [0x89, 0x50, 0x4E, 0x47]),
                            ('gif', [0x47, 0x49, 0x46, 0x38])]:
        key = data[0] ^ magic[0]
        match = all((data[i] ^ key) == magic[i] for i in range(1, len(magic)) if i < len(data))
        if match:
            return bytes(b ^ key for b in data), fmt_name

    return None, None


def export_group_images(group_name, username):
    """导出一个群聊的所有图片"""
    attach_hash = find_attach_hash(username)
    if not attach_hash:
        return 0, 0, 0

    group_dir = os.path.join(ATTACH_DIR, attach_hash)
    safe_name = sanitize_folder_name(group_name)
    exported = 0
    skipped = 0
    failed = 0

    # 遍历所有年月目录
    if not os.path.isdir(group_dir):
        return 0, 0, 0

    for month_folder in sorted(os.listdir(group_dir)):
        month_path = os.path.join(group_dir, month_folder)
        if not os.path.isdir(month_path):
            continue

        img_dir = os.path.join(month_path, "Img")
        if not os.path.isdir(img_dir):
            continue

        # 跳过缩略图和 _h.dat，只导出原图
        dat_files = [
            f for f in os.listdir(img_dir)
            if f.endswith(".dat") and not f.endswith("_t.dat") and not f.endswith("_h.dat")
        ]

        if not dat_files:
            continue

        # 输出目录: 群名/年_月/
        out_subdir = os.path.join(OUTPUT_DIR, safe_name, month_folder.replace("-", "_"))
        os.makedirs(out_subdir, exist_ok=True)

        for fname in sorted(dat_files):
            dat_path = os.path.join(img_dir, fname)
            img_data, ext = extract_image(dat_path)

            if img_data:
                out_name = fname.replace(".dat", f".{ext}")
                out_path = os.path.join(out_subdir, out_name)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                exported += 1
            else:
                failed += 1

    return exported, skipped, failed


TARGET_GROUPS = [
    "【VIP】建龙北京",
    "中国矿产市场报告联系人群",
    "建龙集团市场分析交流群",
    "Mysteel-铁矿石矿工群（正式）",
    "Mysteel铁矿石资讯SVIP正式2群",
]


def main():
    print("正在获取群聊列表...")
    groups = get_all_groups()
    print(f"共找到 {len(groups)} 个群聊")

    target_set = set(TARGET_GROUPS)
    filtered = [(n, u) for n, u in groups if n in target_set]
    print(f"目标群聊: {len(filtered)}/{len(TARGET_GROUPS)} 匹配\n")

    if len(filtered) < len(TARGET_GROUPS):
        found_names = {n for n, _ in filtered}
        for t in TARGET_GROUPS:
            if t not in found_names:
                print(f"  未找到: {t}")

    total_exported = 0
    total_failed = 0

    for i, (name, username) in enumerate(filtered, 1):
        exported, skipped, failed = export_group_images(name, username)
        total_exported += exported
        total_failed += failed
        print(f"[{i}/{len(filtered)}] {name}: {exported} 张导出" +
              (f", {failed} 张失败" if failed else ""))

    print(f"\n{'='*50}")
    print(f"完成！成功导出: {total_exported} 张, 失败: {total_failed} 张")
    print(f"输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
