"""
DevPulse - Web 看板
Flask 应用入口
"""

import json
import os
import glob
from datetime import datetime
from flask import Flask, render_template

from scraper.github_trending import fetch_trending
from scraper.hacker_news import fetch_new_repos
from scraper.ai_analyzer import analyze_github_project, generate_daily_summary
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATA_DIR = "data"


def ensure_data_dir():
    """确保 data 目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_latest_data():
    """加载最新的数据文件"""
    ensure_data_dir()
    data_files = glob.glob(os.path.join(DATA_DIR, "devpulse_*.json"))
    if not data_files:
        return None

    data_files.sort(reverse=True)
    latest_file = data_files[0]

    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_and_save():
    """采集数据并保存（含 AI 分析）"""
    ensure_data_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"devpulse_{today}.json")

    if os.path.exists(filepath):
        print(f"今天的数据已存在: {filepath}")
        return

    print("开始采集数据...")
    projects = fetch_trending(language="", since="daily")
    new_repos = fetch_new_repos(language="", days=7, limit=20)

    # AI 分析 Top 3
    print("开始 AI 分析...")
    for i, project in enumerate(projects[:3], 1):
        print(f"分析第 {i} 名: {project['name']}...")
        try:
            analysis = analyze_github_project(project)
            project["ai_analysis"] = analysis
        except Exception as e:
            project["ai_analysis"] = f"分析失败: {str(e)}"

    # AI 生成趋势日报
    print("生成趋势日报...")
    try:
        daily_summary = generate_daily_summary(projects, new_repos)
    except Exception as e:
        daily_summary = f"日报生成失败: {str(e)}"

    all_data = {
        "date": today,
        "github_trending": projects,
        "github_new_repos": new_repos,
        "daily_summary": daily_summary,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filepath}")


@app.route("/")
def index():
    """首页"""
    data = load_latest_data()

    if not data:
        collect_and_save()
        data = load_latest_data()

    if not data:
        return "<h1>数据采集失败，请稍后刷新重试</h1>"

    return render_template(
        "index.html",
        date=data.get("date", ""),
        trending=data.get("github_trending", []),
        new_repos=data.get("github_new_repos", []),
        summary=data.get("daily_summary", "暂无总结"),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)