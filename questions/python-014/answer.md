## 1. 相等性与身份

`==` 通过类型的相等比较规则判断，通常涉及 `__eq__`，返回值未必是单个布尔值；`is` 判断是否为同一个对象，不能被重载。对象存活期间 `id()` 表示其身份；CPython 通常用地址实现，但地址不是 Python 语言的通用承诺。

```python
a = [1, 2, 3]
b = [1, 2, 3]
assert a == b
assert a is not b
assert None is None
```

## 2. 小整数与编译常量

CPython 常见实现缓存 `[-5, 256]` 的整数；这属于实现细节，不是用 `is` 比较数字的依据。编译器也可能在同一代码对象内合并更大的相同常量，因此 `1000 is 1000` 一类实验会随编译单元与版本变化。

## 3. 字符串驻留

CPython 会自动驻留某些字符串，尤其是编译器使用的名称；**动态构造、看起来像标识符的字符串并不保证自动驻留**。需要明确驻留时可调用 `sys.intern()` 并保留返回值；比较字符串内容仍应使用 `==`。

参考：[对象身份](https://docs.python.org/3.14/reference/datamodel.html#objects-values-and-types)、[sys.intern](https://docs.python.org/3.14/library/sys.html#sys.intern)。
