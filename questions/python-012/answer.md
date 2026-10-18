## 1. 核心区别一览

| 方法 | 触发时机 | 默认行为 | 危险性 |
|---|---|---|---|
| **`__getattribute__`** | **每次访问属性时无条件最先被调用**（无论属性是否存在） | `object` 底层默认实现，负责查找 `__dict__`、描述符、类变量等 | 极高（内部直接访问属性极易死循环） |
| **`__getattr__`** | **只有当常规查找完全找不到属性时**（抛出 AttributeError 前夕）才被调用 | 兜底保底机制，实现动态属性或懒加载 | 极低（安全优雅） |

---

## 2. Python 属性查找的完整调用链

当你执行 `obj.foo` 时，Python 的查找顺序如下：
1. 调用 `obj.__getattribute__('foo')`；
2. 如果类或基类定义了数据描述符（Data Descriptor，实现了 `__set__`），优先使用描述符；
3. 查找实例对象的 `obj.__dict__`；
4. 查找类的非数据描述符（如方法、实现了 `__get__` 的属性）或类属性；
5. **如果经过上述步骤依然没找到**，且对象抛出了 `AttributeError`：
   - 检查是否存在 `__getattr__`；
   - 若存在则执行 `obj.__getattr__('foo')` 获得兜底值；
   - 若不存在则正式抛出 `AttributeError`。

---

## 3. 代码对比演示

```python
class SmartDict:
    def __init__(self, data):
        self._data = data

    # 1. 兜底查找：只有当普通属性不存在时才触发
    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]
        raise AttributeError(f"不存在属性: {item}")

    # 2. 全局拦截：慎用！
    # def __getattribute__(self, item):
    #     # 错误写法：self._data 会无限递归！
    #     # 正确写法：
    #     return super().__getattribute__(item)

d = SmartDict({"username": "alice", "age": 18})
print(d.username)  # 访问成功，输出 alice（通过 __getattr__ 兜底获取）
print(d._data)     # 直接从实例字典获取，不会触发 __getattr__
```
