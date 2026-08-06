"""项目包初始化：统一加载 .env。

放这里是因为项目所有模块都在 src 包下，任何入口（main.py、单独跑某个 source）
都会先触发它，只需写一次。路径写死成项目根目录，不受「从哪个目录运行」影响。
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
