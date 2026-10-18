## 追问 1：FastAPI 是如何区分同一个路由中的路径参数、查询参数和请求体（Body）的？

若参数名声明在路径模版中（如 /items/{item_id}），识别为路径参数；若参数类型继承自 BaseModel 或被显式标注为 Body()，识别为请求体（JSON）；其余单一简单类型（如 int, str）默认自动识别为 URL 查询参数（Query）。
