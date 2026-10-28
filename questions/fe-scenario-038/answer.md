### 一句话总结

判定包含原型链的自定义数据判空，**核心是使用 `for...in` 循环扫描对象及其原型链上的所有可枚举属性，并借助 `Object.prototype` 过滤掉 ECMAScript 语言内置的标准原生原型属性（如 `toString`、`valueOf`）**；若扫描到任何非内置的自定义属性或方法，立即判定为“非空”。

---

### 详细回答

#### 1. 为什么 `Object.keys()` 与 `Reflect.ownKeys()` 都不行？
- `Object.keys(obj)` 只能获取对象**自身拥有的（Own Properties）**可枚举属性，完全忽略原型链上的继承数据；
- 无法满足“包含原型链自定义数据”的题目要求。

#### 2. 原型链过滤的核心策略
- 原生内置的顶级原型 `Object.prototype` 默认带有很多系统内置属性（`isPrototypeOf`, `propertyIsEnumerable` 等），但它们都是不可枚举的；
- 若开发者或第三方库手动修改了原型（例如 `obj.__proto__.myCustomProp = 123`），这个属性是可枚举的，能被 `for...in` 抓取；
- **排查逻辑**：
  遍历原型链直到 `proto === null` 或 `proto === Object.prototype`，收集所有自定义属性。

---

### 核心代码片段（极简记法）

```javascript
function isDeepEmpty(obj) {
  if (obj === null || typeof obj !== 'object') return false;

  // for...in 会遍历自身及整条原型链上的可枚举属性
  for (const key in obj) {
    // 排除内置 Object.prototype 原生属性干扰
    if (!(key in Object.prototype)) {
      return false; // 存在自定义原型属性或自身属性，非空！
    }
  }

  // 进一步检查不可枚举但用户自定义的非原生方法
  let curr = obj;
  while (curr && curr !== Object.prototype) {
    const ownProps = Object.getOwnPropertyNames(curr);
    const hasCustom = ownProps.some(k => k !== 'constructor');
    if (hasCustom) return false;
    curr = Object.getPrototypeOf(curr);
  }

  return true;
}
```

---

### 面试加分项

- **对不可枚举属性与 Symbol 的考量**：指出如果原型链上的方法是通过 `Object.defineProperty(proto, 'customFn', { enumerable: false })` 定义的，`for...in` 会漏掉。必须配合 `Object.getPrototypeOf()` 向上递归，用 `Object.getOwnPropertyNames()` 与 `Object.getOwnPropertySymbols()` 综合扫描才算 100% 严谨。
