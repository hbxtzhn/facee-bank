## 追问 1：如果在 with 块内部发生了异常，__exit__ 如何决定是否向上抛出？

__exit__ 接收 (exc_type, exc_val, exc_tb) 三个参数。如果 __exit__ 返回 True，Python 会吞掉该异常，外部代码继续正常往下执行；若返回 False 或 None，Python 会在退出 __exit__ 后把该异常原样重新向上抛出。

## 追问 2：在异步编程中，async with 的底层协议有什么变化？

异步上下文管理器必须实现 __aenter__(self) 和 __aexit__(self, exc_type, exc_val, exc_tb)，两者都是返回协程的异步方法，使用 async with 触发，常见于 aiohttp 客户端会话和 asyncpg 数据库连接事务。
