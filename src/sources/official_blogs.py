"""数据源：各家官方博客 RSS（产品发布、模型更新）。

对外只暴露一个函数：fetch() -> list[Item]
独立运行调试：python -m src.sources.official_blogs
"""

from src.models import Item, Section
from src.sources._rss import fetch_feeds

FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Microsoft Research": "https://www.microsoft.com/en-us/research/feed/",
    "Google Research": "https://research.google/blog/rss/",
    # Anthropic 与 Meta AI 没有公开 RSS（实测多个地址均 404），暂缺
}


def fetch() -> list[Item]:
    return fetch_feeds(FEEDS, Section.PRODUCT)


if __name__ == "__main__":
    items = fetch()
    print(f"抓到 {len(items)} 条\n")
    for it in items:
        print(f"[{it.source:20}] {it.title[:70]}")
