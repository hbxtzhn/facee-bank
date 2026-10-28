## 追问 1：如果一个复杂任务中，模型同时返回了多个独立的工具调用，状态机如何处理？

**回答要点**：
使用 XState 的并行状态（Parallel States）或在 Actor 内部使用 `Promise.allSettled` 并发调度，全部完成后触发聚合事件统一流转回思考状态。

---

## 追问 2：状态机的持久化与页面刷新恢复怎么做？

**回答要点**：
XState 支持通过 `getPersistedSnapshot()` 导出状态树 JSON，刷新后传入 `createActor(machine, { snapshot })` 即可瞬间无缝恢复。
