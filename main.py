"""
DevPulse - AI 技术趋势分析器
主程序入口
"""

import json
import os
from datetime import datetime

from scraper.github_trending import fetch_trending


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

    # 1. 抓取 GitHub Trending
    print("\n[步骤1] 抓取 GitHub 热门项目...")
    projects = fetch_trending(language="", since="daily")

    if not projects:
        print("没有抓取到数据，请检查网络连接")
        return

    # 2. 显示结果
    print(f"\n[步骤2] 共获取 {len(projects)} 个热门项目:")
    print("-" * 50)

    for i, p in enumerate(projects[:10], 1):
        print(f"  {i:2d}. {p['name']:30s} {p['stars_today']:>15s}")
        print(f"      {p['description'][:60]}")
        print()

    # 3. 保存数据
    print("[步骤3] 保存数据...")
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"github_trending_{today}.json"
    save_to_json(projects, filename)

    print("\n完成！数据已保存。")


if __name__ == "__main__":
    main()