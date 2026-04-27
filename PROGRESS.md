# WeChat AI Daily — 进展记录

> 按时间倒序排列

---

## 2026-04-27 — 项目重组

### 已完成
- [x] 重组目录结构：脚本移入 `src/`，新增 `config/`、`tests/`、`logs/`
- [x] 创建 GitHub 仓库并 push
- [x] 修复脚本中的硬编码路径（`daily.py`、`daily_hermes.py`）
- [x] 创建 README.md、.gitignore
- [x] 创建文档项目（Win_Claude_Work）

### 待办
- [ ] 验证 Hermes cron 路径更新后是否正常
- [ ] Push 到 GitHub 后配置远程跟踪

---

## 2026-04-24 — 自动化完成

### 已完成
- [x] 设置 Hermes 定时任务（每天 06:00）
- [x] 修复 WSL 路径和编码问题
- [x] 添加 PyAutoGUI 自动下载原图功能
- [x] 验证批量下载效果（90秒内11张）
- [x] 更新为仅处理当天新图片，不补齐历史

### 阻塞
- Kimi CLI 中文路径问题 → 解决：复制到 `D:/ClaudeCode/kimi_temp/`（纯 ASCII 路径）
- Hermes 模型 404 → 解决：改用 `kimi-for-coding`

---

## 2026-04-23 — 核心功能完成

### 已完成
- [x] wechat-cli 安装和配置（SQLCipher 4 解密）
- [x] 提取 26 个数据库的加密密钥
- [x] V2 图片解密实现（AES-128-ECB + XOR）
- [x] 图片导出脚本（V1/V2/XOR 三格式支持）
- [x] Kimi AI 图片摘要（8 进程并行）
- [x] 日报汇总脚本

### 关键技术突破
- V2 AES 密钥从微信进程内存提取：`5410f6d49b9e6eda`
- XOR 密钥推导：`0x5c`（通过缩略图 FF D9 特征统计）

---

## 2026-04-21 — 项目启动

### 已完成
- [x] 需求确认：微信群聊图片自动分析 → 飞书日报
- [x] 技术选型：wechat-cli + Kimi k2.6 + Hermes
- [x] 环境搭建：Python 3.12、依赖安装

### 初始需求
- 5 个铁矿石行业群聊
- 每天早上 6:00 推送图片摘要日报到飞书
