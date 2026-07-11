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


def get_available_dates():
    """获取所有可用的日期列表"""
    ensure_data_dir()
    data_files = glob.glob(os.path.join(DATA_DIR, "devpulse_*.json"))
    dates = []
    for f in data_files:
        filename = os.path.basename(f)
        # devpulse_2026-07-11.json -> 2026-07-11
        date_str = filename.replace("devpulse_", "").replace(".json", "")
        dates.append(date_str)
    dates.sort(reverse=True)
    return dates


def load_data_by_date(date_str):
    """按日期加载数据"""
    filepath = os.path.join(DATA_DIR, f"devpulse_{date_str}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_latest_data():
    """加载最新的数据文件"""
    dates = get_available_dates()
    if not dates:
        return None
    return load_data_by_date(dates[0])


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

    # 获取所有可用日期
    available_dates = get_available_dates()

    # 获取当前选择的日期
    selected_date = request.args.get("date", "")

    # 加载数据
    if selected_date:
        data = load_data_by_date(selected_date)
    else:
        data = load_latest_data()
        if data:
            selected_date = data.get("date", "")

    if not data:
        return "<h1>暂无数据，请稍后刷新重试</h1>"

    # 搜索和筛选
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
        date=selected_date,
        available_dates=available_dates,
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


@app.route("/api/data")
def api_data():
    """数据 API 接口"""
    data = load_latest_data()
    if not data:
        from flask import jsonify
        return jsonify({"error": "暂无数据"}), 404
    from flask import jsonify
    return jsonify(data)


@app.route("/api/trending")
def api_trending():
    """只返回 Trending 项目"""
    data = load_latest_data()
    if not data:
        from flask import jsonify
        return jsonify({"error": "暂无数据"}), 404
    from flask import jsonify
    return jsonify(data.get("github_trending", []))


if __name__ == "__main__":
    app.run(debug=True, port=5000)