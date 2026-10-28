## 追问 1：如果对象中有 Symbol 类型的 key，Object.keys() 能捕获到吗？

**回答要点**：
捕获不到！
`Object.keys()` 只返回字符串类型的自身可枚举 key；若要完全覆盖 Symbol，必须使用 `Reflect.ownKeys(obj)` 或 `Object.getOwnPropertySymbols(obj)`。

---

## 追问 2：如果传入的是一个自定义类实例（如 new Date()），你的判空函数会怎么表现？

**回答要点**：
`new Date()` 自身没有直接属性，但它有内置的时间戳状态（通过 `date.getTime()` 读取）。如果不加拦截，会被普通对象规则误判为空；因此严谨的库会加白名单优先排除 Date 与 RegExp 实例。
