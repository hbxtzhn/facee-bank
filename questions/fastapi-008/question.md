# FastAPI 中间件的执行顺序是怎样的？为什么大文件上传时不建议用 BaseHTTPMiddleware？

请详细说明多个中间件在注册时的洋葱模型调用顺序，分析 Starlette BaseHTTPMiddleware 在流式传输（Streaming）和大文件上传时的内部 Task 陷阱，并给出编写高性能纯 ASGI 中间件的规范范式。
