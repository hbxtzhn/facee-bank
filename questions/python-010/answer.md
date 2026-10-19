## 1. 类的本质：类也是对象

在 Python 中，“万物皆对象”贯彻得极其彻底：**类本身也是一个对象，是由元类（Metaclass）实例化出来的**。

```text
元类（默认是 type） ──实例化──> 类（如 User） ──实例化──> 实例对象（如 user1）
```

- 普通对象的类型是它所属的类：`type(user1) is User`
- 类的类型是 `type`：`type(User) is type`
- `type` 既是所有类的默认元类，它自己本身也是自己的实例。

---

## 2. `__new__` vs `__init__`

```text
调用 User(*args, **kwargs)
        │
        ▼
1. User.__new__(cls, *args, **kwargs)  --> 【构造阶段】：静态方法，分配内存，返回新实例对象 instance
        │
        ▼
2. instance.__init__(*args, **kwargs)  --> 【初始化阶段】：实例方法，接收 instance，对其属性赋值
```

| 维度 | `__new__` | `__init__` |
|---|---|---|
| **调用时机** | 最先调用，负责对象的创建 | 仅在 `__new__` 返回该类或子类的实例时继续调用 |
| **方法类型** | 静态方法（第一个参数为 `cls`） | 实例方法（第一个参数为 `self`） |
| **返回值** | 通常返回新实例；若返回其他类型的对象，会跳过原类的 `__init__` | 必须返回 `None`，可显式 `return None`；返回其他值会触发 TypeError |
| **主要用途** | 继承不可变类型（如重写 `int`, `tuple`）；编写单例模式；元类中构建新类 | 普通对象的成员变量赋值与初始化逻辑 |

---

## 3. 元类的实战应用：极简 ORM 字段拦截

元类允许我们在**定义类（即 Python 文件被 import）时**，自动拦截并解析类内部的属性：

```python
class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        # 排除基类 Model 本身
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)
        
        # 扫描并收集所有定义的 Column 字段
        fields = {}
        for k, v in list(attrs.items()):
            if not k.startswith("_") and isinstance(v, str):  # 教学字段，排除 __module__ 等类元数据
                fields[k] = v
        attrs["_fields"] = fields
        print(f"★ 成功注册 ORM 数据表 [{name}]，包含字段：{list(fields.keys())}")
        return super().__new__(mcs, name, bases, attrs)

class Model(metaclass=ModelMeta):
    pass

class User(Model):
    name = "VARCHAR(50)"
    age = "INT"

# 模块一导入，控制台立刻打印：
# ★ 成功注册 ORM 数据表 [User]，包含字段：['name', 'age']
```
