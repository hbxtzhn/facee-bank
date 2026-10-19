## 1. 框架定位

| 维度 | Django | Flask | FastAPI |
|---|---|---|---|
| 主要定位 | 集成 ORM、管理后台、认证等能力的全栈框架 | 以路由等核心为基础，通过扩展组合应用 | 以类型注解、数据契约与 API 开发为中心 |
| 异步 | 支持 ASGI、异步视图及部分异步 ORM；同步/异步边界仍需确认 | 基于 WSGI；支持 async 视图，但普通部署仍占用一个 worker 处理请求 | 基于 Starlette/ASGI；支持异步路由、WebSocket 与流式响应 |
| 校验/文档 | 可配合 Forms、DRF 和 OpenAPI 工具 | 通常组合扩展或自行设计 | 集成 Pydantic 校验与 OpenAPI 文档 |
| 选型依据 | 需要完整业务后台与成熟集成 | 希望精简核心、灵活组合 | API 契约明确且异步 I/O 需求较多 |

## 2. FastAPI 的核心能力与边界

类型注解和 `Depends` 支持请求解析、依赖复用、响应模型及文档生成。异步数据库驱动、HTTP 客户端可与事件循环协作；参数不合契约时默认返回 422。

“用了 FastAPI 就一定比其他框架快”并不成立。数据库、阻塞调用、响应体大小和部署方式往往更重要；需要匹配任务模型，不能用固定框架性能排名代替选型。

参考：[FastAPI async](https://fastapi.tiangolo.com/async/)、[Django async](https://docs.djangoproject.com/en/5.2/topics/async/)、[Flask async](https://flask.palletsprojects.com/en/stable/async-await/)。
