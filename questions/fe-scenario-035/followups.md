## 追问 1：为什么 Axios 废弃了之前的 CancelToken？

**回答要点**：
`CancelToken` 是早年基于提案（TC39 已废弃提案）的非标准实现；而 `AbortController` 已经成为 W3C / WHATWG 官方认可的标准 Web API（Node.js、Fetch、Web Worker 通用），顺应行业标准统一生态。

---

## 追问 2：一个 AbortController 实例可以同时取消多个并发的请求吗？

**回答要点**：
完全可以！
只需将同一个 `controller.signal` 传递给 10 个不同的 Axios 请求；一旦调用 `controller.abort()`，所有绑定了该信号的请求会瞬间被一次性批量全部掐断。
