## 追问 1：Web Worker 中可以使用 DOM 解析库吗？

**回答要点**：
Worker 内部没有 `window` 和 `document`，不能直接使用依赖真实 DOM 的操作（如 `document.createElement`）。
但纯 JavaScript 实现的 AST 解析库（如 `marked`、`json5`）完全可以在 Worker 中顺畅运行。

---

## 追问 2：如果主线程组件销毁了，如何销毁 Worker 中的流式请求？

**回答要点**：
主线程向 Worker 发送 `{ type: 'ABORT', streamId }`，Worker 内部触发对应的 `AbortController.abort()`；若该 Worker 是一次性专属 Worker，直接调用 `worker.terminate()` 瞬间强制终结子线程。
