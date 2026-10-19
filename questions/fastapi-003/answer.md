## 1. Pydantic 在 FastAPI 中的角色

Pydantic 是 FastAPI 的数据骨架，主要负责：
1. **解析与校验**：按字段类型和配置接受或拒绝输入，例如宽松模式下 `"123"` 可转成整数；非整数浮点值等不能无条件转换，严格模式会进一步限制转换。
2. **业务规则校验（Validation）**：字段范围、正则匹配、自定义业务规则拦截。
3. **序列化与响应契约**：声明合适的响应模型后，按其字段输出数据；敏感字段必须通过独立响应 DTO、排除字段等方式明确处理，不能假定 Pydantic 自动识别所有秘密字段。
4. **生成 OpenAPI Schema**：驱动 Swagger UI 自动生成完整的字段文档与示例值。

---

## 2. Pydantic V1 到 V2 的核心蜕变

### ① 底层重写：Rust 引擎（pydantic-core）
- V1 核心逻辑由纯 Python 编写，在大批量数据校验序列化时性能相对较弱。
- V2 通过 Rust 实现的 **pydantic-core** 执行核心校验与序列化，Python 层仍负责模型定义与集成。实际性能受模型、自定义校验和序列化方式影响，不承诺固定加速倍数。

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
