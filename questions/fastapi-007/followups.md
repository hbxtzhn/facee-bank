## 追问 1：路由如何使用 lifespan 资源？

可在 `yield` 前存入 `app.state`，通过 `request.app.state` 获取，或在依赖函数中读取并注入，以便测试替换。资源通常是每个应用进程一份，不能将其当成多 worker 之间共享的内存对象。

## 追问 2：启动阶段失败怎么办？

lifespan 在 yield 前抛异常时，正常支持 lifespan 的 ASGI 服务器会判定启动失败，不应将该进程标记为就绪。是否退出、重启及如何切流由服务器与进程/容器管理器决定。已获取的资源应由 try/finally 或 AsyncExitStack 清理，不能依赖未进入的 yield 后普通语句。
