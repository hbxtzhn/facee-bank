# FastAPI 生命周期：为什么弃用 @app.on_event，推荐现代的 lifespan？

请对比传统的 @app.on_event("startup") / ("shutdown") 与现代的 @asynccontextmanager lifespan 生命周期机制，阐述两者的设计演进背景及完整的实战代码范式。
