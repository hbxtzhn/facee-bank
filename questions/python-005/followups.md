## 追问 1：在 async def 函数中调用了 time.sleep() 会发生什么后果？

time.sleep() 会挂起当前操作系统线程，并阻塞该线程上的事件循环；它并不持续占用 CPU 计算，但其他协程仍无法在这条线程上调度。异步代码应使用 await asyncio.sleep()，或用 asyncio.to_thread() 执行阻塞 I/O；CPU 密集计算还需考虑 GIL 与进程池。
