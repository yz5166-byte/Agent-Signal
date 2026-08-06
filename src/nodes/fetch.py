"""节点：抓取。各数据源并行执行，各自把结果写回 State。

只做「调用 sources 里的函数 + 塞进 State」，抓取细节不写在这里。
"""

from src.sources import arxiv
from src.state import ReportState


def fetch_papers(state: ReportState) -> dict:
    """抓取 arXiv 论文，追加进 State 的 raw_items。

    节点函数的固定形状：接收整个 state，返回一个「只包含自己负责的字段」的 dict。
    不用手动合并——LangGraph 会拿这个 dict 去更新 state，
    raw_items 带了 operator.add，所以是追加而不是覆盖。
    """
    items = arxiv.fetch()
    return {"raw_items": items}
