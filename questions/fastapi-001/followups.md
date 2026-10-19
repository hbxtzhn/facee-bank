## 追问 1：def 与 async def 路由如何调度？

`async def` 路由在事件循环中执行，必须避免阻塞该线程。普通 `def` 路由及同步依赖由 Starlette/AnyIO 在线程池中执行，通常通过 `anyio.to_thread.run_sync` 调度；不能把它固定等同于某个 ThreadPoolExecutor 实例。自己在 async 路由里直接调用的普通工具函数不会因此自动转入线程池。

参考：[Starlette 线程池](https://www.starlette.dev/threadpool/)。
