"""LangGraph 的 State：整张图的「共享记忆」。

每个节点读 State，返回一个 dict 去更新 State。
并行节点的返回值靠 reducer 合并，不会互相覆盖。
"""

import operator
from typing import Annotated, TypedDict

from src.models import Item


class ReportState(TypedDict, total=False):
    """整条流水线共享的状态。

    字段按「哪个阶段写它」从上往下排列，读一遍就是数据的流动顺序。
    """

    # [入口] 本次运行的日期，如 "2026-08-06"
    run_date: str

    # [fetch] 四个数据源【并行】抓取，结果靠 operator.add 累加进同一个列表
    # list[Item]: 这个字段本身的数据类型
    # operator.add: 给 LangGraph 的合并规则（reducer）
    raw_items: Annotated[list[Item], operator.add]

    # [curate] 去重打分后的精选结果。没有 reducer，所以是【整体替换】
    items: list[Item]

    # [tip] 当日 Agent 开发技巧，是一段生成的文字，不属于任何 Item
    tip: str

    # [compose] 两种成品格式
    report_md: str  # 给邮件正文和 output/*.md 归档
    report_json: dict  # 给网页读取的结构化数据

    # [任何阶段] 出错信息，同样累加，用于「单个源挂了不影响整体」
    errors: Annotated[list[str], operator.add]
