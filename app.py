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
from scraper.trends import (
    load_all_data,
    get_star_trends,
    get_language_stats,
    get_daily_project_count,
)
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
    """自动采集数据（6 小时更新一次）"""
    ensure_data_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"devpulse_{today}.json")

    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        hours_old = (datetime.now().timestamp() - mtime) / 3600
        if hours_old < 6:
            return
        print(f"数据超过 6 小时，更新中...")

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
    """首页 - 看板"""
    collect_and_save()
    data = load_latest_data()

    if not data:
        return "<h1>数据采集失败，请稍后刷新重试</h1>"

    keyword = request.args.get("q", "").strip().lower()
    lang_filter = request.args.get("lang", "").strip()

    trending = data.get("github_trending", [])
    new_repos = data.get("github_new_repos", [])

    if keyword:
        trending = [p for p in trending
                    if keyword in (p.get("name", "") + p.get("description", "")).lower()]
        new_repos = [p for p in new_repos
                     if keyword in (p.get("name", "") + (p.get("description") or "")).lower()]

    if lang_filter:
        trending = [p for p in trending if p.get("language", "") == lang_filter]
        new_repos = [p for p in new_repos if p.get("language", "") == lang_filter]

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


@app.route("/trends")
def trends():
    """趋势图表页面"""
    all_data = load_all_data()

    if not all_data:
        return render_template("trends.html", dates=[], star_names=[], star_series=[],
                               trending_counts=[], new_counts=[], lang_data=[])

    dates, star_trends = get_star_trends(all_data, top_n=8)
    lang_stats = get_language_stats(all_data)
    dates_count, trending_counts, new_counts = get_daily_project_count(all_data)

    # 构建 ECharts 需要的数据格式
    star_names = list(star_trends.keys())
    star_series = []
    chart_colors = ['#00e5a0', '#5b9cf6', '#f0c946', '#f65b5b', '#ff8c42',
                    '#a78bfa', '#38bdf8', '#fb7185']

    for i, name in enumerate(star_names):
        star_series.append({
            "name": name,
            "type": "line",
            "smooth": True,
            "data": star_trends[name],
            "lineStyle": {"width": 2},
            "symbolSize": 6,
            "itemStyle": {"color": chart_colors[i % len(chart_colors)]},
        })

    lang_data = [{"name": name, "value": count} for name, count in lang_stats]

    return render_template(
        "trends.html",
        dates=dates,
        star_names=star_names,
        star_series=star_series,
        trending_counts=trending_counts,
        new_counts=new_counts,
        lang_data=lang_data,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)