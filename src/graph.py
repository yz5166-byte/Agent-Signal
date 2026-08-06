"""图的组装：只负责「把节点连起来」，不含任何业务逻辑。

看这一个文件，就能看懂整条流水线的形状。
"""

from langgraph.graph import END, START, StateGraph

from src.nodes.fetch import fetch_blogs, fetch_news, fetch_papers, fetch_repos
from src.state import ReportState

FETCH_NODES = {
    "fetch_papers": fetch_papers,
    "fetch_repos": fetch_repos,
    "fetch_news": fetch_news,
    "fetch_blogs": fetch_blogs,
}


def build_graph():
    """把节点连成图，并编译成可运行对象。

    当前形状：       ┌→ fetch_papers ─┐
              START ─┼→ fetch_repos  ─┼→ END
                     ├→ fetch_news   ─┤
                     └→ fetch_blogs  ─┘

    四条边都从 START 出发 = 四个节点并行执行，
    结果靠 raw_items 上的 operator.add 自动合并（不需要任何汇总代码）。
    """
    graph = StateGraph(ReportState)  # 告诉 LangGraph：这张图共享哪份 State

    for name, node in FETCH_NODES.items():
        graph.add_node(name, node)
        graph.add_edge(START, name)  # 都从 START 出发 => 并行
        graph.add_edge(name, END)

    return graph.compile()  # 编译时检查图是否合法，产出可运行对象
