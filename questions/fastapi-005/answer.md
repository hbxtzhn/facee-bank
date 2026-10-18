## 1. 架构角色分工：Gunicorn + Uvicorn

- **Uvicorn**：是一个极致轻量的高性能 **ASGI 服务器**，基于 `uvloop`（libuv 的 Python 封装）和 `httptools` 构建，专注于高效解析 HTTP 协议并驱动事件循环执行异步协程。但它本身缺乏强大的进程监控、平滑重启等生产运维能力。
- **Gunicorn**：是一个成熟的 UNIX **进程管理器（Process Manager）**，擅长 Master-Worker 架构管理：监听信号、工作进程崩溃自愈、平滑重载配置（Zero-downtime Reload）等。

因此，在传统服务器/虚拟机环境中，标准的生产黄金搭档是：**由 Gunicorn 担任 Master 进程主管，管理多个使用 `uvicorn.workers.UvicornWorker` 的工作进程**。

---

## 2. 生产部署命令与配置

```bash
gunicorn main:app   --workers 4   --worker-class uvicorn.workers.UvicornWorker   --bind 0.0.0.0:8000   --timeout 60   --keep-alive 5   --access-logfile -   --error-logfile -
```

### Worker 进程数设定公式：
$$\text{Workers} = 2 \times \text{CPU核心数} + 1$$
*（针对 I/O 混合型任务，通常一个 4 核服务器分配 8~9 个 UvicornWorker 即可打满性能瓶颈）*

---

## 3. 部署架构演进方案对比

| 部署形态 | 架构组成 | 优势 | 适用场景 |
|---|---|---|---|
| **传统 ECS / 裸机部署** | Nginx (反代/SSL/静态) + Gunicorn (Master) + Uvicorn (Workers) | 进程崩溃自动拉起，多核打满，平滑热更 | 单机或私有云虚拟机 |
| **容器 / K8s 云原生部署** | Ingress (Nginx/Traefik) + Pod (单容器单 Uvicorn 实例) | K8s 天然接管进程调度与健康巡检，弹性扩缩容极快 | 生产微服务集群、公有云 Serverless |
