"""数据源：arXiv 最新论文（cs.AI / cs.CL / cs.MA）。

对外只暴露一个函数：fetch() -> list[Item]
独立运行调试：python -m src.sources.arxiv
"""

import feedparser

from src.models import Item, Section
from src.sources._shared import clean_text, http_get, to_datetime

API_URL = "https://export.arxiv.org/api/query"
# 用 tuple 而非 list：不可变，不会踩「可变默认参数」的坑
DEFAULT_CATEGORIES = ("cs.AI", "cs.CL", "cs.MA")
DEFAULT_MAX_RESULTS = 50


def fetch(
    categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> list[Item]:
    """抓取最新提交的论文，按提交时间倒序。

    本函数只负责「取回来 + 转成 Item」，不做筛选——
    筛选和排序是 curate 节点的职责，分开才好定位问题。
    """
    resp = http_get(
        API_URL,
        params={
            "search_query": " OR ".join(f"cat:{c}" for c in categories),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "start": 0,
            "max_results": max_results,
        },
    )
    feed = feedparser.parse(resp.text)  # arXiv 返回 Atom XML
    return [_to_item(entry) for entry in feed.entries]


def _to_item(entry) -> Item:
    """把 feedparser 解析出的一个 <entry> 转成项目统一的 Item。

    「归一化」就发生在这里：arXiv 的字段名到此为止，
    出了这个文件，全项目只认识 Item。
    """
    return Item(
        section=Section.PAPER,
        title=clean_text(entry.title),
        url=entry.link,  # arXiv 的 abs 页面
        source="arXiv",
        published_at=to_datetime(entry.get("published_parsed")),
        raw_text=clean_text(entry.summary),  # 论文摘要，第 6 步喂给 LLM
        extra={  # arXiv 特有字段放进逃生舱，不污染主结构
            "authors": [a.name for a in entry.get("authors", [])],
            "categories": [t.term for t in entry.get("tags", [])],
            "pdf_url": _pdf_url(entry),
        },
    )


def _pdf_url(entry) -> str:
    """一个 entry 有多个链接（abs 页、PDF、DOI），挑出 PDF 那个。"""
    for link in entry.get("links", []):
        if link.get("type") == "application/pdf":
            return link.href
    return ""


if __name__ == "__main__":
    items = fetch(max_results=5)
    print(f"抓到 {len(items)} 篇\n")
    for i, it in enumerate(items, 1):
        print(f"[{i}] {it.title}")
        print(f"    {it.published_at:%Y-%m-%d %H:%M} UTC | {it.extra['categories']}")
        print(f"    {it.url}\n")
