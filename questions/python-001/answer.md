## 1. 先限定解释器与构建方式

这里讨论 **启用 GIL 的 CPython**。GIL 是保护解释器内部状态的锁；同一解释器在一个时刻通常只有一个线程执行 Python 字节码。它简化了对象引用计数与部分 C API 的并发访问，但不等于所有 Python 实现都必须有 GIL。

Python 3.13 引入可选的实验性 free-threaded 构建，3.14 进一步正式支持这种构建；默认构建仍启用 GIL。自由线程构建、运行时设置和 C 扩展兼容性需分别确认，不能仅凭版本号认定没有 GIL。

## 2. 对并发的影响

| 任务 | 启用 GIL 时的典型表现 | 选择依据 |
|---|---|---|
| 纯 Python CPU 密集计算 | 多线程不能据此获得多核字节码并行，锁竞争可能增加开销 | 可考虑进程池、释放 GIL 的原生实现或兼容的自由线程构建 |
| 网络等阻塞 I/O | 支持释放 GIL 的阻塞调用允许其他线程执行 | 可使用线程池；若库提供异步接口，也可用 asyncio |
| NumPy 等原生计算 | 部分操作会释放 GIL，部分不会 | 取决于具体操作、数据类型和底层库，不能把矩阵运算一概归为不适合线程 |

## 3. GIL 不是业务线程安全保证

读、计算、写的复合逻辑可能跨多个操作。共享余额、缓存或容器的业务不变量仍可能需要锁。协程也可能在 `await` 之间发生任务交错，需要时应使用 `asyncio.Lock`。

参考：[自由线程构建](https://docs.python.org/3.14/howto/free-threading-python.html)、[threading 的 GIL 说明](https://docs.python.org/3.14/library/threading.html#gil-and-performance-considerations)。
