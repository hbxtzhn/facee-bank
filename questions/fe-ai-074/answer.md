### 一句话总结

请求合并采用**“微批处理队列（Micro-batching / DataLoader 模式）结合滑动时间窗口”**。前端或 BFF 中间层在收到零散的模型调用请求时，不立即发起网络传输，而是在微时间窗口（如 50ms）内将其积聚为一个批次，打包为单个 Batch 请求合并喂给大模型或向量模型，计算完毕后拆解回发给各自调用者，大幅提升并发吞吐量并均摊网络握手开销。

---

### 详细回答

#### 1. 适用场景：什么请求能合并？什么不能合并？
- **不能合并**：交互式实时流式多轮对话（用户等待极敏感，强依赖单人上下文）；
- **极度适合合并（吞吐敏感型）**：
  - 批量文本向量化（Batch Embeddings）；
  - 批量审核过滤（Batch Content Moderation）；
  - 多个小模块的轻量分类判断（如“判断这 5 个句子的情感倾向”）。

#### 2. 微批处理核心算法机制
1. **收集窗口**：利用 `setTimeout` 延迟 50ms，收集期间所有进入队列的单个任务 Promise；
2. **容量阈值**：若在 50ms 内收集数量达到最大容量（如 20 条），提前触发立即发车；
3. **单请求批量化**：调用 `openai.embeddings.create({ input: textsArray })`；
4. **结果派发**：根据原始序号将结果分别 resolve 给对应的待决 Promise。

---

### 核心代码片段（极简记法）

```javascript
class BatchEmbeddingQueue {
  constructor(batchSize = 10, delayMs = 50) {
    this.batchSize = batchSize;
    this.delayMs = delayMs;
    this.queue = [];
    this.timer = null;
  }

  add(text) {
    return new Promise((resolve, reject) => {
      this.queue.push({ text, resolve, reject });
      if (this.queue.length >= this.batchSize) this.flush();
      else if (!this.timer) this.timer = setTimeout(() => this.flush(), this.delayMs);
    });
  }

  async flush() {
    clearTimeout(this.timer);
    this.timer = null;
    const batch = this.queue.splice(0, this.batchSize);
    if (!batch.length) return;

    try {
      const results = await callBatchAPI(batch.map(b => b.text));
      batch.forEach((item, i) => item.resolve(results[i]));
    } catch (err) {
      batch.forEach(item => item.reject(err));
    }
  }
}
```

---

### 面试加分项

- **对 Token 成本的节省机制认知**：指出请求合并除了节省 HTTP 连接建立开销外，在使用大模型批量处理相同前置背景的问题时，能充分命中现代大模型推理引擎的 **Prefix Caching（前缀 KV 缓存共享）**，从而享受官方高达 50%~80% 的输入 Token 计费折扣。
