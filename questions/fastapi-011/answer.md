## 1. 致命报错根因剖析：`MissingGreenlet`

在使用异步 ORM（如 `asyncpg` + `AsyncSession`）时，最常遇到的经典崩溃：
```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; 
can't call __init__() in this worker (attribute 'items' is not loaded)
```

### 为什么会发生？
- **传统同步 ORM 的惰性加载（Lazy Loading）机制**：查询 `user = session.get(User, 1)` 时只查用户表；当后续你在代码里访问 `user.orders` 时，SQLAlchemy 内部会**隐式、默默地再发一次同步 SQL 查询**把订单查出来。
- **异步世界的冲突**：在异步世界中，**所有的 I/O 操作都必须显式声明 `await`**。当你在 Pydantic 序列化或模板中访问 `user.orders` 属性时，访问普通属性是不带 `await` 的！SQLAlchemy 无法在一个纯同步的属性访问器中发起异步 I/O 查询，Greenlet 驱动无法挂起，因此直接抛出 `MissingGreenlet` 阻断。

---

## 2. 标准解决方案：显式及早加载（Eager Loading）

必须在最初发起查询时，告诉 SQLAlchemy 把关联对象一次性查出来，彻底禁用隐式惰性查询。

### 方案 A：`selectinload`（推荐，处理 1 对多、多对多最佳）
它会分两次查询：先查主表，然后用 `IN (...)` 子查询批量捞出所有关联项，没有大单表笛卡尔积膨胀风险：

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# ★ 关键：通过 options(selectinload(User.orders)) 预先装载
stmt = select(User).where(User.id == user_id).options(selectinload(User.orders))
result = await session.execute(stmt)
user = result.scalar_one_or_none()

# 此时 user.orders 已经就绪在内存中了，可以直接读取，绝不报错！
print(len(user.orders))
```

### 方案 B：`joinedload`（处理 1 对 1、多对 1 最佳）
利用 SQL 的 `LEFT OUTER JOIN` 将主表与关联表在一张大结果集内通过单条 SQL 一并拉取返回。

---

## 3. 防御性配置最佳实践

在定义模型关系属性时，推荐显式指定 `lazy="raise"` 或 `lazy="selectin"`：
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 显式禁止隐式惰性加载，一旦漏写预加载，本地测试阶段立刻明确报错提醒
    orders: Mapped[List["Order"]] = relationship(lazy="raise")
```
