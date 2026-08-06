"""图的组装：只负责「把节点连起来」，不含任何业务逻辑。

看这一个文件，就能看懂整条流水线的形状。
"""

from langgraph.graph import END, START, StateGraph

from src.nodes.fetch import fetch_papers
from src.state import ReportState


def build_graph():
    """把节点连成图，并编译成可运行对象。

    当前形状：START -> fetch_papers -> END
    后续步骤会在这里继续加节点和边，其他文件不用动。
    """
    graph = StateGraph(ReportState)  # 告诉 LangGraph：这张图共享哪份 State

    # 1) 注册节点："名字" -> 干活的函数
    graph.add_node("fetch_papers", fetch_papers)

    # 2) 连边：谁先谁后
    graph.add_edge(START, "fetch_papers")
    graph.add_edge("fetch_papers", END)

    # 3) 编译：检查图是否合法（有无孤立节点、环等），产出可运行对象
    return graph.compile()
