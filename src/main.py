"""程序入口：编译图 -> 跑一次 -> 打印结果。

日常运行：python -m src.main
"""

from datetime import date

from src.graph import build_graph
from src.models import Section
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
    print(f"运行日期 {state['run_date']}   抓取总数 {len(items)}")
    for section in Section:
        group = [i for i in items if i.section is section]
        print(f"\n── {section.value}（{len(group)} 条）")
        for it in group[:3]:
            print(f"   [{it.source:16}] {it.title[:62]}")
        if len(group) > 3:
            print(f"   ... 其余 {len(group) - 3} 条")


if __name__ == "__main__":
    main()
