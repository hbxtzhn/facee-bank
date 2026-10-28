## 追问 1：在 React 外部（比如纯 JS 工具函数中），Zustand 如何读取和修改状态？

**回答要点**：
Zustand 的 Store 实例自带静态方法：直接调用 `useChatStore.getState()` 读取当前最新状态，调用 `useChatStore.setState({ ... })` 触发更新，完全不依赖 React 组件生命周期。

---

## 追问 2：为什么高频流式推流时不推荐在 Context 中直接维护消息列表？

**回答要点**：
React Context 的任何值变更都会无条件遍历触发所有消费该 Context 的子组件重新渲染，哪怕子组件使用了 `React.memo` 也会失效，导致页面出现灾难级的卡顿掉帧。
