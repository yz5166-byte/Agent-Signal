"""节点：打分挑选 + 中文摘要（调 LLM）。

每个板块一次调用：把候选喂给模型，让它挑出最值得看的 N 条并各写一句中文摘要。
挑选和摘要合在同一次调用里——模型读一遍就能同时做两件事，没必要分两次付费。
"""

from pydantic import BaseModel, Field

from src.llm import get_llm
from src.models import SECTION_NAMES, Item, Section
from src.state import ReportState

# 每个板块最终保留几条
FINAL_COUNT = {
    Section.PAPER: 5,
    Section.REPO: 5,
    Section.NEWS: 6,
    Section.PRODUCT: 3,
}

# 每个板块的挑选标准，直接拼进 prompt
CRITERIA = {
    Section.PAPER: "优先 Agent、LLM 推理、工具调用、多智能体方向；排除与 AI 应用无关的纯理论工作",
    Section.REPO: "优先真正能上手用、用途明确的项目；排除玩具项目和纯资料清单",
    Section.NEWS: "优先重大发布、融资、监管等有实际影响的事件；排除蹭热度的边角消息",
    Section.PRODUCT: "优先新模型、新产品、新能力的正式发布；排除纯公关性质的软文",
}

PROMPT = """你是一份面向 AI 从业者的中文日报的主编，正在编「{section}」板块。

下面是 {n} 条候选，请挑出今天最值得读者知道的 {k} 条。

挑选标准：{criteria}
评分：1-10 分，表示这条有多值得读者今天看到。
摘要：一句话中文，40 字以内，说清「做了什么、为什么值得注意」，不要复述标题。

候选：
{candidates}"""


class Pick(BaseModel):
    index: int = Field(description="候选的编号")
    score: int = Field(description="1-10 分，越高越值得看")
    summary: str = Field(description="一句话中文摘要，40 字以内")


class Selection(BaseModel):
    picks: list[Pick]


def summarize(state: ReportState) -> dict:
    """逐板块挑选并写摘要，结果整体替换 state["items"]。"""
    llm = get_llm().with_structured_output(Selection)
    selected: list[Item] = []
    for section, k in FINAL_COUNT.items():
        group = [i for i in state["items"] if i.section is section]
        if group:
            selected += _pick(llm, section, group, k)
    return {"items": selected}


def _pick(llm, section: Section, group: list[Item], k: int) -> list[Item]:
    """一次调用完成「挑选 + 打分 + 摘要」，再按编号映射回 Item。"""
    result = llm.invoke(
        PROMPT.format(
            section=SECTION_NAMES[section],
            n=len(group),
            k=k,
            criteria=CRITERIA[section],
            candidates="\n".join(
                f"[{n}] {i.title}\n    {i.raw_text[:300]}" for n, i in enumerate(group)
            ),
        )
    )

    picked, seen = [], set()
    for p in result.picks:
        # 模型可能编出不存在的编号，或把同一条挑两次，必须校验
        if p.index in seen or not 0 <= p.index < len(group):
            continue
        seen.add(p.index)
        item = group[p.index]
        item.score, item.summary = p.score, p.summary
        picked.append(item)

    picked.sort(key=lambda i: i.score, reverse=True)
    return picked[:k]
