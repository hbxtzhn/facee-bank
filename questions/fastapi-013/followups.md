## 追问 1：bytes、UploadFile 与普通 Python open 文件对象在上传时有什么不同？

如果路由参数声明为 file: bytes，FastAPI 会一次性把整个文件读入内存，大文件瞬间会导致内存打满；而声明为 UploadFile 时，底层采用 SpooledTemporaryFile，内存只留一个小缓冲区，超出部分自动写入操作系统的临时磁盘文件，内存占用极小且安全。

## 追问 2：在 SSE（Server-Sent Events）向前端流式传输时，前端断开连接（如用户在界面点击了停止生成），FastAPI 后端能感知到并停止调用下游的大模型 API 吗？

可以。在异步生成器内部通过循环轮询 request.is_disconnected() 方法判断。如果检测到前端客户端已断开，立即 break 跳出生成循环，从而中断后续对大模型 API 的流式拉取，避免无谓浪费 Token。
