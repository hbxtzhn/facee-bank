### 一句话总结

大型 AI 应用推荐使用 **Zustand 结合切片模式（Slice Pattern）与 Immer 中间件**。将状态解耦为 `chatSlice`（消息树与流式增量）、`taskSlice`（后台异步推理队列与状态机）和 `settingsSlice`（模型参数与本地持久化），通过**细粒度选择器（Selectors）**订阅局部状态，避免流式吐字触发全页面重渲染。

---

### 详细回答

#### 1. 为什么 Zustand 比传统 Redux 更适合流式 AI 应用？
- **零样板代码**：无需编写冗长的 Action Types 和 Reducer，直接通过 Action 函数就地更新；
- **支持瞬态更新（Transient Updates）**：流式推送每秒 30 次，Zustand 允许绕过 React 重新渲染直接通过 `getState()` 或订阅监听修改 DOM，性能极高；
- **闭包安全与原生异步支持**：在异步 Stream 流中可以随时 `get()` 读取最新状态，杜绝闭包陷阱。

#### 2. 切片架构（Slice Pattern）模块划分
- **`chatSlice`**：存储当前激活会话的 `messages` 列表、当前正在流式追加的 `activeMessageId` 与 Buffer；
- **`taskSlice`**：管理并发任务池，记录正在进行的后台 Agent 任务及其进度与 `AbortController`；
- **`settingsSlice`**：用户偏好、当前选定模型、温度参数，配合 `persist` 中间件自动落盘 `localStorage`。

---

### 核心代码片段（极简记法）

```javascript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export const useChatStore = create(immer((set) => ({
  messages: [],
  // 增量流式更新（结合 Immer 避免深拷贝性能开销）
  appendChunk: (msgId, chunk) => set((state) => {
    const msg = state.messages.find(m => m.id === msgId);
    if (msg) msg.content += chunk;
  })
})));

// 消费端使用细粒度选择器，只有该字段变动才重渲染
const content = useChatStore(state => state.messages.find(m => m.id === id)?.content);
```

---

### 面试加分项

- **选择器浅比较（shallow）**：在组件消费时使用 `useChatStore(selectSubState, shallow)`，避免每次生成新对象引用导致的组件无效重刷。
