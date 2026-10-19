## 1. UploadFile 不等于无限资源保护

UploadFile 使用可落盘的临时文件，避免把整个上传作为 bytes 参数常驻内存；但 multipart 解析可能已在路由执行前消耗带宽、内存或临时磁盘。生产必须在网关/服务器层限制请求体、超时和并发，应用层再按业务校验实际内容。

下例按 1 MiB 分块，限制落盘为 20 MiB，使用服务端生成的文件名，绝不直接拼接客户端的 `file.filename`。写入通过 AnyIO 文件接口避免在事件循环里执行大块同步磁盘写。

```python
import tempfile
import uuid
from pathlib import Path
import anyio
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()
UPLOAD_ROOT = Path(tempfile.gettempdir()) / "facee-upload-example"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 20 * 1024 * 1024

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    destination = UPLOAD_ROOT / f"{uuid.uuid4().hex}.bin"
    size = 0
    created = False
    complete = False
    try:
        async with await anyio.open_file(destination, "xb") as output:
            created = True
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(status_code=413, detail="文件超过 20 MiB")
                await output.write(chunk)
        complete = True
        return {"upload_id": destination.name, "size": size}
    finally:
        # 取消或失败时也尝试关闭临时上传并删除本次未完成文件。
        with anyio.CancelScope(shield=True):
            try:
                await file.close()
            finally:
                if created and not complete:
                    await anyio.to_thread.run_sync(destination.unlink)
```

成功文件由业务生命周期管理；示例不提供公开下载入口，也不把扩展名或 MIME 声明当成可信内容检测。运行示例需要 `python-multipart`。

## 2. SSE 输出与取消

```python
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

async def fake_llm_stream(prompt: str, request: Request):
    for char in f"这是对问题 [{prompt}] 的演示回答":
        if await request.is_disconnected():
            break
        # JSON 编码保证换行等字符不会破坏 SSE 的事件边界。
        yield "data: " + json.dumps({"token": char}, ensure_ascii=False) + "\n\n"
        await asyncio.sleep(0.05)

@app.get("/chat/stream")
async def chat_stream(prompt: str, request: Request):
    return StreamingResponse(fake_llm_stream(prompt, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

两个代码块是独立示例应用，分别保存为文件使用。接入真实模型时，需要在生成器的 `try/finally` 中关闭上游流/客户端资源，并让取消继续传播；仅 `break` 本地循环不一定终止上游已经提交的生成或计费。还应配置心跳、超时、并发上限与代理缓冲，不能把响应头当成适配所有代理的保证。

参考：[UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/)、[StreamingResponse](https://www.starlette.dev/responses/#streamingresponse)。
