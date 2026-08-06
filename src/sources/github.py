"""数据源：GitHub 上热门的 AI / Agent 开源项目。

对外只暴露一个函数：fetch() -> list[Item]
独立运行调试：python -m src.sources.github
"""

import os
from datetime import date, datetime, timedelta

from src.models import Item, Section
from src.sources._shared import clean_text, http_get

API_URL = "https://api.github.com/search/repositories"
PER_QUERY = 15


def fetch(per_query: int = PER_QUERY) -> list[Item]:
    """两路检索后合并：新星项目 + 经典项目。

    GitHub 没有「star 增速」接口，所以用「新建不久却已高星」来近似「涨得快」。
    两路可能返回重复项目，不在这里去重——去重是 curate 节点的职责。
    """
    queries = [
        # 新星：90 天内新建、已有 50+ star，聚焦 Agent
        f"agent in:name,description created:>{_days_ago(90)} stars:>50",
        # 经典：2000+ star 且近 7 天仍在推送，覆盖面更广的老牌项目
        f"topic:llm stars:>2000 pushed:>{_days_ago(7)}",
    ]
    return [_to_item(repo) for q in queries for repo in _search(q, per_query)]


def _days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def _search(query: str, per_page: int) -> list[dict]:
    """发一次 Search API 请求，返回原始 repo 字典列表。"""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"  # 没 token 也能跑，只是限额低
    resp = http_get(
        API_URL,
        params={"q": query, "sort": "stars", "order": "desc", "per_page": per_page},
        headers=headers,
    )
    return resp.json()["items"]


def _to_item(repo: dict) -> Item:
    return Item(
        section=Section.REPO,
        title=repo["full_name"],
        url=repo["html_url"],
        source="GitHub",
        published_at=datetime.fromisoformat(repo["created_at"]),
        raw_text=clean_text(repo.get("description") or ""),
        extra={
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "topics": repo.get("topics", []),
        },
    )


if __name__ == "__main__":
    items = fetch()
    print(f"抓到 {len(items)} 个项目\n")
    for it in items:
        print(f"★{it.extra['stars']:>7}  {it.title[:40]:42} 建于 {it.published_at:%Y-%m-%d}")
