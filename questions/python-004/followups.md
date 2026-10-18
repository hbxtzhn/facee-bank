## 追问 1：为什么写装饰器一定要加上 @functools.wraps(func)？

若不用 functools.wraps，原函数的元信息（如 __name__、__doc__、参数签名）会被替换为内层 wrapper 函数的信息，导致反射、调试栈信息丢失以及基于签名的工具（如 FastAPI 依赖注入、文档生成）失效。
