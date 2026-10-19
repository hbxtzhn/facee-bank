## 追问 1：BaseHTTPMiddleware 有哪些限制？

官方文档明确指出下游对 ContextVar 的修改无法正常向上游传播；它的任务边界与请求/响应封装也使部分底层控制更复杂。不能据此断言所有 StreamingResponse 都会丢失或所有上传都会缓存整个请求体。需要精确控制 ASGI 消息、取消或跨任务上下文时，可编写纯 ASGI 中间件。

参考：[Starlette 中间件限制](https://www.starlette.dev/middleware/#limitations)。
