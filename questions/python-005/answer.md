## 1. 事件循环、协程与 Task

调用 `async def` 函数得到协程对象，不代表已开始并发运行。通过 `await` 执行它，或通过 `asyncio.create_task()` 将它包装为 Task 交给事件循环调度。

同一事件循环线程内，Task 协作式交替执行；遇到需要等待的异步操作时挂起，让其他就绪任务运行。**不是每个 await 都必然切换任务**：被等待对象若已完成，可以立即继续。

网络事件常由 Unix 的 selector（如 epoll/kqueue）驱动；Windows 默认 ProactorEventLoop 使用 IOCP，不能把所有平台都称为同一种 selector 实现。

## 2. 与线程的边界

协程切换通常无需为每个任务切换操作系统线程，但仍有调度和对象管理成本，不能声称没有切换开销或固定是“纳秒级”。单循环也不等于没有竞态，例如读取余额后 `await`，恢复时其他任务可能已修改余额，需要 `asyncio.Lock` 保护业务不变量。

`time.sleep()`、同步网络调用和长时间 CPU 计算会阻塞事件循环线程。阻塞 I/O 可以用异步接口或 `asyncio.to_thread()`；纯 Python CPU 计算在启用 GIL 时通常应考虑进程池。`time.sleep()` 的问题是挂起线程，**不是持续霸占 CPU 计算**。

参考：[asyncio Task](https://docs.python.org/3.14/library/asyncio-task.html)、[事件循环](https://docs.python.org/3.14/library/asyncio-eventloop.html)。
