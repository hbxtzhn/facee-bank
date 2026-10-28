## 追问 1：如果模板字符串非常长（几千字 Prompt），递归类型推导会不会触发 TS 的“类型实例化深度超限”（Type instantiation is excessively deep）？

**回答要点**：
会！TS 默认递归深度限制为 1000 左右。
应对策略：
1. 对于超长 Prompt，仅对变量字典做泛型约束，而非全文递归；
2. 或者拆分为段落式子模板进行组合推导；
3. 将模板声明放在独立的 `as const` 常量中。

---

## 追问 2：如何在类型系统中支持带类型的变量声明（如 {age:number}）？

**回答要点**：
在模板占位符中约定格式 `{varName:type}`，在 `infer Param` 中进一步用模板字面量切分为 `${infer Key}:${infer Type}`，并映射到对应原生类型（`'number' -> number`、`'boolean' -> boolean`）。
