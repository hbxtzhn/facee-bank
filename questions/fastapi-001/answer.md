## 1. 核心架构对比

| 比较维度 | Django | Flask | FastAPI |
|---|---|---|---|
| **定位风格** | “自带电池”大而全的全栈框架（ORM、Admin、模板、Auth 全包） | 极简微框架，仅提供路由与核心上下文，其余靠扩展插件 | 现代轻量高性能 API 框架，专注微服务与后端接口 |
| **异步支持** | 历史同步为主，新版本部分兼容 ASGI 但生态包历史包袱重 | 传统 WSGI 同步为主（2.0 实验性支持 async） | **原生 ASGI（基于 Starlette）**，天生全异步高并发 |
| **数据校验** | Django Forms / DRF Serializers（相对冗长繁琐） | 需手动校验或借助第三方（Marshmallow 等） | **深度整合 Pydantic**，基于 Python 原生类型注解自动校验 |
| **接口文档** | 需安装 drf-yasg 等插件配置 | 需第三方插件（Flasgger 等） | **开箱即用 Swagger UI / ReDoc**，全自动交互式文档 |
| **性能基准** | 偏中低 | 中等 | **接近 Node.js / Go 的高吞吐表现**（基于 Uvicorn） |

---

## 2. FastAPI 的四大核心杀手锏

1. **类型提示即契约（Type Hints Driven）**：
   写标准的 Python 类型标注，FastAPI 一步完成四件事：**入参解析**、**类型转换**、**校验报错（友好 JSON）**与**Swagger 文档生成**。
2. **极其优雅的依赖注入系统（Depends）**：
   层级分明、组件高度可复用，极易进行单元测试 Mock 与权限生命周期管理。
3. **原生异步生态支持**：
   与 SQLAlchemy 2.0 (asyncio)、Redis-py (asyncio)、httpx 等现代异步生态无缝打通。
4. **开发者体验与报错友好**：
   当入参不合法时，自动返回精准的 422 状态码和详细的字段级定位错误，无需手动写繁复的异常捕获。
