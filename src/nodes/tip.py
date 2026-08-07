"""节点：每日 Agent 开发技巧（调 LLM）。

从当天精选出的内容里提炼一条能直接上手试的技巧。

关键设计：强制模型返回一个条目编号，技巧必须基于那条的具体内容。
不加这个约束，模型会输出「记得加重试机制」这类每天都成立、
读者一条都记不住的通用建议——问题不在 prompt 措辞，在于没有锚点。
"""

from pydantic import BaseModel, Field

from src.llm import get_llm
from src.state import ReportState

PROMPT = """你在为一份面向 AI 从业者的中文日报撰写「今日 Agent 开发技巧」栏目。

下面是今天日报里的全部条目。请挑一条作为切入点，
提炼出一个 Agent 开发者今天就能动手试的技巧。

要求：
- 必须基于所选条目的具体内容，不要写通用建议
- 正文用中文，150 字以内：先说清「什么场景下会遇到这个问题」，再给做法
- 做法如果能用代码或命令表达，就写进去，用 Markdown 代码块
- 代码必须是可以直接照抄的安全写法。若涉及执行模型生成的代码，
  给出沙箱或白名单方案，不要示范裸的 exec/eval

今天的条目：
{items}"""


class Tip(BaseModel):
    index: int = Field(description="作为切入点的条目编号")
    title: str = Field(description="技巧标题，一句话，20 字以内")
    body: str = Field(description="正文，中文 150 字以内，可含 Markdown 代码块")


def write_tip(state: ReportState) -> dict:
    """只喂标题和摘要，不喂全文——够模型判断了，没必要多付钱。

    失败就不出这个板块。compose 里 tip 本来就是可选的，
    少一个栏目远好过整份日报发不出去。
    """
    items = state["items"]
    if not items:
        return {"errors": ["技巧生成跳过：当天没有任何条目"]}

    try:
        result = (
            get_llm()
            .with_structured_output(Tip)
            .invoke(
                PROMPT.format(
                    items="\n".join(
                        f"[{n}] {i.title}\n    {i.summary}" for n, i in enumerate(items)
                    )
                )
            )
        )
    except Exception as e:
        return {"errors": [f"技巧生成失败：{type(e).__name__}"]}

    # 编号可能是模型编的，越界就退化成「没有延伸阅读」，而不是让整个节点崩掉
    ref = items[result.index] if 0 <= result.index < len(items) else None
    return {
        "tip": {
            "title": result.title,
            "body": result.body,
            "ref_title": ref.title if ref else "",
            "ref_url": ref.url if ref else "",
        }
    }
