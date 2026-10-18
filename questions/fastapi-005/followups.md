## 追问 1：在 Docker 容器或 Kubernetes 环境中部署 FastAPI，还要用 Gunicorn 启多进程吗？

在 K8s 环境中，最佳实践通常是「单个容器只跑一个单进程 Uvicorn」，通过 Kubernetes 的 Pod 副本控制器（ReplicaSet / HPA）来进行容器维度的弹性扩缩容，这样健康检查更精准、资源边界更清晰，避免容器内僵尸进程。而在裸机或普通 ECS 上部署时，Gunicorn + Uvicorn 组合依然最省心。
