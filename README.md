# WeChat AI Daily — 微信群聊图片 AI 分析与日报

## 项目概述

将微信 PC 端（4.x）加密的群聊图片自动解密导出，使用 Kimi k2.6 多模态模型对图片内容进行 AI 摘要分析，每天自动生成日报推送。

## 目标群聊（5 个）

| # | 群聊名称 |
|---|---------|
| 1 | 【VIP】建龙北京 |
| 2 | 中国矿产市场报告联系人群 |
| 3 | 建龙集团市场分析交流群 |
| 4 | Mysteel-铁矿石矿工群（正式） |
| 5 | Mysteel铁矿石资讯SVIP正式2群 |

## 每日流水线（4 步）

| 步骤 | 脚本 | 说明 | 耗时 |
|------|------|------|------|
| Step 0 | `image_downloader.py` | PyAutoGUI 点击下载当天新图 | 2-3 min |
| Step 1 | `image_export.py` | 解密导出 .dat → jpg/png | 1-2 min |
| Step 2 | `image_summary.py` | Kimi k2.6 AI 图片摘要 | 5-30 min |
| Step 3 | `daily_report.py` | 汇总报告，输出 JSON | <1 min |

## 文件结构

```
src/
├── image_export.py        # 图片解密导出（V2/V1/XOR 三格式）
├── image_summary.py       # Kimi AI 图片摘要（8 进程并行）
├── image_downloader.py    # PyAutoGUI 自动下载当天新图
├── daily.py               # Windows 主控脚本（Step 0~3）
├── daily_report.py        # 日报汇总脚本
├── daily_hermes.py        # Hermes cron 入口脚本（WSL）
└── daily_wsl.sh           # WSL 调用脚本
config/                    # 项目级配置
tests/                     # 测试数据与脚本
logs/                      # 每日运行日志
```

## 依赖

- Python 3.12
- pycryptodome
- zstandard
- PyAutoGUI
- opencv-python
- Kimi CLI (`~/.local/bin/kimi`)

## 使用

```bash
# 手动运行完整流水线
cd src
PYTHONIOENCODING=utf-8 python daily.py

# 单独运行某一步
PYTHONIOENCODING=utf-8 python image_export.py
PYTHONIOENCODING=utf-8 python image_summary.py
```

## 数据目录

- 导出图片：`D:\Wechat_File\Wechat_Image\`
- AI 摘要：各群目录下的 `_image_summary.json`
- 日志：`logs/`

## 配置

- 微信密钥：`C:\Users\lk\.wechat-cli\all_keys.json`
- Hermes 配置：`WSL ~/.hermes/config.yaml`
- 飞书 API：`WSL ~/.hermes/.env`

## 定时任务

Hermes cron：`0 6 * * *`（每天 06:00）

## 相关项目

- [wechat-cli](../wechat-cli/) — 微信数据库 CLI 工具
- [wechat-decrypt](../wechat-decrypt/) — V2 图片解密工具
