# Python / FastAPI 30 题人工审核记录（v1.3.0）

审核日期：2026-10-19。范围：15 道 Python 与 15 道 FastAPI 的题面、答案、追问及目录标题。题库保留已有 ID，版本从 1.2.0 提升至 1.3.0，总题数仍为 505；原有 475 题未作本轮逐篇事实审核。

本文记录人工逐篇核对与修正，不替代代码运行或设备验收。示例的实际执行环境、通过/失败项、不能独立运行的教学片段、ZIP 结构与 SHA256 应以本版本 Release 验证附件为准。性能数字不是本次审核目标，没有新增性能基准或压力测试。

## Python：实现与版本边界

| 题目 ID | 核对结果与主要修正 |
|---|---|
| python-001 | GIL 结论限定于启用 GIL 的 CPython；区分 3.13 实验自由线程和 3.14 受支持的可选构建；自由线程不等于纯粹依靠原子引用计数。 |
| python-002 | 区分引用计数与循环 GC；不将所有 Python 实现、所有 CPython 版本描述为固定三代；修正有 __del__ 的循环必泄漏和一般 LRU 缓存是弱引用的说法。 |
| python-003 | 迭代器协议与生成器函数区分；保留 yield/yield from 解释，缩小示例数据量，去掉运行环境无关的内存节约倍数。 |
| python-004 | 三层装饰器是常见写法而非语法强制；修正函数名/重试参数不匹配；同步重试校验参数，wraps 不保证运行时签名被改写，异步需单独 await 实现。 |
| python-005 | await 不必总切换任务，CPU/同步阻塞工作会卡事件循环；异步客户端需要作用域和关闭，并与线程池、进程池的用途区分。 |
| python-006 | C3 不是简单 BFS/DFS 的变体；明确局部优先、单调性和 super 沿最终 MRO 查找，更新题面与目录标题。 |
| python-007 | dict 布局/填充阈值属于 CPython 版本实现；3.7 起插入顺序是语言保证；修正自动缩容、__hash__/__eq__ 必须同时手写等绝对化描述。 |
| python-008 | 明确赋值/浅深拷贝差异、自引用 memo，以及不可变对象和自定义复制协议的边界；避免用特定对象 ID 作为可移植保证。 |
| python-009 | 默认参数绑定用于捕获循环时值；nonlocal 适用于重新绑定，不把对可变对象的原地修改与赋值混同。 |
| python-010 | 单例 __new__ 不能直接调用无参数匹配的 __init__，重复构造会再初始化；教学缓存不声称并发安全，优先区分类装饰器与 __init_subclass__。 |
| python-011 | with 的异常传播、__enter__ 失败与 finally 边界；__exit__ 返回真值可抑制异常，异步资源需对应异步协议。 |
| python-012 | 普通实例属性查找需考虑数据描述符、实例字典和非数据描述符；魔术方法可能走类型上的隐式查找，防递归应调用 object.__getattribute__。 |
| python-007b | 将巨大分配替换为小型 IPC 教学；共享内存不等于任意 Python 对象零拷贝；映射可能按页取整，显式传递并按有效数据长度读写；Python 3.14 POSIX 默认 forkserver 需区分平台与支持条件。 |
| python-014 | is/== 的语言语义与 CPython 缓存分开；去掉依赖 REPL/编译常量合并的确定输出和固定驻留规则，更新题面与目录。 |
| python-015 | 循环引用不必然泄漏；RSS、解释器分配器与 tracemalloc 覆盖范围区分；减少演示分配量，去掉硬编码内存数字。 |

## FastAPI：接口、安全与资源生命周期

