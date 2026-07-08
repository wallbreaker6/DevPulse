"""
GitHub 搜索爬虫
通过 GitHub API 获取近期新创建的热门项目
"""

import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_new_repos(language="", days=7, limit=20):
    """
    通过 GitHub API 搜索近期新创建的热门项目

    参数:
        language: 编程语言筛选，空字符串表示全部
        days: 最近几天内创建的
        limit: 最多返回多少个

    返回:
        项目列表
    """
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    query = f"created:>{since}"
    if language:
        query += f" language:{language}"

    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    headers = {
        "User-Agent": "DevPulse/1.0",
        "Accept": "application/vnd.github.v3+json",
    }

    print(f"正在通过 GitHub API 搜索近 {days} 天的热门新项目...")
    response = requests.get(url, params=params, headers=headers, timeout=30, verify=False)

    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return []

    data = response.json()
    items = data.get("items", [])

    projects = []
    for item in items:
        projects.append({
            "name": item["full_name"],
            "link": item["html_url"],
            "description": item.get("description", "暂无描述"),
            "language": item.get("language", "未知"),
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "created_at": item.get("created_at", ""),
        })

    print(f"搜索完成，共获取 {len(projects)} 个新项目")
    return projects


if __name__ == "__main__":
    projects = fetch_new_repos()

    print("\n" + "=" * 60)
    print("近 7 天 GitHub 最热新项目")
    print("=" * 60)

    for i, p in enumerate(projects, 1):
        print(f"\n{i}. {p['name']}")
        print(f"   描述: {p['description'][:60] if p['description'] else '暂无'}")
        print(f"   语言: {p['language']}  |  Stars: {p['stars']}")
        print(f"   创建时间: {p['created_at'][:10]}")
        print(f"   链接: {p['link']}")