"""各数据源共用的小工具。

命名约定：本目录下带下划线前缀的文件是助手，不带的才是数据源（都有 fetch()）。
"""

import html
import re
from datetime import datetime, timezone

import httpx

USER_AGENT = "ai-edge-bot/0.1 (+https://github.com/yz5166-byte/ai-edge-bot)"


def http_get(url: str, *, params: dict | None = None, headers: dict | None = None) -> httpx.Response:
    """带 UA 和超时的 GET。非 2xx 直接抛异常，别让错误页伪装成空数据。"""
    resp = httpx.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT, **(headers or {})},
        timeout=30,
        follow_redirects=True,
    )
    resp.raise_for_status()
    return resp


def clean_text(text: str) -> str:
    """去掉 HTML 标签和多余空白——RSS 摘要里常混着 <p> 和 &amp;。"""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def to_datetime(parsed) -> datetime | None:
    """feedparser 给的 UTC 时间元组 -> 带时区的 datetime。"""
    return datetime(*parsed[:6], tzinfo=timezone.utc) if parsed else None
