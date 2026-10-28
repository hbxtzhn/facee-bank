## 追问 1：如何拿到 setState 之后更新完毕的最新 DOM？

**回答要点**：
- 函数组件：在依赖项包含该 state 的 **`useEffect`** 中获取；
- 类组件：在 `this.setState(newState, callback)` 的第 2 个参数回调函数中获取。

---

## 追问 2：为什么 React 官方坚决不在函数组件的 useState 中提供像类组件那样的第 2 个 callback 参数？

**回答要点**：
因为在并发渲染（Concurrent Mode）下，渲染任务可能被挂起或中断，回调时机变得难以预测；且函数组件推崇声明式响应，所有“状态改变后的副作用”统一在 `useEffect` 中处理符合架构纯洁性。
