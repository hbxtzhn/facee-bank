### 一句话总结

在 React 源码底层，**`setState` 本身始终是纯同步代码执行**。所谓的“异步”是指 React 会**将多次状态变更合并并延迟推迟到批处理（Batching）阶段统一刷新组件，以达到避免重复渲染的性能优化目的**。在 **React 18 之前**，原生事件与 `setTimeout` 中的 setState 会逃逸出批处理表现为同步；而在 **React 18+** 中，引入了**全自动批处理（Automatic Batching）**，无论在 Promise、定时器还是原生事件中，一律全场景默认执行批处理（表现为异步）。

---

### 详细回答

#### 1. 为什么 React 要设计成“表现为异步”？
- 若每次调用 `setState` 立即同步执行一次完整 DOM Diff 与渲染，连续调用 3 次就会触发 3 次昂贵重绘；
- React 收集一轮事件处理函数中的所有修改，一次性只渲染一次（批量合并）。

#### 2. React 17 及以前的分界线
- **在 React 合成事件与生命周期中**：处于 React 的执行上下文中，合并批处理，表现为**异步**；
- **在 `setTimeout`、`Promise.then` 或原生 `addEventListener` 中**：脱离了 React 上下文，**表现为同步**（调用后下一行代码立即能拿到最新 state）。

#### 3. React 18 的重大升级：全自动批处理
- React 18 基于根容器 `createRoot`，将批处理范围扩大到了**全宇宙所有场景**；
- 哪怕在 `setTimeout` 内部连续两次 `setState`，也只会合并触发一次渲染！

---

### 核心代码片段（极简记法）

```javascript
// React 18 全自动批处理演示
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React 18 中，以上两行合并为 1 次重绘！(React 17 会触发 2 次)
}, 1000);

// 若在 React 18 中强行要求立即同步渲染，使用 flushSync
import { flushSync } from 'react-dom';
flushSync(() => { setCount(c => c + 1); }); // 立即同步更新 DOM
```

---

### 面试加分项

- **对 setState 传入函数 vs 传入对象的区别**：连续调用 `setCount(count + 1)` 3 次，因为每次读取的都是同一个作用域里的固定快照值，结果只增加 1；而连续调用 `setCount(c => c + 1)` 3 次，React 会将这些 Updater 函数放入执行队列串行累加，最终结果正确增加 3。
