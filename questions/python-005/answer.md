## 1. 核心架构要素

Python 的异步编程由标准库 `asyncio` 提供，属于**单线程协作式多任务并发**模型：

1. **事件循环（Event Loop）**：核心调度引擎。死循环轮询并调度注册到循环中的就绪回调与任务。
2. **I/O 多路复用（Selectors）**：底层依赖 Linux `epoll`、macOS `kqueue` 或 Windows `IOCP`。当网络 Socket 阻塞时向内核注册文件描述符事件，非阻塞等待就绪通知。
3. **协程对象（Coroutine）**：由 `async def` 定义的函数调用时返回。协程对象实现了 `__await__` 协议，可在遇到 I/O 时通过 `await` 主动让出 CPU 控制权。
4. **任务（Task）**：通过 `asyncio.create_task()` 将协程包装为 Task，Task 会被自动注册进事件循环中并发调度执行。

---

## 2. 调度执行流程

```text
[调用 async def] ──> 生成 Coroutine
       │
[asyncio.create_task] ──> 封装为 Task ──> 注册到 Event Loop 运行队列
                                                │
                                  ┌─────────────┴─────────────┐
                                  ▼                           ▼
                           当前 Task 执行             其他就绪 Task 轮流执行
                                  │
                             遇到 await I/O
                                  │
                           向 Selector 注册事件并让出 CPU
                                  │
                           底层 epoll 监听就绪
                                  │
                           唤醒并放入就绪队列重新执行
```

---

## 3. 面试高频对比：asyncio vs 多线程

- **无上下文切换代价**：协程切换是用户态函数调度的开销（纳秒级），线程切换涉及内核上下文切换（微秒级）。
- **无数据竞态（Race Condition）**：单线程运行，同一时刻只有一段代码在跑。只要两段逻辑之间没有 `await` 让出控制权，操作就是天然原子的，省去了大量互斥锁开销。
- **缺点**：不能包含任何 CPU 密集阻塞或同步阻塞调用（如 `requests.get`、`time.sleep`），否则一卡卡全家。
