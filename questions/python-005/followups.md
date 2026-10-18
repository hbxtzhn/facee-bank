## 追问 1：在 async def 函数中调用了 time.sleep() 会发生什么后果？

time.sleep() 是阻塞式的同步调用，它会霸占线程 CPU 并直接挂起整个操作系统线程，导致所属事件循环被彻底卡死，期间所有并发的协程都无法得到调度。在异步代码中必须使用 await asyncio.sleep()，或者使用 asyncio.to_thread() 将阻塞操作抛到外部线程池。
