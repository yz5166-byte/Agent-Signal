"""程序入口：编译图 -> 跑一次 -> 结束。

日常运行：python -m src.main
成品写在 output/ 目录，投递情况由 deliver 节点打印。
"""

from datetime import date

from src.graph import build_graph
from src.state import ReportState


def main() -> None:
    initial_state: ReportState = {"run_date": date.today().isoformat()}
    build_graph().invoke(initial_state)


if __name__ == "__main__":
    main()
