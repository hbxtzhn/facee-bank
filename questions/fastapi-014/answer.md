## 1. 为什么浏览器会发送 OPTIONS 预检请求？

跨域资源共享（CORS）是**浏览器单方面的同源安全防御机制**。

- **简单请求**：满足方法为 `GET/POST/HEAD`，且请求头仅包含 `Accept`、`Content-Type` 为 `application/x-www-form-urlencoded` 或 `multipart/form-data` 等，浏览器直接发起真实请求并在返回时检查响应头。
- **复杂请求**：包含自定义 Header（如 `Authorization: Bearer xxx`）、请求头 `Content-Type: application/json`、或请求方法为 `PUT/DELETE`：
  - 浏览器必须在发送真实数据前，**自动先行发送一条 `OPTIONS` 方法的嗅探预检请求（Preflight Request）**；
  - 只有当服务端预检确认通过，浏览器才会继续发起真正的业务请求。

---

## 2. 致命大坑：`allow_credentials=True` 与 通配符 `*`

根据 W3C CORS 规范：**当允许携带 Cookie / 身份凭据（`allow_credentials=True`）时，`Access-Control-Allow-Origin` 绝对不能为通配符 `*`！**

如果强行这么配，现代所有主流浏览器都会直接在控制台报错并拦截响应。

### 生产标准安全配置：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 明确列出受信任的前端域名白名单
origins = [
    "https://my-app.com",
    "https://admin.my-app.com",
    "http://localhost:3000",  # 本地前端调试
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # 白名单域名
    # 如果域名很多且动态多变，可用正则模式：
    # allow_origin_regex=r"https://.*\.my-domain\.com",
    allow_credentials=True,             # 允许携带 Cookie
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],                # 允许前端自定义请求头
    max_age=86400,                      # 预检缓存 24 小时，极大减少 OPTIONS 发包
)
```
