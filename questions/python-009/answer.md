## 1. 闭包的定义与底层存储

**闭包（Closure）** 是指：一个内层函数引用了外层函数作用域中的非全局变量（自由变量），并且外层函数返回了这个内层函数。即便外层函数执行完毕生命周期结束，这些被引用的变量依然会被保存在内存中。

### 底层原理：`__closure__` 与 `cell` 对象
当 Python 编译器发现内层函数引用了外部自由变量时，会在堆上创建一个特殊的 **`cell` 对象**：
- 外层函数把该变量存储在 `cell` 对象的指针中；
- 返回的内层函数对象的 `__closure__` 属性持有这个 `cell` 的元组引用；
- 无论内层函数何时何地被调用，都是通过 `cell.cell_contents` 获取变量值。

---

## 2. 经典的“延迟绑定（Late Binding）”踩坑

看下面这段非常经典的面试高频代码：

```python
def make_multipliers():
    return [lambda x: i * x for i in range(4)]

funcs = make_multipliers()
print([f(2) for f in funcs])
# 直觉以为是：[0, 2, 4, 6]
# 实际输出是：[6, 6, 6, 6]！
```

### 为什么全是 6？
因为**闭包在定义时并不会立即计算并固定变量的值，而是在内层函数被真正调用执行时，才去作用域中动态查找变量当前的值**。
- 当 `make_multipliers()` 执行完时，循环已经结束，此时 `i` 的最终值是 `3`；
- 4 个 lambda 函数的 `__closure__` 中引用的都是同一个 `i` 的 cell 对象；
- 随后执行 `f(2)` 时，读取到的 `i` 全部是 `3`，计算 $3 	imes 2 = 6$。

---

## 3. 标准解决解法

### 解法一：利用默认参数（推荐，最 Pythonic）
函数的默认参数是在**函数定义时求值**并固定下来的：
```python
def make_multipliers():
    # 通过 i=i 将当前循环的 i 固化为函数的默认参数
    return [lambda x, i=i: i * x for i in range(4)]

funcs = make_multipliers()
print([f(2) for f in funcs])  # 输出：[0, 2, 4, 6]
```

### 解法二：借助额外的函数作用域（嵌套工厂）
```python
def make_multipliers():
    def make_fn(val):
        return lambda x: val * x
    return [make_fn(i) for i in range(4)]
```
