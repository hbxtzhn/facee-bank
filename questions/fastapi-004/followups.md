## 追问 1：使用 BaseHTTPMiddleware 时，为什么有时候会遇到 StreamingResponse 丢失或上下文断裂的问题？

BaseHTTPMiddleware 在处理流式响应或捕获异常时，内部通过嵌套 Task 封装，可能导致请求体消费冲突或特定异常被吞并。高并发流式传输（如 SSE、大文件上传下载）场景下，官方推荐编写纯 ASGI 中间件以获得更高的稳定性和性能。
