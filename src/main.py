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
    raw, items = state.get("raw_items", []), state.get("items", [])
    print(f"运行日期 {state['run_date']}   抓取 {len(raw)} 条 -> 候选 {len(items)} 条")
    for section in Section:
        group = [i for i in items if i.section is section]
        raw_n = len([i for i in raw if i.section is section])
        print(f"\n── {section.value}（{raw_n} -> {len(group)}）")
        for it in group:
            print(f"   [{it.source:16}] {it.title[:62]}")


if __name__ == "__main__":
    main()
