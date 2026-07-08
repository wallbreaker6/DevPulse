"""
GitHub Trending 爬虫
抓取 GitHub 今日热门开源项目
"""

import requests
import urllib3
from bs4 import BeautifulSoup

# 关闭 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_trending(language="", since="daily"):
    """
    抓取 GitHub Trending 页面

    参数:
        language: 编程语言筛选，如 "python", "javascript"，空字符串表示全部
        since: 时间范围，"daily" / "weekly" / "monthly"

    返回:
        项目列表，每个项目是字典
    """
    url = f"https://github.com/trending/{language}?since={since}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"正在抓取: {url}")
    response = requests.get(url, headers=headers, timeout=30, verify=False)

    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    projects = []

    repo_list = soup.select("article.Box-row")

    for item in repo_list:
        name_tag = item.select_one("h2 a")
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True).replace(" ", "").replace("\n", "")
        link = "https://github.com" + name_tag["href"]

        desc_tag = item.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else "暂无描述"

        lang_tag = item.select_one("[itemprop='programmingLanguage']")
        language_name = lang_tag.get_text(strip=True) if lang_tag else "未知"

        stars_today_tag = item.select_one("span.d-inline-block.float-sm-right")
        stars_today = stars_today_tag.get_text(strip=True) if stars_today_tag else "0"

        star_tags = item.select("a.Link--muted")
        total_stars = star_tags[0].get_text(strip=True) if star_tags else ""

        projects.append({
            "name": name,
            "link": link,
            "description": description,
            "language": language_name,
            "stars_today": stars_today,
            "total_stars": total_stars,
        })

    print(f"抓取完成，共获取 {len(projects)} 个项目")
    return projects


if __name__ == "__main__":
    projects = fetch_trending()

    print("\n" + "=" * 60)
    print("GitHub 今日热门项目")
    print("=" * 60)

    for i, p in enumerate(projects, 1):
        print(f"\n{i}. {p['name']}")
        print(f"   描述: {p['description'][:80]}")
        print(f"   语言: {p['language']}")
        print(f"   今日 Star: {p['stars_today']}")
        print(f"   链接: {p['link']}")