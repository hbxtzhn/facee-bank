## 追问 1：同步 worker 遇到大量长轮询会怎样？

每个正在等待的同步请求会占用可用执行槽；如果并发超过 worker/线程容量，其他请求会排队或超时。具体内存与吞吐取决于部署数量、超时和负载，不能断言某个固定连接数一定内存耗尽。WSGI 的流式迭代器可以发送 SSE，只是同步等待的资源模型与异步不同。

## 追问 2：FastAPI、Starlette、Uvicorn 如何分工？

Uvicorn 负责网络协议解析和调用 ASGI 应用；Starlette 提供路由、中间件、响应、WebSocket 等基础能力；FastAPI 在其上集成类型驱动的参数处理、Pydantic、依赖注入与 OpenAPI。
