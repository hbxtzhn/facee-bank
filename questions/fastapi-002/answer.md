## 1. 什么是依赖注入？

依赖注入（DI）是指：**路由函数不主动创建自己所需的资源，而是声明自己“需要什么”，由框架在调用前负责实例化、注入参数，并在请求结束后进行收尾**。

FastAPI 通过 `Depends` 提供声明式依赖注入，其底层借助 Python 的 `inspect` 模块分析函数签名，解析出所有依赖参数并构建有向无环图（DAG），按拓扑序依次解析执行。

---

## 2. 常见使用场景

1. **安全校验与认证鉴权**（获取当前登录用户、解析 JWT Token、权限 RBAC 校验）。
2. **共享数据库连接与事务上下文**（每请求一个 DB Session）。
3. **通用分页与筛选参数复用**。
4. **测试时的依赖替换（`app.dependency_overrides`）**：单测时用内存数据库或 Mock 用户秒级替换真实依赖。

---

## 3. 带 yield 的依赖（上下文生命周期管理）

利用生成器语法 `yield`，可以非常直观地实现「请求到达时初始化 -> 请求处理 -> 响应返回后清理资源」的完整闭环：

```python
from fastapi import Depends, FastAPI
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ★ 数据库 Session 依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session         # 注入给路由处理函数
            await session.commit() # 正常处理则统一提交
        except Exception:
            await session.rollback() # 异常则自动回滚
            raise
        # 退出 async with 块时自动关闭会话

app = FastAPI()

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # 直接使用由框架安全注入的 db 实例
    return {"user_id": user_id}
```
