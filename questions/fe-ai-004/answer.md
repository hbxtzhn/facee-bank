### 一句话总结

模板字面量类型允许使用类似 ES6 模板字符串的语法，在类型层面定义精确的**字符串模式（Pattern Matching）**。例如将日期约束为 `` `${number}-${number}-${number}` ``，或将 AI 产出的状态 ID 约束为 `` `session_${string}_v${number}` ``，实现编译期的结构合规强校验。

---

### 详细回答

#### 1. 常见约束场景
- **日期时间格式**：``type ISODate = `${number}-${number}-${number}`;``
- **实体 ID 规范**：``type MessageId = `msg_${string}`;``，约束必须以 `msg_` 为前缀；
- **颜色十六进制**：``type HexColor = `#${string}`;``
- **模型版本号**：``type ModelTag = `gpt-${'4o' | '4-turbo'}-${number}`;``

#### 2. 结合模式匹配进行条件收缩
通过 `extends` 检查传入的字符串是否符合该模板字面量模式：
```typescript
function validateMsgId<T extends string>(id: T extends `msg_${string}` ? T : never) {
  // 必须传入 msg_ 开头的字符串
}
```

---

### 核心代码片段（极简记法）

```typescript
// 1. 约束 AI 生成的日期与会话 ID 格式
type ISODate = `${number}-${number}-${number}`;
type SessionId = `sess_${string}_v${1 | 2}`;

// 2. 消费测试
const validDate: ISODate = "2026-05-20"; // ✅ 合法
// const invalidDate: ISODate = "2026/05/20"; // ❌ 报错：Type '"2026/05/20"' is not assignable to type '`${number}-${number}-${number}`'
```

---

### 面试加分项

- **静态 vs 运行时双重防线**：模板字面量类型只在**编译期**生效，而 AI 返回的内容是运行时到达的。必须指明在工程中结合 **Zod 字符串正则**（`z.string().regex(/^msg_/)`）作为运行时守卫，两者互补。
