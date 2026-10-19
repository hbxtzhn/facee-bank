## 1. 进程间通信的选择

| 机制 | 适用方式 | 代价 |
|---|---|---|
| Queue | 多生产者、多消费者传递对象 | 通常经 pickle、管道和后台 feeder 线程 |
| Pipe | 点对点传递消息 | 双工管道/连接；性能依消息与同步方式而异 |
| Value / Array | 共享固定类型标量或数组 | 共享内存，复合读写仍需同步 |
| Manager | 通过服务进程代理字典、列表等对象 | 代理调用与序列化开销 |
| shared_memory | 多进程共享连续字节区域 | 生命周期与同步需自行管理 |

## 2. 大对象瓶颈与共享内存边界

普通 Queue 传对象通常包含序列化、传输和反序列化，可能增加 CPU、内存峰值与复制开销；具体倍数不是固定值。共享内存允许多个进程映射同一数据区域，避免每次通过 Queue 复制整个数据；**初始化仍可能有一次复制，元数据仍需传递，写入仍需同步**。

下面是同一进程演示两次映射的小型可运行示例。实际跨进程时须传递名称和有效数据长度（数组还需 shape、dtype），管理者在全部使用者退出后 unlink。分配或附加映射的可见大小可能按系统内存页取整，不能把整个缓冲区的长度当成业务数据长度。

```python
from multiprocessing import shared_memory

payload = b"Face"
length = len(payload)
owner = shared_memory.SharedMemory(create=True, size=length)
reader = None
try:
    owner.buf[:length] = payload
    reader = shared_memory.SharedMemory(name=owner.name)
    assert bytes(reader.buf[:length]) == payload
finally:
    if reader is not None:
        reader.close()
    owner.close()
    owner.unlink()
```

持有 memoryview 或 NumPy 视图时先释放视图再关闭映射。`close()` 关闭当前句柄，`unlink()` 负责删除共享内存对象；Windows 的回收规则与 POSIX 不同，不能让各消费者随意提前 unlink。

参考：[multiprocessing](https://docs.python.org/3.14/library/multiprocessing.html)、[shared_memory](https://docs.python.org/3.14/library/multiprocessing.shared_memory.html)。
