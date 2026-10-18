## 追问 1：传统的 WSGI 容器（如 Gunicorn + sync worker）在遇到 1000 个长轮询连接时会发生什么？

WSGI 的每一个连接都必须绑定一个操作系统进程或线程。如果并发 1000 个连接，需要开 1000 个工作线程/进程，不仅内存直接爆炸，而且 CPU 会被天量的线程上下文切换拖垮，绝大多数连接会超时排队报错。

## 追问 2：FastAPI、Starlette、Uvicorn 三者在处理一个请求时分别负责什么？

Uvicorn（ASGI 服务器）负责监听 Socket 端口并解析 HTTP/WebSocket 协议；Starlette（ASGI 核心框架）负责底层路由匹配、中间件调度和会话生命周期；FastAPI 继承自 Starlette，在此之上增加了 Pydantic 参数校验、依赖注入系统和自动 OpenAPI/Swagger 文档生成。
