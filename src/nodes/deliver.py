"""节点：投递。整条流水线里唯一产生「副作用」的一步。

本节点只决定「投到哪些渠道」，怎么投在 delivery/ 里实现。
也是唯一不修改 State 的节点——它的产出在程序之外（磁盘、邮箱）。
"""

import os

from src.delivery import email, files
from src.state import ReportState


def deliver(state: ReportState) -> dict:
    md = files.save_markdown(state["run_date"], state["report_md"])
    js = files.save_json(state["run_date"], state["report_json"])
    print(f"[deliver] 已写入 {md.name} 和 {js.name}")

    # 没配 SMTP 也能正常跑完，只是不发信——本地调试时不必每次都发一封
    if os.getenv("SMTP_HOST"):
        email.send(f"AI Edge 日报 · {state['run_date']}", state["report_md"])
        print(f"[deliver] 已发送邮件至 {os.environ['MAIL_TO']}")
    else:
        print("[deliver] 未配置 SMTP_HOST，跳过邮件")

    return {}  # 不改 State
