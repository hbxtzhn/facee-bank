## 1. BackgroundTasks 的工作机制

FastAPI 的 `BackgroundTasks`（源自 Starlette）是一种**轻量级、同进程内的后台任务机制**：

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome_email(email: str, username: str):
    # 模拟耗时 2 秒的邮件发送
    pass

@app.post("/register")
async def register_user(user: UserSchema, bg_tasks: BackgroundTasks):
    # 1. 注册业务逻辑已完成
    save_to_db(user)
    
    # 2. 挂载后台任务：该任务不会阻塞响应
    bg_tasks.add_task(send_welcome_email, user.email, user.username)
    
    # 3. 立即向客户端返回 200 OK 响应！
    # ★ 响应完全发送给客户端之后，事件循环才开始就地执行 send_welcome_email
    return {"status": "success", "message": "注册成功"}
```

---

## 2. 深度对比：BackgroundTasks vs Celery

| 对比维度 | FastAPI 原生 BackgroundTasks | Celery / RQ (分布式任务队列) |
|---|---|---|
| **执行载体** | **当前 API 进程内部**（占用当前服务的 CPU/内存/事件循环） | **完全独立的 Worker 进程/跨物理机集群** |
| **持久化存储** | **无持久化（纯内存任务队列）** | 基于 RabbitMQ / Redis / SQS 等强持久化 Broker |
| **容灾抗风险** | **极低**。若服务器重启、发版更新或 Worker 进程 OOM 崩溃，**内存中未执行的任务全部永久丢失** | **极高**。有消息确认（ACK）与心跳机制，Worker 挂了任务自动重新分配给其他人 |
| **重试机制** | 无内置重试，抛错即结束 | 支持指数退避重试（Exponential Backoff）、死信队列（DLX） |
| **资源隔离** | 无法隔离。重型计算会抢占 Web 服务的 CPU，拖垮 API 吞吐 | 完全物理隔离，即便任务把 Worker 算爆，前端 API 依旧秒开 |
| **运维复杂度** | **零成本**（零额外外部组件依赖） | 较高（需维护 Redis/RabbitMQ、Celery Beat、Flower 监控面板等） |

---

## 3. 生产选型黄金准则

- **选择原生 `BackgroundTasks` 的场景**：
  - 任务执行耗时极短（< 3 秒）；
  - 丢失了对业务影响不大（如写入分析访问埋点、发送非关键验证日志）；
  - 小型项目不希望引入繁重的 MQ 运维包袱。
- **必须选用 `Celery` 的场景**：
  - 耗时长于 5 秒以上的重任务（如音视频转码、大批量 PDF/Excel 报表生成、AI 模型离线微调/批量推理）；
  - 核心关键业务不允许丢失（如第三方支付异步充值到账对账、短信通道重试）；
  - 需要定时任务（Crontab/调度）以及任务结果状态持久化查询。
