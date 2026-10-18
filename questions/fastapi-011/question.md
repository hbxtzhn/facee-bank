# FastAPI 集成 SQLAlchemy 2.0 异步 ORM 时，MissingGreenlet 异常是怎样产生的？如何解决？

请分析在 async / await 环境下访问关系属性（Relationship）触发延迟加载（Lazy Loading）引发 Greenlet 协程上下文缺失的根因，并给出使用 selectinload / joinedload 预加载的正确解法。
