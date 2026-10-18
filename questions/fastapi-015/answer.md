## 1. 企业级推荐分层工程目录树

```text
my_fastapi_project/
├── app/
│   ├── main.py                  # 应用装配中心：生命周期、全局中间件、路由聚合
│   ├── core/                    # 核心配置
│   │   ├── config.py            # Pydantic-settings 读取环境变量
│   │   ├── security.py          # 密码加盐、JWT 编解码
│   │   └── database.py          # SQLAlchemy 异步引擎与会话工厂
│   ├── api/                     # 表现层（控制器）
│   │   ├── v1/
│   │   │   ├── api.py           # 统一聚合 v1 路由器
│   │   │   └── endpoints/       # 具体模块路由
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       └── items.py
│   ├── models/                  # 基础设施层：SQLAlchemy ORM 数据库实体
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/                 # 契约层：Pydantic 验证模型（Req/Resp DTO）
│   │   ├── user.py
│   │   └── item.py
│   ├── services/                # 业务逻辑层（纯粹的业务编排，解耦路由）
│   │   ├── user_service.py
│   │   └── order_service.py
│   └── tests/                   # 自动化单测与集成测试
└── pyproject.toml
```

---

## 2. APIRouter 的多层级依赖继承

利用 `APIRouter`，我们可以将路由与权限像俄罗斯套娃一样分层包裹：

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends

# 模块级路由器：指定统一前缀与文档标签
router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/")
async def list_users():
    return [{"username": "alice"}]

# ─────────────────────────────────────────────────────────────
# app/api/v1/api.py
from fastapi import APIRouter, Depends
from app.api.v1.endpoints import users, auth
from app.core.security import verify_admin_token

api_v1_router = APIRouter()

# 普通用户公开/登录接口
api_v1_router.include_router(auth.router, prefix="/auth")

# ★ 权限继承：给整组 /users 接口统一强制叠加管理员权限依赖
api_v1_router.include_router(
    users.router,
    dependencies=[Depends(verify_admin_token)]
)

# ─────────────────────────────────────────────────────────────
# app/main.py (顶层组装)
app.include_router(api_v1_router, prefix="/api/v1")
```
最终访问地址自动组装为 `/api/v1/users/`，自动带上权限校验，结构井井有条，易于维护。
