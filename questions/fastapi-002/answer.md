## 1. 声明依赖，由框架解析与复用

路由通过 `Depends` 声明所需参数、认证与资源。FastAPI 分析签名，递归解析依赖；同一请求内相同依赖通常有缓存，可用 `use_cache=False` 改变行为。测试可通过 `app.dependency_overrides` 替换实现。

## 2. 资源生命周期与事务生命周期要分开

带 `yield` 的依赖适合管理会话释放；**不要默认在 yield 之后 commit**，因为默认请求作用域可能在响应发送完成后才执行收尾。若提交失败，客户端可能已经拿到成功响应。

下面使用 SQLAlchemy 2.x 的异步会话工厂，在路由的事务块正常退出时提交、异常时回滚；提交成功后才返回。安装示例依赖：`fastapi sqlalchemy aiosqlite`。

```python
from collections.abc import AsyncIterator
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./example.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI()

async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # 用 SELECT 演示无业务表依赖的可运行事务；写业务也在此边界内完成。
        value = await db.scalar(text("SELECT :user_id"), {"user_id": user_id})
    return {"user_id": value}
```

## 3. 说明版本与 scope

FastAPI 0.118.0 起，请求作用域 yield 依赖的退出时机重新放在响应发送之后，适配流式响应。0.121.0 起可显式选择 `Depends(get_db, scope="function")`，使退出发生在路由函数完成后、发送响应前；流式响应若仍需要会话则不能提前关闭。

因此应根据安装版本、scope 与是否流式输出讨论时序，不把一种固定的中间件/依赖清理顺序当成全部版本的通则。

参考：[高级依赖与 scope](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)。
