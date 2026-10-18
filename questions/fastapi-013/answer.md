## 1. 大文件分块安全上传：`UploadFile`

不要一次性 `await file.read()`，这会把几 GB 的文件瞬间塞满服务器内存。应当使用**流式切块（Chunked Streaming）**：

```python
from fastapi import FastAPI, UploadFile, File
import shutil
from pathlib import Path

app = FastAPI()

@app.post("/upload")
async def upload_large_file(file: UploadFile = File(...)):
    dest_path = Path("/tmp") / file.filename
    # 分块读取，每块 1MB，内存始终只占用 1MB！
    chunk_size = 1024 * 1024
    with dest_path.open("wb") as buffer:
        while chunk := await file.read(chunk_size):
            buffer.write(chunk)
            
    await file.close()  # 必须释放临时文件句柄
    return {"filename": file.filename, "size": dest_path.stat().st_size}
```

---

## 2. AI 大模型流式输出（SSE，Server-Sent Events）

通过 `StreamingResponse` 包装异步生成器，将 LLM 产出的每个 Token 实时推送给客户端：

```python
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

# 模拟大模型异步流式吐字
async def fake_llm_stream(prompt: str, request: Request):
    full_reply = f"这是针对问题 [{prompt}] 的详细深度回答："
    for char in full_reply:
        # ★ 生产关键：检查前端用户是否已中途关掉了网页
        if await request.is_disconnected():
            print("客户端已主动断开，终止后续模型生成！")
            break
            
        # 遵循标准 SSE 格式：data: <内容>\n\n
        yield f"data: {char}\n\n"
        await asyncio.sleep(0.05)  # 模拟打字间隔

@app.get("/chat/stream")
async def chat_stream(prompt: str, request: Request):
    return StreamingResponse(
        fake_llm_stream(prompt, request),
        media_type="text/event-stream",  # 标准流式媒体类型
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # ★ 告诉 Nginx 禁用反向代理缓冲，立刻推给前端
        }
    )
```
