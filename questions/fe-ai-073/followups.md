## 追问 1：在执行 LCEL 链的过程中，如何实现取消正在运行的流式生成？

**回答要点**：
在调用 `.invoke()` 或 `.stream()` 时，第二个可选配置参数传入包含 `signal` 的对象：
`await chain.stream({ topic: '...' }, { signal: abortController.signal })`，即可直接中断链路中的底层网络请求。

---

## 追问 2：链中的某个中间步骤（如知识库检索）如果抛错，整条链如何容错？

**回答要点**：
使用 LangChain 提供的 `.withFallbacks([fallbackChain])` 方法声明备选链，当主链中的节点执行崩溃时自动无缝降级到备选链继续执行。
