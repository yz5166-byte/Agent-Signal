"""节点：抓取。四个数据源并行执行，各自把结果写回 State。

只做「调用 sources 里的函数 + 塞进 State」，抓取细节不写在这里。

四个函数几乎一样，但故意不合并成工厂函数：显式写出来，
出错时 traceback 里直接看到是哪个节点炸的，也方便各自单独演化。
"""

from src.sources import arxiv, github, news_rss, official_blogs
from src.state import ReportState


def fetch_papers(state: ReportState) -> dict:
    """arXiv 论文 -> raw_items"""
    return {"raw_items": arxiv.fetch()}


def fetch_repos(state: ReportState) -> dict:
    """GitHub 项目 -> raw_items"""
    return {"raw_items": github.fetch()}


def fetch_news(state: ReportState) -> dict:
    """行业新闻 -> raw_items"""
    return {"raw_items": news_rss.fetch()}


def fetch_blogs(state: ReportState) -> dict:
    """官方博客 -> raw_items"""
    return {"raw_items": official_blogs.fetch()}
