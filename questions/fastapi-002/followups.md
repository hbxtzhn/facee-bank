## 追问 1：Depends 默认在同一个请求中多次引用同一个依赖项，会被执行多次吗？

默认不会。FastAPI 的 Depends(func, use_cache=True) 默认开启了请求级缓存。在单个 HTTP 请求中，相同的依赖项只会被执行一次并将结果缓存复用；若每次都要重新计算，需设置 use_cache=False。
