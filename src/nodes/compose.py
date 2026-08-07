"""节点：排版。把 State 里的内容拼成一份分板块的中文日报。

产出两种格式：Markdown（给邮件和归档）与 JSON（给网页）。
两者内容相同、形态不同，所以只分一次组，各自渲染。
"""

from src.models import SECTION_NAMES, Item, Section
from src.state import ReportState


def compose(state: ReportState) -> dict:
    """把精选结果排版成两种成品格式。"""
    groups: dict[Section, list[Item]] = {}
    for section in Section:
        group = [i for i in state["items"] if i.section is section]
        if group:  # 空板块不出现在日报里，而不是留一个空标题
            groups[section] = group

    return {
        "report_md": _to_markdown(state, groups),
        "report_json": _to_json(state, groups),
    }


def _to_markdown(state: ReportState, groups: dict[Section, list[Item]]) -> str:
    """给邮件正文和 output/*.md 归档用。"""
    total = sum(len(g) for g in groups.values())
    parts = [f"# AI Edge 日报 · {state['run_date']}", "", f"> 今日精选 {total} 条", ""]

    for section, group in groups.items():
        parts += [f"## {SECTION_NAMES[section]}", ""]
        for item in group:
            parts += [
                f"**[{item.title}]({item.url})**",
                "",
                item.summary,
                "",
                f"*{_meta(item)}*",
                "",
            ]

    # 技巧是对当天内容的提炼，放在最后当作「今日一学」
    if state.get("tip"):
        parts += ["## 今日 Agent 开发技巧", "", state["tip"], ""]

    return "\n".join(parts)


def _to_json(state: ReportState, groups: dict[Section, list[Item]]) -> dict:
    """给网页读取用。Item 交给 Pydantic 序列化，datetime 会自动转成字符串。"""
    return {
        "date": state["run_date"],
        "tip": state.get("tip", ""),
        "sections": [
            {
                "key": section.value,
                "name": SECTION_NAMES[section],
                "items": [item.model_dump(mode="json") for item in group],
            }
            for section, group in groups.items()
        ],
    }


def _meta(item: Item) -> str:
    """每条底部的补充信息。各板块该显示什么不一样，差异只集中在这里。"""
    if item.section is Section.REPO:
        return f"{item.source} · ★{item.extra['stars']:,} · {item.extra['language'] or '—'}"
    if item.published_at:
        return f"{item.source} · {item.published_at:%m-%d}"
    return item.source
