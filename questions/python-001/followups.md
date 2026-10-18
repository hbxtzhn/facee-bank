## 追问 1：Python 3.12/3.13 的自由线程（No-GIL / Free-threaded）目前进展如何？

PEP 703 引入了在构建 CPython 时禁用 GIL 的选项（--disable-gil）。在 Python 3.13 中作为实验性特性发布（free-threaded 模式），通过细粒度锁、偏向引用计数（mimalloc）来替代全局大锁。对于 CPU 密集型纯 Python 代码的多线程运行速度带来巨大提升，但现有 C 扩展需要重新适配编译。

## 追问 2：为什么 I/O 密集型任务下 Python 多线程依然有效？

在进行网络请求、磁盘读写或 time.sleep 等阻塞型 I/O 操作时，CPython 会在调用底层 C 系统调用前主动释放 GIL，待 I/O 数据就绪返回后再重新竞争 GIL。因此多个 I/O 线程可以真正并发等待，从而隐藏等待延迟。
