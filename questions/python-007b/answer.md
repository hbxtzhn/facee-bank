## 1. 常见进程间通信（IPC）机制对比

| IPC 方式 | 底层机制 | 特点与适用场景 |
|---|---|---|
| **`Queue`** | 管道（Pipe）+ 锁 + 缓冲线程 | 适合多生产者-多消费者模型，API 简单易用 |
| **`Pipe`** | 操作系统全双工管道/套接字对 | 双向点对点通信，吞吐量和速度明显高于 Queue |
| **`Value` / `Array`** | 共享内存段（底层 C 原生类型） | 速度快，无需序列化，但只支持数字、布尔等基础标量和固定长度数组 |
| **`Manager`** | 独立的 Server 进程提供代理对象 | 支持跨进程操作字典、列表，但每次方法调用都要经过 IPC 代理，性能最慢 |
| **`shared_memory`** (3.8+) | 操作系统原生共享内存（shm） | **零拷贝（Zero-Copy）**，海量数据（NumPy/图片/张量）最佳解决方案 |

---

## 2. 传统 Queue 在传输海量数据时的致命瓶颈：pickle 序列化

当通过 `queue.put(big_data)` 发送一个 1GB 的数据集或图像矩阵时，内部必须经历：
1. **CPU 序列化**：发送方进程调用 `pickle.dumps()` 将对象在内存中完整打包为字节流（极其消耗 CPU 和耗费 1 倍额外内存）；
2. **内核空间拷贝**：字节流通过 OS Pipe 写入操作系统内核缓冲区；
3. **CPU 反序列化**：接收方进程从管道读出字节流并执行 `pickle.loads()` 重新构造一模一样的新对象。

**结果**：多核带来的并行收益被庞大的 CPU 序列化与内存频繁拷贝彻底抵消，甚至引发 OOM。

---

## 3. 破局之道：Python 3.8 原生共享内存（SharedMemory）

通过共享内存，多个进程可以直接映射同一块物理内存地址空间，**实现零拷贝秒级共享**：

```python
from multiprocessing import shared_memory
import numpy as np

# 进程 A：创建 1GB 的连续数组并放入共享内存
a = np.ones((1000, 1000, 250), dtype=np.float32)  # ~1GB 数据
shm = shared_memory.SharedMemory(create=True, size=a.nbytes)
# 将 numpy 数组直接映射到这块共享内存
b = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
b[:] = a[:]  # 填充数据
print("共享内存块名称:", shm.name)

# 进程 B（子进程）：无需序列化，直接通过名称秒级接入
existing_shm = shared_memory.SharedMemory(name=shm.name)
c = np.ndarray(a.shape, dtype=a.dtype, buffer=existing_shm.buf)
print("直接读取共享数据:", c[0, 0, 0])  # 零拷贝读取，无延迟！

# 用完后必须释放并清理
existing_shm.close()
shm.close()
shm.unlink()
```
