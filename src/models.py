"""数据模型：定义全项目统一的「一条资讯」。

所有数据源抓回来的东西，最终都要归一化成这里的 Item，
后面的筛选、摘要、排版才能用同一套代码处理。
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Section(str, Enum):
    """日报的板块。每条 Item 属于且只属于一个板块。"""

    PAPER = "paper"  # 前沿论文
    REPO = "repo"  # 热门开源项目
    NEWS = "news"  # 行业新闻、市场与投资动态
    PRODUCT = "product"  # 产品发布、模型更新


class Item(BaseModel):
    """一条资讯。字段按「由哪个阶段填写」分成三组。"""

    # --- 第 1 组：抓取阶段填写（由 sources/ 里的各数据源负责）---
    section: Section
    title: str
    url: str
    source: str  # 具体出处，如 "arXiv" / "GitHub" / "TechCrunch"
    published_at: datetime | None = None
    raw_text: str = ""  # 原始摘要或描述，后面喂给 LLM
    extra: dict = Field(default_factory=dict)  # 各源特有字段，如 stars、作者

    # --- 第 2 组：精选阶段填写（由 nodes/curate.py 负责）---
    score: float = 0.0

    # --- 第 3 组：摘要阶段填写（由 nodes/summarize.py 负责）---
    summary: str = ""  # 一句话中文摘要
