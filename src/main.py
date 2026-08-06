"""程序入口：编译图 -> 跑一次 -> 打印结果。

日常运行：python -m src.main
"""

from datetime import date

from src.graph import build_graph
from src.state import ReportState


def main() -> None:
    app = build_graph()

    # 初始 State：只填入口该填的字段，其余交给各节点
    initial_state: ReportState = {"run_date": date.today().isoformat()}

    final_state = app.invoke(initial_state)  # 跑完整张图，返回最终 State
    _preview(final_state)


def _preview(state: ReportState) -> None:
    """临时的结果预览。第 8 步接上 deliver 节点后会删掉。"""
    items = state.get("raw_items", [])
    print(f"运行日期: {state['run_date']}")
    print(f"抓取条数: {len(items)}\n")
    for i, item in enumerate(items[:5], 1):
        print(f"[{i}] ({item.section.value}) {item.title[:70]}")
    if len(items) > 5:
        print(f"... 其余 {len(items) - 5} 条略")


if __name__ == "__main__":
    main()
