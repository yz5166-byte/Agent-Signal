"""图的组装：只负责「把节点连起来」，不含任何业务逻辑。

看这一个文件，就能看懂整条流水线的形状。
"""

from langgraph.graph import END, START, StateGraph

from src.nodes.compose import compose
from src.nodes.curate import curate
from src.nodes.deliver import deliver
from src.nodes.fetch import fetch_blogs, fetch_news, fetch_papers, fetch_repos
from src.nodes.summarize import summarize
from src.nodes.tip import write_tip
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
              START ─┼→ fetch_repos  ─┼→ curate → summarize → tip → compose → deliver → END
                     ├→ fetch_news   ─┤
                     └→ fetch_blogs  ─┘
                                          （curate 之后全部串行）

    出：四条边都从 START 出发 = 四个节点并行执行。
    合：四条边都汇入 curate = LangGraph 会等四路全部跑完才启动 curate，
        结果靠 raw_items 上的 operator.add 自动合并（不需要任何汇总代码）。
    """
    graph = StateGraph(ReportState)  # 告诉 LangGraph：这张图共享哪份 State

    for name, node in FETCH_NODES.items():
        graph.add_node(name, node)
        graph.add_edge(START, name)  # 并行出发
        graph.add_edge(name, "curate")  # 汇入同一个节点

    graph.add_node("curate", curate)
    graph.add_node("summarize", summarize)
    graph.add_node("tip", write_tip)
    graph.add_node("compose", compose)
    graph.add_edge("curate", "summarize")
    graph.add_edge("summarize", "tip")  # tip 要读 summarize 挑出的条目
    graph.add_node("deliver", deliver)
    graph.add_edge("tip", "compose")
    graph.add_edge("compose", "deliver")
    graph.add_edge("deliver", END)

    return graph.compile()  # 编译时检查图是否合法，产出可运行对象
