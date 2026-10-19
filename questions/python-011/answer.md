## 1. 上下文管理协议（Context Management Protocol）

任何实现了 `__enter__` 和 `__exit__` 方法的对象都被称为上下文管理器：

```python
class ManagedResource:
    def __enter__(self):
        print("1. 获取资源")
        return self  # 返回值将绑定给 with ... as target 的 target

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("3. 清理释放资源")
        if exc_type is not None:
            print(f"捕获到异常: {exc_val}")
            return True  # ★ 返回 True 表示吞并异常，阻止其继续扩散
        return False
```

### 执行时序图：
```text
with 块的 __enter__ 成功后：
with Resource() as r:
   │
   ├──> 调用 Resource.__enter__() -> 得到 r
   │
   ├──> 执行 with 代码块内部语句
   │
   └──> 无论代码块是正常结束还是抛出异常
        必定调用 Resource.__exit__(exc_type, exc_val, exc_tb)
```

---

## 2. 使用 @contextlib.contextmanager 极速实现

手动写一个类并实现两个方法略显啰嗦，标准库提供了 `@contextlib.contextmanager` 装饰器，利用生成器把准备工作与收尾逻辑写在同一个函数内：

```python
import contextlib
import time

@contextlib.contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield start  # yield 之前相当于 __enter__，产出的值赋给 as 后面的变量
    finally:
        # yield 之后（在 finally 块中）相当于 __exit__，确保发生异常也会执行清理
        cost = time.perf_counter() - start
        print(f"[{label}] 耗时: {cost:.4f}s")

# 实战调用
with timer("大数据集计算") as t:
    total = sum(i * i for i in range(1000000))
# 耗时由实际环境决定，不把示例时间当成性能保证。
```
