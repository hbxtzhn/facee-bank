## 1. Pydantic 在 FastAPI 中的角色

Pydantic 是 FastAPI 的数据骨架，主要负责：
1. **数据解析与清洗（Parsing & Coercion）**：宽进严出，自动将外部传来的字符串/浮点数智能转换为目标数据类型（例如 `"123"` 自动转为 `int`）。
2. **业务规则校验（Validation）**：字段范围、正则匹配、自定义业务规则拦截。
3. **响应序列化（Serialization）**：将 ORM 数据对象自动过滤敏感字段并转成符合契约的 JSON。
4. **生成 OpenAPI Schema**：驱动 Swagger UI 自动生成完整的字段文档与示例值。

---

## 2. Pydantic V1 到 V2 的核心蜕变

### ① 底层重写：Rust 引擎（pydantic-core）
- V1 核心逻辑由纯 Python 编写，在大批量数据校验序列化时性能相对较弱。
- V2 将核心校验与序列化逻辑完全用 **Rust（pydantic-core）** 重写，带来了 **5 到 50 倍的性能飙升**，直接让 FastAPI 的吞吐能力再上一个台阶。

### ② 常用方法迁移对比表

| 功能 | Pydantic V1 API | Pydantic V2 API（推荐） |
|---|---|---|
| 转字典 | `model.dict()` | `model.model_dump()` |
| 转 JSON 字符串 | `model.json()` | `model.model_dump_json()` |
| 字典解析为模型 | `Model.parse_obj(data)` | `Model.model_validate(data)` |
| 自定义字段校验器 | `@validator("age")` | `@field_validator("age")` |
| 模型级多字段校验器 | `@root_validator` | `@model_validator(mode="after/before")` |
| 模型配置项 | `class Config:` 内部类 | `model_config = ConfigDict(...)` |

### 生产示例（V2 语法）：
```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class UserRegisterReq(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=20)
    age: int = Field(..., ge=18, le=120)

    @field_validator("username")
    @classmethod
    def no_admin(cls, v: str) -> str:
        if "admin" in v.lower():
            raise ValueError("用户名禁止包含敏感词 admin")
        return v
```
