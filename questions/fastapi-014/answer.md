## 1. CORS 是浏览器的跨源访问规则

Origin 由协议、主机和端口组成。满足 CORS safelist 的简单请求（例如部分 GET/HEAD/POST 和允许的请求头）可直接发送；使用 Authorization、application/json 等非 safelist 条件时，浏览器通常先发带 Origin 与 Access-Control-Request-Method 的 OPTIONS 预检。

CORS 不是服务端认证，也不防止非浏览器客户端调用；简单请求即使响应不能被脚本读取，也可能已经在服务器执行，所以 Cookie 认证仍需处理 CSRF。

## 2. 携带凭据时显式列出可信来源

凭据模式下，浏览器不能接受 `Access-Control-Allow-Origin: *`。框架可能将部分通配配置展开成具体来源，但不要依赖这种行为代替明确的信任名单。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-app.example", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

@app.get("/ping")
async def ping():
    return {"ok": True}
```

明确列出允许的方法与请求头；生产按环境移除调试来源。OPTIONS 预检由中间件处理，不需要为了预检单独暴露业务 OPTIONS 路由。

参考：[FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)、[Starlette CORS](https://www.starlette.dev/middleware/#corsmiddleware)。
