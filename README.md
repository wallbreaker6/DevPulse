<div align="center">

# DevPulse

**AI 驱动的开发者技术趋势分析器**

自动抓取 GitHub 热门项目，用 AI 生成趋势日报和深度分析

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-7c3aed?logo=openai&logoColor=white)](https://platform.deepseek.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 项目简介

DevPulse 是一个面向开发者的技术趋势分析工具。它能够：

- 自动抓取 **GitHub Trending** 热门项目
- 通过 **GitHub API** 搜索近期最火的新项目
- 调用 **DeepSeek AI** 对项目进行智能分析和中文摘要生成
- 自动生成 **每日技术趋势日报**
- 通过 **Flask Web 看板** 可视化展示所有数据

## 效果展示

### 命令行输出

```
==================================================
  DevPulse - AI 技术趋势分析器
==================================================

[步骤1] 抓取 GitHub 热门项目...
抓取完成，共获取 15 个项目

[步骤2] 搜索近 7 天热门新项目...
搜索完成，共获取 20 个新项目

[步骤3] AI 正在分析热门项目...
[步骤4] AI 正在生成今日趋势日报...

==================================================
  AI 趋势日报
==================================================
今日技术热点集中在 AI Agent 工具链与基础设施的
爆发式增长，最火方向无疑是 AI ...
```

### Web 看板

启动后访问 `http://127.0.0.1:5000`，可看到：

- 数据统计卡片
- AI 趋势日报摘要
- GitHub Trending 项目列表（含 AI 深度分析）
- 近 7 天热门新项目列表

## 项目结构

```
DevPulse/
├── app.py                    # Flask Web 应用入口
├── main.py                   # 命令行主程序
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量模板
├── .gitignore
│
├── scraper/                  # 爬虫模块
│   ├── __init__.py
│   ├── github_trending.py    # GitHub Trending 爬虫
│   ├── hacker_news.py        # GitHub API 热门新项目爬虫
│   └── ai_analyzer.py        # DeepSeek AI 分析模块
│
├── templates/                # Web 页面模板
│   └── index.html            # 看板页面
│
├── data/                     # 采集的数据（自动生成）
│   └── devpulse_YYYY-MM-DD.json
│
└── venv/                     # 虚拟环境（不上传）
```

## 技术栈

| 模块 | 技术 |
|---|---|
| 数据采集 | Python + Requests + BeautifulSoup4 |
| 数据分析 | DeepSeek API（OpenAI SDK） |
| Web 框架 | Flask + Jinja2 |
| 部署 | PythonAnywhere / 本地运行 |
| 版本管理 | Git + GitHub |

## 快速开始

### 环境要求

- Python 3.10+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/wallbreaker6/DevPulse.git
cd DevPulse
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-你的key
```

> API Key 获取：前往 [DeepSeek 开放平台](https://platform.deepseek.com) 注册并创建

### 5. 运行

**命令行模式（含 AI 分析）：**

```bash
python main.py
```

**Web 看板模式：**

```bash
python app.py
```

然后打开浏览器访问 `http://127.0.0.1:5000`

## 核心功能详解

### GitHub Trending 爬虫

- 抓取 GitHub 每日/每周/每月热门项目
- 支持按编程语言筛选
- 提取项目名称、描述、语言、Star 数等信息

### GitHub API 搜索

- 通过 GitHub Search API 搜索近期新创建的热门项目
- 按 Star 数排序
- 支持编程语言和时间范围筛选

### AI 智能分析

- 对 Trending Top 3 项目进行深度分析
- 分析项目用途、火爆原因、对开发者的价值
- 生成每日技术趋势日报

### Web 看板

- 响应式设计，支持移动端
- 暗色主题，程序员友好的视觉风格
- 数据统计、AI 日报、项目卡片分区展示

## TODO

- [ ] 添加更多数据源（Reddit、V2EX、掘金）
- [ ] 支持关键词搜索和语言筛选
- [ ] 添加项目历史趋势图表
- [ ] 定时自动采集（每日 Cron Job）
- [ ] 邮件/微信推送每日日报
- [ ] 深色/浅色主题切换

## 作者

**wallbreaker6** — 计算机本科生

- GitHub：[@wallbreaker6](https://github.com/wallbreaker6)

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

---

<div align="center">

如果觉得有用，给个 Star 支持一下

</div>
