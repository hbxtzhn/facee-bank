## 追问 1：在 FastAPI 中定义 def 路由和 async def 路由，底层的调度线程模型有何不同？

若写 async def，FastAPI 直接在主事件循环中运行该协程；若写普通 def，FastAPI 判定其可能含有同步阻塞代码，会自动将其扔到内置的外部线程池（ThreadPoolExecutor）中执行，防止阻塞主事件循环。
