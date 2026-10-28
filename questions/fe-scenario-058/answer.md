### 一句话总结

React 18 的最核心基石是**“并发渲染机制（Concurrent Rendering）”**，它彻底告别了过去的同步不可中断渲染，赋予了 React **按优先级暂停、中断、恢复渲染任务的能力**。基于并发机制衍生出了三大杀手级特性：**全自动批处理（Automatic Batching）**、**可中断状态过渡 Hook（`useTransition` / `useDeferredValue`）**、以及**流式服务端渲染（Streaming SSR with Suspense）**。

---

### 详细回答

#### 1. 并发模式（Concurrent Mode）的底层颠覆
- **旧版痛点**：JavaScript 是单线程的，如果渲染一个包含万条 DOM 的复杂组件树耗时 100ms，期间浏览器主线程被死死霸占，用户点击输入框、打字完全毫无反应（严重掉帧假死）；
- **React 18 并发机制**：将渲染工作拆解为微小的可中断切片。当用户输入高优先级交互发生时，React 会**立即暂停当前低优先级的后台渲染，优先响应用户输入，随后在空闲时再继续渲染**。

#### 2. 杀手级 Hook：useTransition（优先级降级）
- 将一个紧急任务（如即时打字回显）与一个非紧急任务（如根据输入内容过滤千条列表）解耦拆分：
  ```javascript
  const [isPending, startTransition] = useTransition();
  // 保持打字极其丝滑，后台计算列表被降级调度
  startTransition(() => { setFilteredList(heavyFilter(keyword)); });
  ```

#### 3. 流式 SSR（Streaming SSR）
- 结合 `<Suspense>`，服务端可以先将页面的骨架 HTML 瞬间流式输出给客户端；
- 慢速的数据模块（如评论区）在服务端异步加载完成后，再以 HTML 片段形式沿同一个 HTTP 流推送到前端就地拼装。

---

### 核心代码片段（极简记法）

```javascript
import { createRoot } from 'react-dom/client';

// 开启 React 18 并发特性的统一入口
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

---

### 面试加分项

- **Strict Mode（严格模式）在开发环境执行两次渲染的目的**：很多初级开发误以为这是 Bug。必须向面试官解释：React 18 为了验证组件是否对“并发可复用状态（Offscreen 卸载与重载）”具备纯净幂等性，特意在 Dev 环境故意执行两次 mount/unmount，帮助开发者提前暴露出在 `useEffect` 中未清理事件监听和定时器的内存泄漏 Bug。
