### 一句话总结

声明兼容 SSE、WebSocket 和 Fetch Stream 的通用流式接口，核心是利用 **`AsyncIterable<T>`（异步可迭代对象）** 屏蔽底层通信协议差异，配合**事件回调泛型接口（OnChunk / OnError / OnComplete）**与 **`AbortSignal`** 实现统一的流式生命周期抽象。

---

### 详细回答

#### 1. 为什么首选 AsyncIterable 作为通用抽象？
- 现代 JavaScript/TypeScript 原生支持异步生成器与 `for await...of` 语法；
- 无论是 SSE 的 `ReadableStream`、WebSocket 的 `message` 事件，还是 Node.js Stream，均能轻量包装为 `AsyncIterable<Chunk>`；
- 业务消费层无需关心底层是长轮询、SSE 还是 WS，只需统一 `for await (const chunk of stream)`。

#### 2. 通用流式控制器接口设计
```typescript
interface StreamClientConfig {
  url: string;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

interface StreamResponse<TData, TError = Error> {
  // 1. 异步迭代器语法糖
  [Symbol.asyncIterator](): AsyncIterator<TData>;
  // 2. 事件监听式回调
  on(event: 'chunk', listener: (data: TData) => void): this;
  on(event: 'error', listener: (err: TError) => void): this;
  on(event: 'end', listener: () => void): this;
  // 3. 主动中断能力
  cancel(): void;
}
```

---

### 核心代码片段（极简记法）

```typescript
// 通用传输适配层签名
type TransportType = 'sse' | 'websocket' | 'fetch-stream';

interface UniversalStreamRequest<TPayload, TChunk> {
  transport: TransportType;
  endpoint: string;
  payload: TPayload;
  onChunk: (chunk: TChunk) => void;
  onError: (error: Error) => void;
  signal?: AbortSignal;
}

// 统一消费示例
function createStream<P, C>(req: UniversalStreamRequest<P, C>): () => void {
  // 内部根据 transport 分流为 SSE 或 WS 实现，外部 API 保持一致
  return () => { /* 取消订阅 */ };
}
```

---

### 面试加分项

- **泛型约束错误结构**：很多团队把错误类型写成 `any`。应该泛型约束 `TError = { code: string; message: string; retryable: boolean }`，在类型层面指导前端决定是否发起自动重试。
