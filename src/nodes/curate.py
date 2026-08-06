"""节点：精选（纯 Python，不调 LLM）。

去重 -> 时效过滤 -> 排序 -> 每板块截断成候选池，写入 state["items"]。

这里只做「机器能可靠判断」的事。「哪条更值得看」需要读懂内容，
交给第 6 步的 LLM 打分，所以本节点产出的是候选池而非最终条数。
"""

import re
from datetime import datetime, timedelta, timezone

from src.models import Item, Section
from src.state import ReportState

# 各板块的时效窗口（天）。
# repo 的 published_at 是「仓库创建时间」，和「最近是否热门」无关
# （AutoGPT 建于 2023 年），所以不做时效过滤，改用 star 数排序。
MAX_AGE_DAYS = {
    Section.PAPER: 3,
    Section.NEWS: 2,
    Section.PRODUCT: 7,
    Section.REPO: None,
}

# 每板块送进 LLM 的候选数量。最终条数由第 6 步的 LLM 打分决定。
CANDIDATES_PER_SECTION = 15

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)  # 缺时间的条目排最后


def curate(state: ReportState) -> dict:
    """把 raw_items 压成候选池，写入 items。"""
    fresh = [i for i in _dedupe(state["raw_items"]) if _is_fresh(i)]

    candidates: list[Item] = []
    for section in Section:
        group = sorted(
            (i for i in fresh if i.section is section),
            key=_rank_key,
            reverse=True,  # 两种 key 都是「越大越靠前」
        )
        candidates += group[:CANDIDATES_PER_SECTION]

    return {"items": candidates}


def _dedupe(items: list[Item]) -> list[Item]:
    """按 URL 和标题各去一次重。

    URL 重复：同一个 GitHub 项目被「新星」「经典」两路查询同时命中。
    标题重复：同一条新闻被多家媒体报道，或 HN 转发了 arXiv 论文。
    """
    seen: set[str] = set()
    result = []
    for item in items:
        keys = (item.url.rstrip("/").lower(), _title_key(item.title))
        if any(k in seen for k in keys):
            continue
        seen.update(keys)
        result.append(item)
    return result


def _title_key(title: str) -> str:
    """标题归一化：只留小写字母和数字，抹掉标点与空格的差异。"""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def _is_fresh(item: Item) -> bool:
    """时间未知的一律保留——宁可多留，不要凭猜测丢数据。"""
    max_age = MAX_AGE_DAYS[item.section]
    if max_age is None or item.published_at is None:
        return True
    return item.published_at >= datetime.now(timezone.utc) - timedelta(days=max_age)


def _rank_key(item: Item) -> float:
    """排序依据：项目看 star 数，其余看发布时间。"""
    if item.section is Section.REPO:
        return item.extra.get("stars", 0)
    return (item.published_at or _EPOCH).timestamp()
