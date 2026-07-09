"""
DevPulse - AI 技术趋势分析器
主程序入口
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

from scraper.github_trending import fetch_trending
from scraper.hacker_news import fetch_new_repos
from scraper.ai_analyzer import analyze_github_project, generate_daily_summary

# 加载 .env 文件中的环境变量
load_dotenv()


def save_to_json(data, filename):
    """保存数据到 JSON 文件"""
    filepath = os.path.join("data", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filepath}")


def main():
    print("=" * 50)
    print("  DevPulse - AI 技术趋势分析器")
    print("=" * 50)

    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 抓取 GitHub Trending
    print("\n[步骤1] 抓取 GitHub 热门项目...")
    projects = fetch_trending(language="", since="daily")

    # 2. 搜索近期热门新项目
    print("\n[步骤2] 搜索近 7 天热门新项目...")
    new_repos = fetch_new_repos(language="", days=7, limit=20)

    # 3. AI 分析 Trending 前 3 名
    print("\n[步骤3] AI 正在分析热门项目...")
    for i, project in enumerate(projects[:3], 1):
        print(f"\n  正在分析第 {i} 名: {project['name']}...")
        analysis = analyze_github_project(project)
        project["ai_analysis"] = analysis
        print(f"  分析完成")

    # 4. AI 生成今日趋势总结
    print("\n[步骤4] AI 正在生成今日趋势日报...")
    daily_summary = generate_daily_summary(projects, new_repos)

    # 5. 合并所有数据
    all_data = {
        "date": today,
        "github_trending": projects,
        "github_new_repos": new_repos,
        "daily_summary": daily_summary,
    }

    # 6. 展示结果
    print("\n" + "=" * 50)
    print("  今日数据摘要")
    print("=" * 50)
    print(f"  GitHub Trending 项目: {len(projects)} 个")
    print(f"  近 7 天热门新项目: {len(new_repos)} 个")

    print("\n" + "=" * 50)
    print("  AI 趋势日报")
    print("=" * 50)
    print(daily_summary)

    print("\n" + "=" * 50)
    print("  AI 项目分析 Top 3")
    print("=" * 50)
    for i, project in enumerate(projects[:3], 1):
        print(f"\n  {i}. {project['name']} ({project['language']})")
        print(f"     今日 Star: {project['stars_today']}")
        print(f"     AI 分析: {project.get('ai_analysis', '无')}")

    # 7. 保存
    filename = f"devpulse_{today}.json"
    save_to_json(all_data, filename)

    print("\n完成！")


if __name__ == "__main__":
    main()