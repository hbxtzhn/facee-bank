## 追问 1：SQLAlchemy 2.x 查询接口如何演进？

推荐 `select(Model)` 配合 Session/AsyncSession 执行；旧 Query 属于 legacy API，并非所有 1.x 接口都已被删除。`Model.query` 常来自 Flask-SQLAlchemy 等集成层，不能当成 SQLAlchemy 所有 ORM 模型原生都有的属性。

## 追问 2：事务上下文解决什么问题？

`async with session.begin()` 在正常退出时提交、异常时回滚，集中管理事务边界；也可以显式 commit/rollback。关键是提交成功后才向客户端返回成功，不能仅在响应已发送后的依赖清理阶段提交关键写操作。
