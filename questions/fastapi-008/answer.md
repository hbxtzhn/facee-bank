## 1. 多个中间件的执行顺序（洋葱模型）

在 FastAPI 中通过 `@app.middleware("http")` 或 `app.add_middleware()` 注册多个中间件时，其执行顺序是**洋葱结构**：

```text
注册顺序（代码自上而下）：
app.add_middleware(MiddlewareA)  # 最先注册（最外层）
app.add_middleware(MiddlewareB)  # 后注册（内层）

请求进入阶段：
  客户端发起请求 ──> MiddlewareA (前置) ──> MiddlewareB (前置) ──> 路由处理函数
                                                                        │
响应返回阶段：                                                           │
  客户端收到响应 <── MiddlewareA (后置) <── MiddlewareB (后置) <────────┘
```
**口诀**：**“先进后出，洋葱包裹”**。越先添加的中间件，在请求时越先执行，在响应返回时越后离开。

---

## 2. 为什么大文件上传/流式输出慎用 BaseHTTPMiddleware？

`BaseHTTPMiddleware` 是 Starlette 封装的高层级便捷工具，但其底层实现有严重隐患：
1. **内部创建独立的异步 Task**：
   为了让开发者能像写普通同步函数一样使用 `call_next(request)`，它在底层启动了一个新的 `asyncio.Task` 来运行下游应用。
2. **上下文变量丢失（ContextVars）**：
   在不同 Task 之间切换可能导致部分基于 `contextvars` 的链路追踪库丢失上下文。
3. **破坏流式传输（Streaming / SSE）与内存爆破**：
   当进行大文件分块上传或 SSE 流式输出时，`BaseHTTPMiddleware` 很容易在错误处理分支中强行缓冲整个 Body，导致大文件直接吃空服务器内存，或者由于 Task 取消导致生成器流断裂。

---

## 3. 高性能纯 ASGI 中间件编写范式

针对超高并发、大文件处理或流式传输场景，官方推荐编写**原生纯 ASGI 中间件**：

```python
class PureASGICustomMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 仅对 HTTP 请求做处理，WebSocket 及其它协议透明放行
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. 请求前置处理（可修改 scope 中的 headers、query 等）
        # ...
        
        # 2. 拦截并包装 send 回调（用于后置给客户端追加 Header）
        async def custom_send(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"X-Engine-Name", b"FaceE-ASGI"))
                message["headers"] = headers
            await send(message)

        # 3. 将包装后的 send 传递给下游应用（零额外 Task 封装，零内存缓冲）
        await self.app(scope, receive, custom_send)

# 挂载
app.add_middleware(PureASGICustomMiddleware)
```
