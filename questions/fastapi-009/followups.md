## 追问 1：如果一个 BackgroundTask 内部抛出了未捕获的异常，会导致主响应报错吗？

不会。因为在 BackgroundTask 真正执行前，HTTP 响应早已通过 ASGI 通道成功发送给客户端了。后台任务的异常只会在服务端控制台打印错误堆栈，客户端不会收到 500 报错。

## 追问 2：如果在 BackgroundTasks 中传入了一个同步 def 函数，FastAPI 会怎样执行它？

FastAPI 内部会自动将其扔到 Starlette 的线程池（ThreadPoolExecutor）中并发执行，不会阻塞主事件循环；如果是 async def 函数，则作为独立协程在当前事件循环中直接调用。
