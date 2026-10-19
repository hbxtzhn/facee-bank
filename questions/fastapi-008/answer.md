## 1. 注册顺序与包裹顺序

对 `app.add_middleware()` 和 `@app.middleware("http")` 添加的用户中间件，**最后添加的位于最外层**。例如先 A 后 B：

```text
注册：A，然后 B
请求：B 前置 → A 前置 → 路由
响应：路由 → A 后置 → B 后置
```

Starlette 内置的错误处理中间件还有自己的外层/内层位置。不要将用户注册顺序简单套到所有框架内部层。

## 2. BaseHTTPMiddleware 的实际限制

其已知限制包括下游 ContextVar 修改不能向上游正常传播。它的任务边界还可能影响取消与高级流处理的设计，但不能笼统声称所有 SSE 必然被破坏、所有上传必然缓存完整 body。处理流式协议时应避免自己读取或缓冲完整请求/响应体，复杂场景可以直接编写纯 ASGI 中间件。

## 3. 完整的纯 ASGI 示例

```python
from fastapi import FastAPI

class AddHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_header(message):
            if message["type"] == "http.response.start":
                message = dict(message)
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-engine-name", b"FaceE-ASGI")
                ]
            await send(message)

        await self.app(scope, receive, send_with_header)

app = FastAPI()
app.add_middleware(AddHeaderMiddleware)

@app.get("/ping")
async def ping():
    return {"ok": True}
```

示例不缓冲 body，不创建额外 Task；响应头名按 ASGI 要求使用小写字节串。

参考：[FastAPI middleware order](https://fastapi.tiangolo.com/tutorial/middleware/)、[Starlette middleware](https://www.starlette.dev/middleware/)。
