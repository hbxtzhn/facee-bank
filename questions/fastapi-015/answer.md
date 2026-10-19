## 1. 结构按职责划分，而不是套固定目录

典型工程可将入口装配、配置与安全、API 路由、ORM models、Pydantic schemas、业务 services 和测试分别组织。目录名不是框架要求；小项目不必提前拆成大量空层。

```text
app/
  main.py
  core/       # 配置、鉴权、连接工厂
  api/v1/     # 路由聚合与端点
  models/     # ORM 存储模型
  schemas/    # 请求/响应契约
  services/   # 业务与事务编排
 tests/
pyproject.toml
```

## 2. 多级路由与依赖的单文件演示

下面展示完整可运行的路由装配。`X-Demo-Token` 只用于演示依赖继承；生产应替换为真实身份认证与权限校验。测试时从环境设置 `DEMO_ADMIN_TOKEN` 为临时假值，不提供配置则拒绝访问。

```python
import os
import secrets
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException

def verify_demo_admin(x_demo_token: str | None = Header(default=None)):
    expected = os.environ.get("DEMO_ADMIN_TOKEN")
    if not expected or not x_demo_token or not secrets.compare_digest(x_demo_token, expected):
        raise HTTPException(status_code=403, detail="演示管理员凭据无效")

users_router = APIRouter(prefix="/users", tags=["用户管理"])

@users_router.get("/")
async def list_users():
    return [{"username": "alice"}]

api_v1_router = APIRouter()
api_v1_router.include_router(users_router, dependencies=[Depends(verify_demo_admin)])
app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")
```

最终地址为 `/api/v1/users/`。聚合层的 dependencies 会在组内请求时执行，但返回值不自动注入端点参数；需要使用返回值时，在端点或下游依赖中声明。模块、router、include_router 和端点自己的依赖可以叠加，请求缓存语义仍适用。

拆为多文件时，把 router 和鉴权依赖放进相应模块，在 main.py 导入聚合路由即可；不要漏掉 `app = FastAPI()` 或依赖模块定义。

参考：[FastAPI bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)。
