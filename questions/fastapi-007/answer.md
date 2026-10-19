## 1. 用 lifespan 将创建与释放放在一起

FastAPI 推荐使用 lifespan 上下文管理器；`on_event("startup")` / `on_event("shutdown")` 已弃用。统一上下文便于共享局部资源，也能用 `try/finally` 表达成对释放。不能把配置了 lifespan 后的旧事件处理器也默认算成会一起执行。

下面使用当前 redis-py 的 `redis.asyncio`，不再使用已停止独立维护的 aioredis 包。

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from redis.asyncio import Redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    try:
        await redis.ping()  # 启动前检查；失败也会进入 finally
        app.state.redis = redis
        yield
    finally:
        await redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/ping")
async def ping(request: Request):
    return {"redis_ping": await request.app.state.redis.ping()}
```

安装示例依赖 `fastapi redis`，运行需要 Redis；单元测试应替换为桩对象，不访问真实服务。`from_url` 创建客户端不需要 await；连接相关操作和 `aclose()` 需要 await。

## 2. 清理不是任何故障下的绝对保证

正常退出或被应用正确处理的异常会执行 finally；SIGKILL、进程崩溃和机器断电无法保证执行 Python 清理逻辑。初始化多个资源可配合 `AsyncExitStack`，在中途失败时释放之前已成功获取的资源。

参考：[FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)、[redis-py asyncio](https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html)。
