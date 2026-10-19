## 1. 隐式 I/O 与 MissingGreenlet

AsyncSession 下访问尚未加载的关系属性或已过期字段，可能试图在普通属性访问中执行异步 I/O。若没有 SQLAlchemy 所需的异步桥接上下文，就可能出现：

```text
greenlet_spawn has not been called; can't call await_only() here.
```

不要将同步示例 `session.get(...)` 直接照搬给 AsyncSession：异步方法需要 await；响应序列化期间也应避免再触发未声明的 I/O。

## 2. 在明确的 await 边界预加载

以下为可导入的 SQLAlchemy 2.x 查询模块；调用前需创建表和测试数据。

```python
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    orders: Mapped[list["Order"]] = relationship(lazy="raise")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

async def load_user(session: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id).options(selectinload(User.orders))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is not None:
        print(len(user.orders))  # 已加载，不在属性访问处追加查询
    return user
```

`selectinload` 通常先查主对象，再用 `IN (...)` 查询关联；大批量父对象可能分批查询，不是固定永远两条 SQL。`joinedload` 可用 JOIN 预加载，加载集合时通常还需 `result.unique()` 去重，避免结果行膨胀。

## 3. 其他防护

按需求使用 `expire_on_commit=False` 避免提交后立即过期；也可以用 AsyncAttrs 的 `awaitable_attrs` 或显式 `await session.refresh(...)`。一个 AsyncSession 不应被并发任务共用。事务可以由 `async with session.begin()` 管理，正常退出提交、异常回滚。

参考：[SQLAlchemy 避免隐式 I/O](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession)。
