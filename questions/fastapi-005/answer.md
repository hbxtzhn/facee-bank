## 1. ASGI 服务器与进程管理

Uvicorn 负责 HTTP/WebSocket 协议与 ASGI 调用，可以使用不同的 HTTP 实现和事件循环；uvloop 并非所有平台或安装方式下的必备组件。Uvicorn 自身提供 `--workers` 多进程管理与健康监控，并不是只能由 Gunicorn 才能拉起多个进程。

Gunicorn 是 Unix 生态常用的进程管理器。若采用 Gunicorn + Uvicorn，应使用独立的 **uvicorn-worker** 包；旧的 `uvicorn.workers` 模块已弃用。

## 2. 两种可选启动方式

```bash
# 自带多进程管理；仅作起始配置，按资源限制调整
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

# Unix 环境，先安装 gunicorn 和 uvicorn-worker
# pip install gunicorn uvicorn-worker
gunicorn main:app --workers 2 --worker-class uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000 --timeout 60
```

生产环境还需反向代理/TLS、可信代理头、健康检查与优雅退出配置。不要把 `2 * CPU + 1` 套成异步 worker 的通用最优公式：每个 worker 都有独立连接池、模型副本与内存占用，CPU 配额和数据库容量也会限制数量。

## 3. 容器选型

Kubernetes 等平台常采用单进程容器配合多个副本；单容器多 worker 也可以是经过资源评估的选择。裸机或虚拟机可选择 Uvicorn 自身的管理器或 Gunicorn，关键是明确由谁监督进程和处理信号。

参考：[Uvicorn deployment](https://uvicorn.dev/deployment/)、[FastAPI server workers](https://fastapi.tiangolo.com/deployment/server-workers/)。
