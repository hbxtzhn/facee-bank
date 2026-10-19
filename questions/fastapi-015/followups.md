## 追问 1：在 APIRouter 中定义 dependencies=[Depends(verify_token)] 与在具体的路由函数中传参定义有何区别？

在 router 级别注入 dependencies 会使得该路由分组下的所有接口统一强制执行该依赖校验，且无需在每个路由函数的形参中显式接收返回值，非常适合用于模块级的大门权限管控。

## 追问 2：为什么企业级项目中要严格区分 models（ORM 实体）和 schemas（Pydantic 模型）？

models 映射存储结构，schemas 描述 API 输入输出契约。独立的响应 DTO 可避免把 password_hash 等内部字段直接序列化，但仍需正确配置 response_model、字段排除及对象级授权；仅仅建立两个目录不保证敏感字段不会泄露。解耦也便于 API 演进与数据库结构分别管理。
