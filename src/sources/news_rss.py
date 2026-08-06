"""数据源：行业新闻 RSS（媒体报道、市场与投资动态）。

对外只暴露一个函数：fetch() -> list[Item]
独立运行调试：python -m src.sources.news_rss
"""

from src.models import Item, Section
from src.sources._rss import fetch_feeds

FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "Ars Technica": "https://arstechnica.com/ai/feed/",
    "VentureBeat": "https://venturebeat.com/feed/",  # AI 分类的 feed 已停更，改用全站
    "Hacker News": "https://hnrss.org/frontpage?points=100",
}


def fetch() -> list[Item]:
    return fetch_feeds(FEEDS, Section.NEWS)


if __name__ == "__main__":
    items = fetch()
    print(f"抓到 {len(items)} 条\n")
    for it in items:
        print(f"[{it.source:16}] {it.title[:70]}")
