### 一句话总结

定义复杂动态的 AI 接口时，核心是采用**“可辨识联合类型（Discriminated Union）”作为基石**，通过固定的标识符（如 `type: 'text' | 'tool_call'`）让 TypeScript 实现自动类型收窄；结合**泛型映射表与条件类型**，根据具体的工具名（`tool_name`）动态推导对应的参数类型，避免使用任何 `any` 或宽泛的 `object`。

---

### 详细回答

#### 1. 为什么不能用可选字段（`?`）堆砌单个接口？
- **反例**：若定义 `interface Message { content?: string; tool_calls?: any[]; }`，在消费时 `msg.content` 永远是 `string | undefined`，必须处处写非空断言 `!` 或额外判空，且无法约束“文本消息绝不能有 tool_calls”这一互斥业务规则。
- **正解（可辨识联合）**：通过具有唯一标识字段（如 `type`）的独立接口联合：
  ```typescript
  type TextMessage = { type: 'text'; content: string };
  type ToolCallMessage<T extends string = string> = { type: 'tool_call'; tool: T; args: ToolArgs<T> };
  type AIMessage = TextMessage | ToolCallMessage;
  ```
  在 `if (msg.type === 'text')` 分支下，TS 会自动将 `msg` 收窄为 `TextMessage`，安全访问 `msg.content`。

#### 2. 工具调用的泛型映射与条件类型推导
- **建立工具注册表（Tool Registry）**：集中声明每个工具的入参 Schema：
  ```typescript
  interface ToolSchemaMap {
    search: { query: string; limit?: number };
    calculator: { expression: string };
  }
  ```
- **使用条件类型提取入参**：
  ```typescript
  type ToolArgs<T extends string> = T extends keyof ToolSchemaMap 
    ? ToolSchemaMap[T] 
    : Record<string, unknown>; // 兜底未知工具
  ```

#### 3. 流式 Chunk 增量类型的动态推导
- 流式返回的 delta 往往是完整结构的浅层可选子集，使用条件类型和映射修饰符实现：
  ```typescript
  type StreamDelta<T> = T extends object ? { [K in keyof T]?: StreamDelta<T[K]> } : T;
  ```

---

### 核心代码片段（极简记法）

```typescript
// 1. 工具类型字典
interface ToolRegistry {
  web_search: { query: string };
  code_runner: { code: string; language: 'js' | 'python' };
}

// 2. 可辨识联合类型（Discriminated Union）
type AIMessage = 
  | { type: 'text'; content: string }
  | { [K in keyof ToolRegistry]: { type: 'tool'; name: K; args: ToolRegistry[K] } }[keyof ToolRegistry];

// 3. 消费时自动精准类型收窄
function handleMessage(msg: AIMessage) {
  if (msg.type === 'text') {
    console.log(msg.content.toUpperCase()); // 安全推导为 string
  } else if (msg.name === 'web_search') {
    console.log(msg.args.query); // 自动推导出 { query: string }
  }
}
```

---

### 面试加分项

- **Zod 运行时校验与类型同步**：在真实项目中，大模型返回的 JSON 参数是不可信的字符串。通常用 `zod` 定义工具入参 Schema，利用 `z.infer<typeof schema>` 自动生成 TS 类型，兼顾**静态类型安全**与**运行时异常拦截**。
- **模板字面量约束**：可用模板字面量类型约束模型标识符（如 `type ModelName = \`gpt-${'4o' | '4-turbo'}\` | \`claude-3-5-${'sonnet' | 'haiku'}\``），提高静态拼写防护。
