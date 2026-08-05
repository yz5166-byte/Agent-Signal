"""网页服务：读取 output/ 下的 JSON 日报，提供可交互的浏览界面。

与流水线完全解耦——流水线只管产出文件，网页只管读文件。
启动：uvicorn web.app:app --reload
"""
