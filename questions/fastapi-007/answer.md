## 1. 传统 on_event 的历史缺陷

在早期的 FastAPI / Starlette 中，管理生命周期采用事件监听器：
```python
# 传统写法（官方已正式弃用 Deprecated）
@app.on_event("startup")
async def startup_event():
    # 初始化 DB
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # 关闭 DB
    pass
```

### 痛点：
1. **启动与清理割裂在两个独立函数中**：无法直接共享局部变量（例如启动时创建的引擎实例必须借用全局变量传递给关闭函数）；
2. **异常回滚复杂**：若 startup 中途抛出异常，shutdown 不会被调用，可能导致前面已申请的连接或资源无法正常析构释放；
3. **类型推导与测试不友好**：对 Starlette 的 ASGI 标准演进兼容较差。

---

## 2. 现代推荐：lifespan 上下文管理器

FastAPI 官方全面推荐使用 Python 标准库的 `@asynccontextmanager` 定义统一的 `lifespan`：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import aioredis

# ★ 集中式生命周期上下文管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── [启动阶段] ── (yield 之前)
    print(">>> 正在初始化系统：建立 Redis 连接池、预热 AI 大模型...")
    redis = await aioredis.from_url("redis://localhost:6379")
    app.state.redis = redis  # 挂载到应用全局状态
    
    yield  # ★ 此时应用启动成功，开始接收并处理客户端 HTTP 请求
    
    # ── [关闭阶段] ── (yield 之后，哪怕发生终止信号也会执行)
    print("<<< 收到关闭信号：正在优雅关闭 Redis 连接池、flush 缓冲日志...")
    await redis.close()

# 绑定生命周期
app = FastAPI(lifespan=lifespan)

@app.get("/ping")
async def ping(request: Request):
    # 路由中轻松获取全局就绪资源
    redis = request.app.state.redis
    val = await redis.ping()
    return {"redis_ping": val}
```

### 核心优势：
- **逻辑高内聚**：资源的“创建”与“释放”写在同一个上下文里，成对出现，一清二楚；
- **利用 Python 原生异常栈**：支持使用标准 `try...finally` 结构，保证关闭清理必定被执行；
- **资源共享极简**：通过闭包作用域或 `app.state` 传递，告别全局脏变量。