| 题目 ID | 核对结果与主要修正 |
|---|---|
| fastapi-001 | def 端点/同步依赖通常在线程池执行，而 async def 内同步阻塞并不会自动被框架搬走；不保证框架名本身带来固定吞吐优势。 |
| fastapi-002 | 依赖树、请求级缓存、替换测试依赖；yield 清理时机说明 FastAPI 版本和 scope，不把所有版本概括为响应前关闭。 |
| fastapi-003 | Pydantic v2 的整数转换不允许任意浮点截断；model_dump 与 Python dict 的区别、字段校验及路径/查询/请求体推断边界。 |
| fastapi-004 | 中间件与异常处理职责区分；BaseHTTPMiddleware 的 ContextVar 传播限制，纯 ASGI 中间件不可无条件假定 HTTP scope。 |
| fastapi-005 | uvicorn.workers 的弃用与独立 uvicorn-worker；内置多进程管理、容器资源约束和反向代理信任配置，不写固定 worker 数公式。 |
| fastapi-006 | WSGI 可通过 iterable 流式响应，不是只能一次性 bytes；ASGI 明确 scope/receive/send 与 WebSocket/lifespan，更新题面和目录。 |
| fastapi-007 | lifespan 放在独立模块作用域，app.state 存取资源；初始化失败与正常退出都释放已创建资源，移除无边界的昂贵模型演示。 |
| fastapi-008 | 后注册中间件通常位于更外层，返回按相反顺序；ContextVar 和 body 流限制分开描述，不笼统声称所有大上传必然失败；yield scope 时序有版本条件。 |
| fastapi-009 | BackgroundTasks 在同一进程内响应发送后运行；同步任务在线程池、异步任务 await，任务列表默认顺序执行，异常不会回写已发送响应。 |
| fastapi-010 | 补缺失 send_personal_message，finally 清理连接；明确逐个广播的慢客户端问题及进程内列表的边界，心跳协议与应用层心跳区分。 |
| fastapi-011 | SQLAlchemy AsyncSession 的查询需要 await；提供完整模型/查询模块与 selectinload，说明 MissingGreenlet、过期字段、并发 Session 和事务边界。 |
| fastapi-012 | 使用受环境配置的密钥、真实哈希校验和有限期 JWT；OAuth2PasswordBearer 只提取 token，JWT 签名不是加密；补错误密码/过期/声明校验；RFC 9700 密码授权限制。 |
| fastapi-013 | UploadFile 的落盘不构成总上传保护；加入大小限制、服务端文件名、异步写和失败清理；SSE JSON 事件编码与上游取消/资源关闭边界。 |
| fastapi-014 | CORS 不是认证或 CSRF 防御；显式 origins/methods/headers，凭据响应不能允许通配 Origin；简单请求、预检与缓存分别说明。 |
| fastapi-015 | 将缺 app、缺模块的片段改为可导入的单文件多级路由演示；鉴权示例默认拒绝且只读演示环境值；依赖返回值不自动注入，DTO 分层不自动保证无泄漏。 |

## 核对依据

- [Python 自由线程说明](https://docs.python.org/3/howto/free-threading-python.html) 与 [Python 3.14 新变化](https://docs.python.org/3/whatsnew/3.14.html)。
- [gc 模块](https://docs.python.org/3/library/gc.html)、[PEP 442：安全的对象终结](https://peps.python.org/pep-0442/)、[weakref](https://docs.python.org/3/library/weakref.html)。
- [数据模型](https://docs.python.org/3/reference/datamodel.html)、[copy](https://docs.python.org/3/library/copy.html)、[functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps)、[asyncio](https://docs.python.org/3/library/asyncio-task.html)、[multiprocessing](https://docs.python.org/3/library/multiprocessing.html)。
- [FastAPI async/def](https://fastapi.tiangolo.com/async/)、[高级依赖与 yield scope](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)、[lifespan](https://fastapi.tiangolo.com/advanced/events/)。
- [Pydantic 转换表](https://docs.pydantic.dev/latest/concepts/conversion_table/)、[Uvicorn 部署](https://www.uvicorn.org/deployment/)、[ASGI 规范](https://asgi.readthedocs.io/en/latest/specs/main.html)。
- [Starlette BaseHTTPMiddleware 限制](https://www.starlette.dev/middleware/#limitations)、[BackgroundTasks](https://www.starlette.dev/background/)、[FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)。
- [SQLAlchemy 异步 ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)、[FastAPI JWT 教程](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)、[RFC 9700 §2.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.4)。
- [UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/)、[CORS](https://fastapi.tiangolo.com/tutorial/cors/)、[大型应用路由装配](https://fastapi.tiangolo.com/tutorial/bigger-applications/)。

上述参考材料用于事实与 API 交叉核对；本轮新增内容的许可边界见仓库 NOTICE 和 sources.md。
