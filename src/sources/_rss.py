"""RSS 通用抓取逻辑，被 news_rss.py 和 official_blogs.py 共用。

两者的差别只有「feed 列表」和「归属板块」，逻辑完全一样，所以抽在这里。
"""

import feedparser

from src.models import Item, Section
from src.sources._shared import clean_text, http_get, to_datetime


def fetch_feeds(
    feeds: dict[str, str], section: Section, per_feed: int = 10
) -> tuple[list[Item], list[str]]:
    """抓取一组 RSS 源。feeds 形如 {"TechCrunch": "https://..."}。

    单个源失败只跳过它：RSS 地址随时可能改版或下线，
    不能让一个死链拖垮整批。失败信息随返回值带出去，最终写进 state["errors"]。
    """
    items: list[Item] = []
    errors: list[str] = []
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(http_get(url).text)
            items += [_to_item(e, source, section) for e in feed.entries[:per_feed]]
        except Exception as e:
            errors.append(f"{source} 抓取失败：{type(e).__name__}")
    return items, errors


def _to_item(entry, source: str, section: Section) -> Item:
    return Item(
        section=section,
        title=clean_text(entry.title),
        url=entry.link,
        source=source,
        published_at=to_datetime(entry.get("published_parsed")),
        raw_text=clean_text(entry.get("summary", ""))[:800],  # 截断：喂 LLM 用不上更多
    )
