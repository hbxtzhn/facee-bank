## 1. 什么是 GIL？

**GIL（Global Interpreter Lock，全局解释器锁）** 是 CPython 解释器中用于保护解释器内部状态的互斥锁（Mutex）。
它确保在任何时刻，**只有一个系统原生线程能够执行 Python 字节码**。

由于早期 CPython 内存管理采用了非线程安全的引用计数（Reference Counting）机制，引入 GIL 能够极简地避免并发修改引用计数的竞态条件，并且单线程执行时几乎没有加锁开销，还能方便集成非线程安全的 C 语言扩展库。

---

## 2. GIL 对并发的影响

| 任务类型 | 多线程表现 | 原因 | 应对策略 |
|---|---|---|---|
| **CPU 密集型** (如矩阵计算、音视频处理、复杂算法) | **性能不升反降** | 多个线程不仅无法利用多核并行，反而在 GIL 释放与重新竞争中产生大量的线程上下文切换与锁争用开销 | 使用 `multiprocessing` 多进程充分利用多核；或使用 NumPy / Rust / C++ 扩展并在底层释放 GIL |
| **I/O 密集型** (如 Web 请求、数据库查询、文件读写) | **显著提升吞吐** | 当线程发起系统调用（如 socket 等待）时，CPython 会主动释放 GIL，其他线程可继续执行字节码 | 使用多线程（`threading` / `ThreadPoolExecutor`），或采用更轻量高效的单线程协程（`asyncio`） |

---

## 3. 常见避坑与解法总结

1. **CPU 密集型不要用 Python 原生多线程**：优先选择 `multiprocessing.Pool` 或 `concurrent.futures.ProcessPoolExecutor`。
2. **底层计算库绕过 GIL**：例如 NumPy 的数组运算、PyTorch 的张量操作以及 Polars 等在底层 C/C++/Rust 层面执行计算时，均会显式调用 `Py_BEGIN_ALLOW_THREADS` 临时解开 GIL，此时多线程可真正跑满全核。
3. **协程更优**：在现代 Python Web（如 FastAPI、aiohttp）中，I/O 场景通常首选基于事件循环的单线程 `asyncio`，避免多线程内存开销与竞态问题。
