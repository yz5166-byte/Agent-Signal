"""数据源：arXiv 最新论文（cs.AI / cs.CL / cs.MA）。

对外只暴露一个函数：fetch() -> list[Item]
不依赖 LangGraph，可以单独运行调试：python -m src.sources.arxiv
"""

from datetime import datetime, timezone

import feedparser
import httpx

from src.models import Item, Section

API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "ai-edge-bot/0.1 (+https://github.com/yz5166-byte/ai-edge-bot)"

# 默认参数。第 5 步接入 config.yaml 后，改为由调用方传入覆盖。
# 用 tuple 而非 list：不可变，不会踩「可变默认参数」的坑。
DEFAULT_CATEGORIES = ("cs.AI", "cs.CL", "cs.MA")
DEFAULT_MAX_RESULTS = 50


def fetch(
    categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> list[Item]:
    """抓取最新提交的论文，按提交时间倒序。

    本函数只负责「取回来 + 转成 Item」，不做任何筛选——
    筛选和排序是 curate 节点的职责，两者分开才好定位问题。
    """
    params = {
        "search_query": " OR ".join(f"cat:{c}" for c in categories),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_results,
    }
    response = httpx.get(
        API_URL,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()  # HTTP 4xx/5xx 直接抛异常，别让脏数据往下流

    feed = feedparser.parse(response.text)  # arXiv 返回 Atom XML
    return [_to_item(entry) for entry in feed.entries]


def _to_item(entry) -> Item:
    """把 feedparser 解析出的一个 <entry> 转成项目统一的 Item。

    「归一化」就发生在这里：arXiv 的字段名在这个函数里终结，
    出了这个文件，全项目只认识 Item。
    """
    return Item(
        section=Section.PAPER,
        title=_clean(entry.title),
        url=entry.link,  # arXiv 的 abs 页面
        source="arXiv",
        published_at=_to_datetime(entry.get("published_parsed")),
        raw_text=_clean(entry.summary),  # 论文摘要，第 6 步喂给 LLM
        extra={  # arXiv 特有字段放进逃生舱，不污染主结构
            "authors": [a.name for a in entry.get("authors", [])],
            "categories": [t.term for t in entry.get("tags", [])],
            "pdf_url": _pdf_url(entry),
        },
    )


def _clean(text: str) -> str:
    """arXiv 的标题和摘要里有换行和多余空格，压成一行。"""
    return " ".join(text.split())


def _to_datetime(parsed) -> datetime | None:
    """feedparser 给的是 UTC 时间元组，转成带时区的 datetime。

    带时区很重要：后面要和「今天」比较，裸 datetime 无法和带时区的做比较。
    """
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


def _pdf_url(entry) -> str:
    """一个 entry 有多个链接（abs 页、PDF、DOI），挑出 PDF 那个。"""
    for link in entry.get("links", []):
        if link.get("type") == "application/pdf":
            return link.href
    return ""


if __name__ == "__main__":
    # 单独运行本文件即可看到真实数据：python -m src.sources.arxiv
    items = fetch(max_results=5)
    print(f"抓到 {len(items)} 篇\n")
    for i, item in enumerate(items, 1):
        when = f"{item.published_at:%Y-%m-%d %H:%M} UTC" if item.published_at else "时间未知"
        print(f"[{i}] {item.title}")
        print(f"    {when} | {item.extra['categories']}")
        print(f"    {item.url}")
        print(f"    {item.raw_text[:120]}...\n")
