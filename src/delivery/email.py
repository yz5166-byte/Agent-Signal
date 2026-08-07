"""投递渠道：通过 SMTP 发送日报。

Gmail 需要「应用专用密码」，不是账号密码——
账号密码从 2022 年起已被禁止用于 SMTP 登录。
"""

import os
import smtplib
from email.message import EmailMessage

import markdown

_CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
     max-width:680px;margin:0 auto;padding:24px;line-height:1.7;color:#24292f}
a{color:#0969da;text-decoration:none}
h1{font-size:22px}
h2{font-size:17px;margin-top:36px;padding-bottom:6px;border-bottom:1px solid #d8dee4}
h3{font-size:15px}
blockquote{color:#656d76;border-left:3px solid #d8dee4;margin:0;padding-left:12px}
code{background:#f6f8fa;padding:2px 5px;border-radius:4px;font-size:13px}
pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow-x:auto}
pre code{background:none;padding:0}
em{color:#8c959f;font-size:13px;font-style:normal}
"""


def send(subject: str, body_md: str) -> None:
    """同时带纯文本和 HTML 两个版本，邮件客户端自己挑能渲染的那个。"""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["MAIL_TO"]
    msg.set_content(body_md)  # 纯文本兜底
    msg.add_alternative(_to_html(body_md), subtype="html")  # 能渲染就优先用这个

    with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)


def _to_html(body_md: str) -> str:
    body = markdown.markdown(body_md, extensions=["fenced_code"])
    return f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{body}</body></html>"
