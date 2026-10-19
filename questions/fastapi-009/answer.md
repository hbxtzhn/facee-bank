## 1. 响应发送后的同进程工作

`BackgroundTasks` 来自 Starlette，是附在响应上的任务列表。响应发送后按添加顺序执行；它不是持久化消息队列，也不是自动新建进程。

```python
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Notification(BaseModel):
    username: str = Field(min_length=1, max_length=50)

def record_notification(username: str):
    # 教学占位：真实通知服务在这里调用；不宣称已写数据库或已发邮件。
    print("已处理演示通知")

@app.post("/notify", status_code=202)
async def notify(body: Notification, tasks: BackgroundTasks):
    tasks.add_task(record_notification, body.username)
    return {"accepted": True}
```

同步任务由 AnyIO 线程池调度，异步任务被 await；多个任务默认顺序执行，前一个抛异常会使后续任务不再执行。CPU 重任务仍可能影响当前 API 进程，异步函数内的阻塞代码仍会阻塞事件循环。

## 2. 与外部队列的选择

| 需求 | BackgroundTasks | Celery / RQ 等 |
|---|---|---|
| 进程重启后恢复 | 不提供持久化 | 取决于 broker、持久化与确认配置 |
| 重试、结果查询、调度 | 需自行实现 | 可配置对应能力 |
| 资源隔离 | 与 API 同进程 | 可放到独立 worker，但资源仍需规划 |
| 交付保证 | 进程退出可能丢失 | 需设计 ACK、重投和幂等，不能默认“恰好一次” |

选型依据是可靠性、耗时、并发与隔离需求，没有通用的“3 秒/5 秒”分界。支付、关键通知等需要可靠交付时，还应考虑事务 outbox 与业务幂等。

参考：[Starlette background tasks](https://www.starlette.dev/background/)、[FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)。
