### 一句话总结

**`infer` 关键字用于在条件类型的模式匹配中“声明待推导的类型变量”**。通过递归或深层结构解构，可精准穿透嵌套的数组与对象，自动提取诸如 `Response['choices'][number]['delta']['content']` 等深层叶子节点类型，即便服务端接口定义包裹多层也能零冗余提取纯文本类型。

---

### 详细回答

#### 1. infer 的核心工作机制
`T extends Pattern<infer P> ? P : Fallback`：
- `extends` 左边是传入的具体类型；
- 右边是包含 `infer X` 的占位模板；
- 编译器会反向推导匹配占位符的真实类型并将其绑定到 `X` 上。

#### 2. 提取 choices[0].delta.content 案例
```typescript
type OpenAIChatChunk = {
  id: string;
  choices: Array<{
    index: number;
    delta: { content?: string; role?: string };
  }>;
};

// 利用 infer 提取数组元素与嵌套 delta
type ExtractContent<T> = T extends {
  choices: Array<{
    delta: { content?: infer C };
  }>;
} ? C : never;

type Result = ExtractContent<OpenAIChatChunk>; // 推导为 string | undefined
```

---

### 核心代码片段（极简记法）

```typescript
// 通用路径提取工具类型
type ExtractDeltaContent<T> = T extends { choices: [{ delta: { content: infer Text } }] }
  ? Text
  : T extends { choices: Array<{ delta: { content?: infer Text } }> }
  ? Text
  : never;

// 测试推导
type MyChunk = { choices: [{ delta: { content: string } }] };
type ContentType = ExtractDeltaContent<MyChunk>; // 结果是 string
```

---

### 面试加分项

- **穿透 Promise 与 AsyncIterable**：在流式客户端中，接口往往返回 `Promise<AsyncIterable<Chunk>>`。可结合 `Awaited<T>` 与 `infer` 编写 `UnwrapStream<T>` 工具类型，一步到位提取出最终消费的 Chunk 类型。
