"""
DevPulse - AI 技术趋势分析器
主程序入口
"""

import json
import os
from datetime import datetime

from scraper.github_trending import fetch_trending
from scraper.hacker_news import fetch_new_repos


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

    # 2. 通过 GitHub API 搜索近期热门新项目
    print("\n[步骤2] 搜索近 7 天热门新项目...")
    new_repos = fetch_new_repos(language="", days=7, limit=20)

    # 3. 合并数据
    all_data = {
        "date": today,
        "github_trending": projects,
        "github_new_repos": new_repos,
    }

    # 4. 显示摘要
    print("\n" + "=" * 50)
    print("  今日数据摘要")
    print("=" * 50)
    print(f"  GitHub Trending 项目: {len(projects)} 个")
    print(f"  近 7 天热门新项目: {len(new_repos)} 个")

    if projects:
        print(f"\n  Trending 第一名: {projects[0]['name']}")
        print(f"  今日 Star: {projects[0]['stars_today']}")

    if new_repos:
        print(f"\n  新项目第一名: {new_repos[0]['name']}")
        print(f"  总 Star: {new_repos[0]['stars']}")

    # 5. 保存
    filename = f"devpulse_{today}.json"
    save_to_json(all_data, filename)

    print("\n完成！")


if __name__ == "__main__":
    main()