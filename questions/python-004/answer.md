## 1. 装饰器的本质

装饰器是作用于函数或类的可调用对象；常见函数装饰器接受目标函数并返回包装函数或其他替代对象。
`@decorator` 语法糖是在模块加载并定义函数时（**导入时/定义时执行，而非调用时执行**）进行的等价转换：

```python
@my_decorator
def foo():
    pass

# 等价于：
foo = my_decorator(foo)
```

---

## 2. 带参数的装饰器结构

如果装饰器本身需要传参（例如 `@retry(max_times=3)`），常见函数写法使用三层嵌套（也可用可调用类、partial 等实现，并非语法强制要求）：
- 最外层：接收装饰器参数；
- 第二层：接收被装饰的目标函数；
- 最内层（wrapper）：接收被装饰函数运行时的实际入参 `*args, **kwargs`。

### 通用标准模板：
```python
import functools
import time

def timed_retry(max_attempts: int = 3, delay: float = 1.0):
    """同步函数的重试与耗时统计；异步函数需另写 await 版本。"""
    if max_attempts < 1 or delay < 0:
        raise ValueError("max_attempts 必须至少为 1，delay 不能为负")
    def decorator(func):
        @functools.wraps(func)  # ★ 保留原函数的 __name__ 和 __doc__
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    cost = time.perf_counter() - start
                    print(f"[{func.__name__}] 耗时 {cost:.4f}s")
                    return result
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

# 使用示例
@timed_retry(max_attempts=3, delay=0.5)
def fetch_api(url: str):
    return "ok"
```
