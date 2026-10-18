## 追问 1：SQLAlchemy 2.0 的 select() 语法与 1.x 的 Model.query 相比有何核心改进？

2.0 统一采用了 select(Model).where(...) 显式查询语法，彻底废弃了跟 ThreadLocal 绑定的 Model.query，语法与原生 SQL 更贴近，而且这一套语法在同步引擎与基于 asyncpg/aiosqlite 的异步引擎中完全统一，类型检查更加友好。

## 追问 2：异步 Session 的 commit 和 rollback 为什么要配合 async with session.begin()？

async with session.begin() 会自动管理事务生命周期，在块正常结束时自动调用 await session.commit()，若中途发生任何未捕获异常则自动触发 await session.rollback()，能够有效防止因为忘记 commit 导致数据丢失或由于忘记 rollback 导致脏连接放回连接池。
