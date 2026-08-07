"""节点：抓取。四个数据源并行执行，各自把结果写回 State。

只做「调用 sources 里的函数 + 塞进 State」，抓取细节不写在这里。

四个函数几乎一样，但故意不合并成工厂函数：显式写出来，
出错时 traceback 里直接看到是哪个节点炸的，也方便各自单独演化。
"""

from collections.abc import Callable

from src.models import Item
from src.sources import arxiv, github, news_rss, official_blogs
from src.state import ReportState


def fetch_papers(state: ReportState) -> dict:
    """arXiv 论文 -> raw_items"""
    return _safe("arXiv", arxiv.fetch)


def fetch_repos(state: ReportState) -> dict:
    """GitHub 项目 -> raw_items"""
    return _safe("GitHub", github.fetch)


def fetch_news(state: ReportState) -> dict:
    """行业新闻 -> raw_items"""
    return _safe("新闻 RSS", news_rss.fetch)


def fetch_blogs(state: ReportState) -> dict:
    """官方博客 -> raw_items"""
    return _safe("官方博客", official_blogs.fetch)


def _safe(label: str, fetcher: Callable[[], tuple[list[Item], list[str]]]) -> dict:
    """整个源挂掉也不中断全图：记进 errors，当天少一个板块而已。

    源自己返回的 errors 是「部分失败」（6 个 RSS 挂了 1 个），
    这里 except 到的是「整体失败」（网络断了、接口改了），两者都进同一个字段。
    """
    try:
        items, errors = fetcher()
        return {"raw_items": items, "errors": errors}
    except Exception as e:
        return {"raw_items": [], "errors": [f"{label} 整体抓取失败：{type(e).__name__}"]}
