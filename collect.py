"""
定时采集脚本
由 GitHub Actions 每天自动调用
采集数据 + 调用 AI 生成日报 + 对 Trending 前3名进行 AI 分析
"""

import json
import os
from datetime import datetime

from scraper.github_trending import fetch_trending
from scraper.hacker_news import fetch_new_repos


DATA_DIR = "data"


def collect_and_save():
    """采集数据并保存（每次都重新采集并生成 AI 日报和分析）"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"devpulse_{today}.json")

    print(f"[{datetime.now()}] 开始采集数据...")

    projects = fetch_trending(language="", since="daily")
    new_repos = fetch_new_repos(language="", days=7, limit=20)

    # 1. 尝试对 Trending 前3名进行 AI 分析
    print("\n[步骤1] AI 正在分析热门项目...")
    for i, project in enumerate(projects[:3], 1):
        print(f"  正在分析第 {i} 名: {project['name']}...")
        try:
            from scraper.ai_analyzer import analyze_github_project
            analysis = analyze_github_project(project)
            project["ai_analysis"] = analysis
            print(f"  分析完成")
        except Exception as e:
            project["ai_analysis"] = f"AI 分析失败: {str(e)}"
            print(f"  分析失败: {e}")

    # 2. 尝试调用 AI 生成日报
    print("\n[步骤2] AI 正在生成今日趋势日报...")
    daily_summary = "AI 趋势日报生成失败，请检查 DEEPSEEK_API_KEY 是否正确配置。"
    try:
        from scraper.ai_analyzer import generate_daily_summary
        daily_summary = generate_daily_summary(projects, new_repos)
        print(f"AI 日报生成成功")
    except Exception as e:
        print(f"AI 日报生成失败: {e}")

    all_data = {
        "date": today,
        "github_trending": projects,
        "github_new_repos": new_repos,
        "daily_summary": daily_summary,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n[{datetime.now()}] 数据已保存到: {filepath}")
    print(f"  GitHub Trending: {len(projects)} 个项目")
    print(f"  近 7 天新项目: {len(new_repos)} 个")
    print(f"  AI 分析: {len([p for p in projects[:3] if p.get('ai_analysis')])} 个")
    print(f"  AI 日报: {'成功' if '失败' not in daily_summary else '失败'}")


if __name__ == "__main__":
    collect_and_save()