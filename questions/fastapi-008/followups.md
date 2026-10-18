## 追问 1：FastAPI 中如果同时使用了中间件（Middleware）和路由依赖注入（Depends），谁先执行？谁后执行？

中间件先于依赖注入执行。完整的链路是：HTTP 请求 -> 外层中间件的前置逻辑 -> 路由匹配 -> 执行该路由的 Depends 依赖解析 -> 路由处理函数 -> 退出 Depends 上下文 -> 中间件后置逻辑 -> 返回客户端。

## 追问 2：纯 ASGI 中间件应该怎么写？

定义一个普通 Python 类，__init__ 接收 app（下一个 ASGI 应用），并实现 async def __call__(self, scope, receive, send) 方法，直接在原始 ASGI 消息层拦截处理。
