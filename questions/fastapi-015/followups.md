## 追问 1：在 APIRouter 中定义 dependencies=[Depends(verify_token)] 与在具体的路由函数中传参定义有何区别？

在 router 级别注入 dependencies 会使得该路由分组下的所有接口统一强制执行该依赖校验，且无需在每个路由函数的形参中显式接收返回值，非常适合用于模块级的大门权限管控。

## 追问 2：为什么企业级项目中要严格区分 models（ORM 实体）和 schemas（Pydantic 模型）？

models 映射的是数据库物理表的存储结构；而 schemas 映射的是外部 API 的输入输出契约。两者解耦可以严格防止数据库敏感字段（如 password_hash、内部租户 ID）泄露到前端，也允许外部接口格式随业务灵活重构而无需频繁改动数据库底层表。
