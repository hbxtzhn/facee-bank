## 追问 1：Object.create(null) 创建的对象在判空时有何特殊之处？

**回答要点**：
`Object.create(null)` 没有原型链（`__proto__ === undefined`），没有诸如 `toString` 等任何内置方法，遍历时不会受到任何原生原型的干扰，结构极其纯净。

---

## 追问 2：直接修改 Object.prototype 对整个项目有何致命危害？

**回答要点**：
会导致原型污染（Prototype Pollution）！
全工程所有普通对象都会意外多出这个属性，不仅导致第三方库的遍历逻辑全部崩溃，还会引入严重的远程代码执行（RCE）安全漏洞。
