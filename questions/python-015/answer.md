## 1. 生产环境四大常见“内存泄漏”根源

严格来说，Python 属于自动垃圾回收语言，绝大多数所谓的“内存泄漏”都是**无意间持有了长生命周期的强引用**：

1. **全局容器无节制增长**：
   模块级全局变量 `cache = {}` 或全局 `list` 不断追加数据，缺少最大容量上限（未设置 LRU 过期淘汰机制）。
2. **闭包或回调函数意外保留外层引用**：
   在事件监听器、信号注册机制中绑定了实例方法，未显式解绑注销，导致整个类实例无法被 GC 销毁。
3. **重写了 `__del__` 的循环引用**（早期版本遗留或死锁资源持有）。
4. **C/C++ 扩展底层泄漏**：
   调用 OpenCV、NumPy、Cython 等底层第三方库时，在底层 C 申请的 `malloc` 内存没有显式 `free`，Python 垃圾回收器完全无法感知。

---

## 2. 使用 tracemalloc 实战精确定位

Python 3.4+ 标准库自带了 **`tracemalloc`**，能拦截每个对象的内存分配并记录当时的完整调用栈，性能损耗小，是排查内存问题的官方核武器：

```python
import tracemalloc
import time

# 1. 开启内存追踪
tracemalloc.start()

# 2. 拍摄第一个基准快照
snapshot1 = tracemalloc.take_snapshot()

# 模拟业务运行过程中的内存增长
leaked_data = []
for i in range(100000):
    leaked_data.append(f"leak-item-{i}")

# 3. 拍摄第二个快照
snapshot2 = tracemalloc.take_snapshot()

# 4. 对比两个快照，按代码行过滤出内存增量最大的前 3 行
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

print("=== 内存净增量 Top 3 代码行 ===")
for stat in top_stats[:3]:
    print(stat)
```

### 控制台输出示例：
```text
=== 内存净增量 Top 3 代码行 ===
/app/main.py:12: size=8203 KiB (+8203 KiB), count=100001 (+100001)
```
- 直接精确定位到具体的代码文件路径和行号（`main.py:12`）；
- 清楚显示在两次快照间隔期净增长了 `8.2 MB`，新创建了 `100001` 个对象，排障一目了然。
