# WeChat AI Daily — 微信群聊图片 AI 分析与日报

## 项目概述

将微信 PC 端（4.x）加密的群聊图片自动解密导出，使用 Kimi k2.6 多模态模型对图片内容进行 AI 摘要分析，每天早上 6:00 自动生成日报推送到飞书。

## 功能表

| 功能 | 状态 | 说明 |
|------|------|------|
| 图片解密导出（V2/V1/XOR） | ✅ 已完成 | 支持微信 4.x 三种加密格式 |
| Kimi AI 图片摘要 | ✅ 已完成 | 8 进程并行，kimi-for-coding 模型 |
| PyAutoGUI 自动下载原图 | ✅ 已完成 | 模拟点击，含防封号随机延迟 |
| 日报汇总生成 | ✅ 已完成 | 输出 JSON 报告 |
| Hermes 定时推送 | ✅ 已完成 | 每天 06:00 自动执行，推送飞书 |
| 仅处理当天新图 | ✅ 已完成 | 不补齐历史，避免重复处理 |
| 聊天记录导出 | ⏳ 待开始 | 规划迁移到 wechat-chat-history |

## 技术栈

- Python 3.12
- pycryptodome（AES 解密）
- zstandard（压缩）
- PyAutoGUI（屏幕自动化）
- opencv-python（图像处理）
- Kimi CLI（AI 摘要）
- Hermes（定时任务 + 飞书推送）

## 关联项目

| 项目 | 关系 | 链接 |
|------|------|------|
| wechat-cli | 上游依赖 | [本地](../wechat-cli/) |
| wechat-decrypt | 上游依赖 | [本地](../wechat-decrypt/) |
| wechat-chat-history | 下游扩展 | [本地](../wechat-chat-history/) |

## 代码仓库

- GitHub：[github.com/Jeff19930831/wechat-ai-daily](https://github.com/Jeff19930831/wechat-ai-daily)
- 本地：`D:\ClaudeCode\wechat-ai-daily`

## 文档位置

- 知识库：`Win_Claude_Work\wechat-ai-daily`

## 每日流水线（4 步）

| 步骤 | 脚本 | 说明 | 耗时 |
|------|------|------|------|
| Step 0 | `src/image_downloader.py` | PyAutoGUI 点击下载当天新图 | 2-3 min |
| Step 1 | `src/image_export.py` | 解密导出 .dat → jpg/png | 1-2 min |
| Step 2 | `src/image_summary.py` | Kimi k2.6 AI 图片摘要 | 5-30 min |
| Step 3 | `src/daily_report.py` | 汇总报告，输出 JSON | <1 min |

## 使用方式

```bash
# 手动运行完整流水线
cd src
PYTHONIOENCODING=utf-8 python daily.py

# 单独运行某一步
PYTHONIOENCODING=utf-8 python image_export.py
PYTHONIOENCODING=utf-8 python image_summary.py
PYTHONIOENCODING=utf-8 python image_downloader.py
```

## 目标群聊（5 个）

| # | 群聊名称 |
|---|---------|
| 1 | 【VIP】建龙北京 |
| 2 | 中国矿产市场报告联系人群 |
| 3 | 建龙集团市场分析交流群 |
| 4 | Mysteel-铁矿石矿工群（正式） |
| 5 | Mysteel铁矿石资讯SVIP正式2群 |

## 数据目录

- 导出图片：`D:\Wechat_File\Wechat_Image\`
- AI 摘要：各群目录下的 `_image_summary.json`
- 运行日志：`logs/`

## 配置

| 配置项 | 位置 | 说明 |
|--------|------|------|
| 微信密钥 | `C:\Users\lk\.wechat-cli\all_keys.json` | 26 个数据库密钥 |
| wechat-cli 配置 | `C:\Users\lk\.wechat-cli\config.json` | 数据库目录 |
| Hermes 配置 | WSL `~/.hermes/config.yaml` | 模型、飞书 |
| 飞书 API | WSL `~/.hermes/.env` | APP_ID / APP_SECRET |

## 定时任务

- Hermes cron：`0 6 * * *`（每天 06:00）
- 脚本：WSL `~/.hermes/scripts/wechat_daily.py`

## 维护者

- 创建者：lk
- 创建日期：2026-04
- 自动化日期：2026-04-24
- 当前状态：运行中（每天自动）
