## 追问 1：在 Linux 生产环境中，多进程的启动方式（fork vs spawn）如何选择？

默认的 fork 速度快且写时复制（COW），但如果父进程已经创建了线程池、数据库连接池或 SSL 上下文，fork 出的子进程很容易死锁或共享句柄产生混乱。Python 3.8+ 强烈推荐在生产或多线程混合场景下使用 multiprocessing.set_start_method('spawn')，保证子进程环境完全干净。

## 追问 2：multiprocessing.Queue 和 queue.Queue 有什么区别？

queue.Queue 是线程安全的队列，仅在同一个进程内的多线程之间共享内存引用；而 multiprocessing.Queue 是跨进程的，底层基于 Pipe（管道）+ 操作系统锁 + 后台专门的 Feeder 线程 + pickle 序列化，开销显著大于线程队列。
