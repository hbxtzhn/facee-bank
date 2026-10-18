## 追问 1：在 lifespan 中初始化的全局资源（如 Redis 连接池、AI 模型权重），如何在具体的路由函数中优雅访问？

可以在 lifespan 中通过 yield 前后将资源存入 app.state（例如 app.state.redis = redis_pool）。在路由函数中，既可以通过 request.app.state.redis 直接读取，也可以编写一个 Depends(get_redis) 依赖项注入，方便单元测试覆盖。

## 追问 2：如果在 lifespan 启动阶段（yield 之前）发生了网络异常（如连不上数据库），FastAPI 会怎么处理？

yield 之前发生异常，应用会立刻终止启动并退出进程，不会接受任何外部 HTTP 流量。这种“快速失败（Fail-Fast）”机制极其符合生产部署要求，能防止容器在依赖缺失的情况下对外提供假死服务。
