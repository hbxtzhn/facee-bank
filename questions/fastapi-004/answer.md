## 1. 中间件（洋葱模型）

FastAPI 中间件包裹在整个应用的外部，请求到达具体路由之前、以及响应离开应用返回给客户端之后，都会经过中间件链路。

### 典型场景：
- 全局 TraceID 注入与日志记录
- 请求耗时统计头（`X-Process-Time`）
- 全局跨域 CORS 设置（`CORSMiddleware`）
- 全局 Gzip 压缩

```python
import time
import uuid
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_trace_and_timing(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id  # 贯穿本次请求
    
    start_time = time.perf_counter()
    response = await call_next(request)  # 进入后续中间件或路由处理
    cost_time = time.perf_counter() - start_time
    
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-Process-Time"] = f"{cost_time:.4f}s"
    return response
```

---

## 2. 全局统一异常捕获与标准化返回

在生产企业级 API 开发中，绝不能直接把 500 堆栈抛给前端，而是应收拢为统一格式 `{code, message, data}`：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class BusinessException(Exception):
    """自定义业务异常"""
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg

# 1. 捕获自定义业务异常
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=200,  # 业务码包裹在 JSON 中，HTTP 状态码返回 200
        content={"code": exc.code, "message": exc.msg, "data": None}
    )

# 2. 覆盖默认的 422 参数校验异常，输出更友好的错误说明
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}" if errors else "参数错误"
    return JSONResponse(
        status_code=400,
        content={"code": 40001, "message": f"参数校验不通过: {first_msg}", "data": None}
    )
```
