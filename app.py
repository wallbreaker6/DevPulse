"""
DevPulse - Web 看板
Flask 应用入口
"""

import json
import os
import glob
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)


def load_latest_data():
    """加载最新的数据文件"""
    data_files = glob.glob(os.path.join("data", "devpulse_*.json"))
    if not data_files:
        return None

    # 按文件名排序，取最新的
    data_files.sort(reverse=True)
    latest_file = data_files[0]

    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    """首页 - 看板"""
    data = load_latest_data()

    if not data:
        return "<h1>暂无数据，请先运行 python main.py 采集数据</h1>"

    return render_template(
        "index.html",
        date=data.get("date", ""),
        trending=data.get("github_trending", []),
        new_repos=data.get("github_new_repos", []),
        summary=data.get("daily_summary", "暂无总结"),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)