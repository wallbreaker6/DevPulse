"""
AI 分析模块
调用 DeepSeek API 对爬取的数据进行智能分析
"""

import os
from openai import OpenAI


def get_client():
    """初始化 DeepSeek 客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    return client


def analyze_github_project(project):
    """
    用 AI 分析一个 GitHub 项目

    参数:
        project: 项目字典，包含 name、description、language 等字段

    返回:
        AI 生成的分析文本
    """
    client = get_client()

    prompt = f"""你是一位资深技术分析师。请用中文分析以下 GitHub 热门项目：

项目名称：{project['name']}
描述：{project['description']}
编程语言：{project['language']}
今日 Star 数：{project['stars_today']}
项目链接：{project['link']}

请从以下角度进行分析（控制在 150 字以内）：
1. 这个项目是做什么的（一句话概括）
2. 为什么它最近火了（可能的原因）
3. 对开发者有什么价值

请直接输出分析内容，不要加标题或编号。"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 分析失败: {str(e)}"


def generate_daily_summary(projects, new_repos):
    """
    用 AI 生成今日技术趋势总结

    参数:
        projects: Trending 项目列表
        new_repos: 新项目列表

    返回:
        今日总结文本
    """
    client = get_client()

    trending_text = "\n".join(
        [f"- {p['name']}（{p['language']}）：{p['description'][:50]}"
         for p in projects[:10]]
    )

    new_text = "\n".join(
        [f"- {p['name']}（{p['language']}，{p['stars']} stars）：{(p['description'] or '暂无描述')[:50]}"
        for p in new_repos[:10]]
    )

    prompt = f"""你是一位技术趋势分析师。请根据今天的数据，用中文写一份简洁的技术趋势日报。

【今日 GitHub Trending 热门项目】
{trending_text}

【近 7 天最热新项目】
{new_text}

请从以下角度总结（控制在 300 字以内）：
1. 今天的技术热点是什么
2. 哪个方向最火（AI、前端、后端、DevOps 等）
3. 推荐关注哪 2-3 个项目，为什么

请直接输出总结内容，不要加标题。"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 总结生成失败: {str(e)}"