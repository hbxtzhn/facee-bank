## 1. 两种接口解决的问题不同

| 协议 | 应用接口 | 特点 |
|---|---|---|
| WSGI | `application(environ, start_response)` 返回字节块迭代器 | 同步请求/响应接口，通常由进程或线程执行 |
| ASGI | `async application(scope, receive, send)` | 异步事件接口，规范包含 HTTP、WebSocket 与 lifespan |

WSGI 可以通过迭代器流式输出 HTTP 内容，因此 **SSE 不要求必须使用 ASGI**；不过长时间等待通常占用同步 worker 的执行槽。WebSocket 不属于标准 WSGI 接口，框架或服务器的扩展支持不能等同于 WSGI 本身的保证。

ASGI 支持 HTTP/2 的协议表示，不代表每个 ASGI 服务器都实现 HTTP/2。例如部署时还要查看 Uvicorn 或其他服务器、反向代理的实际能力。

## 2. 最小 ASGI 应用

```python
async def app(scope, receive, send):
    # 示例只实现 HTTP；测试时服务器需禁用 lifespan 自动协商。
    if scope["type"] != "http":
        raise RuntimeError("This example supports HTTP only")
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain; charset=utf-8")],
    })
    await send({"type": "http.response.body", "body": b"Hello ASGI"})
```

`scope` 保存连接/请求元信息，`receive` 提供入站事件，`send` 发出响应事件。读取请求体时需处理多个 `http.request` 事件及 `more_body`，不能假定一次 receive 就读取完整上传。

## 3. 为什么异步模型适合长连接？

等待网络就绪时协程可让出事件循环，让同一线程服务其他连接。实际并发容量仍受文件描述符、内存、业务逻辑与代理配置限制，不能仅凭协议名承诺上万连接。

参考：[ASGI HTTP/WebSocket 规范](https://asgi.readthedocs.io/en/latest/specs/www.html)、[WSGI PEP 3333](https://peps.python.org/pep-3333/)。
