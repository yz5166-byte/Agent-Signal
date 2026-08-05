"""LangGraph 的 State：整张图的「共享记忆」。

每个节点读 State，返回一个 dict 去更新 State。
并行节点的返回值靠 reducer 合并，不会互相覆盖。
"""
