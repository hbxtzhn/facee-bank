## 1. 协议设计哲学与接口签名对比

| 规范 | 架构风格 | 核心接口函数签名 | 处理模型 | 协议支持 |
|---|---|---|---|---|
| **WSGI** (PEP 3333) | 同步阻塞 | `application(environ, start_response)` | 一问一答，单请求独占线程 | 仅支持标准 HTTP/1.1 请求/响应 |
| **ASGI** (异步演进) | 异步事件驱动 | `async def application(scope, receive, send)` | 全双工异步非阻塞协程 | HTTP/1.1、HTTP/2、WebSocket、长连接 SSE |

---

## 2. ASGI 的核心接口三剑客（scope, receive, send）

ASGI 将所有的交互抽象为一个异步可调用对象（Callable）：

```python
async def simple_asgi_app(scope, receive, send):
    if scope['type'] == 'http':
        # 1. scope: 字典，包含本次连接的基础元信息（请求方法、路径、Headers、客户端 IP 等）
        # 2. receive: 异步通道，用于非阻塞等待客户端发来的数据包（如 Body 字节流）
        event = await receive()
        
        # 3. send: 异步通道，用于随时向客户端推送数据包（分块发送）
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'text/plain']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello from Pure ASGI!',
        })
```

---

## 3. 为什么 WebSocket 和大模型流式打字机必须依赖 ASGI？

- **在 WSGI 模型下**：函数必须直接返回一个可迭代的 Response 对象，一次请求处理完毕后该线程的连接就结束了。WSGI 根本无法在不阻塞线程的前提下持续等待客户端随时可能发来的消息（如 WebSocket 上行消息）。
- **在 ASGI 模型下**：`receive` 和 `send` 都是独立的异步等待通道。一个单线程的事件循环（Uvicorn）就能轻松挂起上万个空闲的 WebSocket 连接或 SSE 长连接，有数据时才被内核 `epoll` 唤醒派发事件，真正实现万级高并发。
