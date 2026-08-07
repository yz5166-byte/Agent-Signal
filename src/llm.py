"""LLM 客户端：全项目唯一初始化模型的地方。

走 AIHubMix（OpenAI 兼容接口），所以直接用 langchain-openai。
换模型、换供应商只改这一个文件，节点代码一行都不用动。
"""

import os

from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """温度默认调低：日报要的是稳定复现，不是创意发挥。"""
    return ChatOpenAI(
        model=os.environ["LLM_MODEL_ID"],
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
        temperature=temperature,
        timeout=180,
        # 默认只重试 2 次。实测本机代理在并发下会瞬断，
        # 提到 5 次（SDK 内置指数退避，累计约 15 秒）足以扛过抖动。
        max_retries=5,
    )
