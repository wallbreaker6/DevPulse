"""
DevPulse - Web 看板
Flask 应用入口
"""

import json
import os
import glob
from datetime import datetime
from flask import Flask, render_template, request

from scraper.github_trending import fetch_trending
from scraper.hacker_news import fetch_new_repos
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATA_DIR = "data"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_latest_data():
    ensure_data_dir()
    data_files = glob.glob(os.path.join(DATA_DIR, "devpulse_*.json"))
    if not data_files:
        return None

    data_files.sort(reverse=True)
    latest_file = data_files[0]

    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_and_save():
    """自动采集今天的最新数据"""
    ensure_data_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"devpulse_{today}.json")

    # 如果今天已经有数据，检查是否超过 6 小时，超过就更新
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        hours_old = (datetime.now().timestamp() - mtime) / 3600
        if hours_old < 6:
            print(f"数据在 6 小时内，无需更新")
            return
        print(f"数据已超过 6 小时，开始更新...")

    print("开始采集数据...")
    projects = fetch_trending(language="", since="daily")
    new_repos = fetch_new_repos(language="", days=7, limit=20)

    all_data = {
        "date": today,
        "github_trending": projects,
        "github_new_repos": new_repos,
        "daily_summary": "AI 趋势日报需要在本地运行 python main.py 生成。",
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filepath}")


def get_all_languages(data):
    """提取所有出现过的编程语言"""
    languages = set()
    for p in data.get("github_trending", []):
        lang = p.get("language", "")
        if lang and lang != "未知":
            languages.add(lang)
    for p in data.get("github_new_repos", []):
        lang = p.get("language", "")
        if lang and lang != "未知":
            languages.add(lang)
    return sorted(languages)


@app.route("/")
def index():
    """首页 - 支持搜索和筛选"""
    # 每次访问时检查是否需要自动采集
    collect_and_save()

    data = load_latest_data()

    if not data:
        return "<h1>数据采集失败，请稍后刷新重试</h1>"

    # 获取筛选参数
    keyword = request.args.get("q", "").strip().lower()
    lang_filter = request.args.get("lang", "").strip()

    trending = data.get("github_trending", [])
    new_repos = data.get("github_new_repos", [])

    # 关键词搜索
    if keyword:
        trending = [p for p in trending
                    if keyword in (p.get("name", "") + p.get("description", "")).lower()]
        new_repos = [p for p in new_repos
                     if keyword in (p.get("name", "") + (p.get("description") or "")).lower()]

    # 语言筛选
    if lang_filter:
        trending = [p for p in trending if p.get("language", "") == lang_filter]
        new_repos = [p for p in new_repos if p.get("language", "") == lang_filter]

    # 获取所有语言列表（用于下拉菜单）
    all_languages = get_all_languages(data)

    return render_template(
        "index.html",
        date=data.get("date", ""),
        trending=trending,
        new_repos=new_repos,
        summary=data.get("daily_summary", "暂无总结"),
        languages=all_languages,
        keyword=keyword,
        lang_filter=lang_filter,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)