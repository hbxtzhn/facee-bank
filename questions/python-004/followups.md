## 追问 1：functools.wraps 保留了什么？

它复制 `__name__`、`__doc__`、注解等元数据，并设置 `__wrapped__`，使 `inspect.signature()` 等工具能沿包装链找到原函数签名。它不会把 wrapper 的实际调用参数或栈帧变成原函数；调用行为是否正确仍取决于包装代码，异步函数也需相应的异步包装器。

参考：[functools.wraps](https://docs.python.org/3.14/library/functools.html#functools.wraps)。
