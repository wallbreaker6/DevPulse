"""
历史趋势数据聚合
从多个日期的数据文件中提取趋势信息
"""

import json
import os
import glob
from collections import defaultdict


DATA_DIR = "data"


def load_all_data():
    """加载所有历史数据文件"""
    data_files = glob.glob(os.path.join(DATA_DIR, "devpulse_*.json"))
    all_data = []

    for filepath in sorted(data_files):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.append(data)
        except Exception as e:
            print(f"读取 {filepath} 失败: {e}")

    return all_data


def get_star_trends(all_data, top_n=10):
    """
    提取项目的 Star 趋势数据

    返回:
        dates: 日期列表
        trends: {项目名: [每天的star数]} 字典
    """
    dates = []
    # 记录每天的项目和 star 数
    daily_projects = []

    for data in all_data:
        date = data.get("date", "")
        dates.append(date)

        projects = {}
        for p in data.get("github_trending", []):
            name = p.get("name", "")
            stars_text = p.get("stars_today", "0")
            # 提取数字: "1,297 stars today" -> 1297
            try:
                stars = int(stars_text.replace(",", "").split()[0])
            except (ValueError, IndexError):
                stars = 0
            projects[name] = stars

        daily_projects.append(projects)

    if not daily_projects:
        return [], {}

    # 统计每个项目出现的次数和总 star 数
    project_total = defaultdict(int)
    project_count = defaultdict(int)
    for daily in daily_projects:
        for name, stars in daily.items():
            project_total[name] += stars
            project_count[name] += 1

    # 选出现次数最多、总 star 最高的 top_n 个项目
    sorted_projects = sorted(
        project_total.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    top_names = [name for name, _ in sorted_projects]

    # 构建趋势数据
    trends = {}
    for name in top_names:
        trend = []
        for daily in daily_projects:
            trend.append(daily.get(name, 0))
        trends[name] = trend

    return dates, trends


def get_language_stats(all_data):
    """
    统计编程语言分布

    返回:
        [(语言名, 出现次数), ...]
    """
    lang_count = defaultdict(int)

    for data in all_data:
        for p in data.get("github_trending", []):
            lang = p.get("language", "未知")
            if lang and lang != "未知":
                lang_count[lang] += 1

        for p in data.get("github_new_repos", []):
            lang = p.get("language", "未知")
            if lang and lang != "未知":
                lang_count[lang] += 1

    # 排序取前 15
    sorted_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:15]
    return sorted_langs


def get_daily_project_count(all_data):
    """
    统计每天采集到的项目数量

    返回:
        dates: 日期列表
        trending_counts: Trending 数量
        new_counts: 新项目数量
    """
    dates = []
    trending_counts = []
    new_counts = []

    for data in all_data:
        dates.append(data.get("date", ""))
        trending_counts.append(len(data.get("github_trending", [])))
        new_counts.append(len(data.get("github_new_repos", [])))

    return dates, trending_counts, new_counts