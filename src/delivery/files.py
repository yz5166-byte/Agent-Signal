"""投递渠道：写到本地 output/ 目录。

Markdown 给邮件正文和归档，JSON 给网页读取。
两者共用输出目录，所以放在同一个文件里，而不是各拆一个。
"""

import json
from pathlib import Path

# 从本文件位置往上两层就是项目根，不依赖当前工作目录
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"


def save_markdown(run_date: str, content: str) -> Path:
    return _write(f"{run_date}.md", content)


def save_json(run_date: str, data: dict) -> Path:
    return _write(f"{run_date}.json", json.dumps(data, ensure_ascii=False, indent=2))


def _write(name: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(content, encoding="utf-8")
    return path
