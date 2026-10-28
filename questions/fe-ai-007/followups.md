## 追问 1：AsyncIterable 和 RxJS Observable 在流式前端场景怎么选？

**回答要点**：
普通 AI 对话展示使用 `AsyncIterable` 最自然，零依赖原生支持；若应用包含高并发流式合并、动态多通道过滤、音视频复杂流编排，选用 RxJS 配合强大的操作符（`switchMap`、`mergeMap`）更合适。

---

## 追问 2：如果在流式传输过程中连接意外中断，AsyncIterable 如何触发终止清理？

**回答要点**：
在异步生成器内部实现 `return()` 和 `finally` 块。当外部调用 `break` 或 `AbortController.abort()` 时，运行时会自动触发生成器的 `finally`，在其中关闭 WebSocket 连接或释放 Reader 锁。
