### 一句话总结

综合判空采用**“基础假值快速短路 + 精准类型分流分支校验”**。首先过滤 `null` 与 `undefined`；数值 `0` 与布尔 `false` 按题意归入空；对复合引用类型分别校验：字符串与数组取 `.length === 0`，Map 与 Set 校验 `.size === 0`，普通对象校验 `Reflect.ownKeys(val).length === 0`。

---

### 详细回答

#### 1. 业务定义中的各种“空”分类
- **原生假值类**：`null`, `undefined`, `NaN`, `0`, `""`；
- **集合容器类**：
  - 数组：`[]`；
  - Map / Set：`new Map()`, `new Set()`；
- **纯对象类**：`{}`。

#### 2. 避免踩坑：为什么不能简单用 `!value`？
- 普通的 `!value` 会把非空对象 `{}` 和非空数组 `[]` 判定为 `true`（它们在布尔转换时是真值）；
- 必须针对引用对象进行内部元素的容量探测。

---

### 核心代码片段（极简记法）

```javascript
function isEmpty(val) {
  // 1. null, undefined, 空字符串, 数字 0, NaN 均为空
  if (val === null || val === undefined || val === '' || val === 0 || Number.isNaN(val)) return true;

  // 2. 数组或字符串
  if (Array.isArray(val) || typeof val === 'string') return val.length === 0;

  // 3. Map 或 Set
  if (val instanceof Map || val instanceof Set) return val.size === 0;

  // 4. 普通对象（包含 Symbol 键）
  if (typeof val === 'object') return Reflect.ownKeys(val).length === 0;

  return false;
}
```

---

### 面试加分项

- **对数字 0 是否为空的业务辩证**：必须主动向面试官指出：在常规通用工具库（如 Lodash `_.isEmpty(0)`）中，数字 `0` 是被当作**非空（有效数值）**看待的。本题之所以将 0 判为空是基于特定的业务表单清空场景，展示自己对通用库规范与业务定制差异的清醒认知。
