## 追问 1：fork、spawn 与 forkserver 如何选择？

默认值取决于平台和版本：Windows 使用 spawn，macOS 从 3.8 起默认 spawn；Python 3.14 在支持 forkserver 的 POSIX 平台将默认方式改为 forkserver，fork 已不再是任何平台的默认方式。

fork 会继承父进程状态，多线程父进程中可能继承无法正常释放的锁或不安全连接。应使用 `multiprocessing.get_context()` 选定业务与库支持的上下文；采用 spawn/forkserver 时关注可 pickle 性、导入副作用以及 `if __name__ == "__main__"` 入口保护，不能用一条跨版本的“Linux 默认 fork”代替判断。

## 追问 2：与 queue.Queue 有何区别？

queue.Queue 在线程间共享对象引用。multiprocessing.Queue 面向进程，通过 IPC 传递对象，通常包含 pickle 与 feeder 线程，不能把进程队列当成共享 Python 对象的引用容器。
