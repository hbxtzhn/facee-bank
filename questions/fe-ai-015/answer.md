### 一句话总结

高频流式输出的核心痛点是**昂贵的文本渲染阻塞了用户的紧急交互**。利用 React 18 并发特性的时间切片机制，通过 **`useTransition`** 或 **`useDeferredValue`** 将大段 Markdown/代码高亮降级为**“低优先级过渡更新”**，优先保障用户输入、页面滚动和按钮点击的 60fps 响应，并在高频打断时丢弃过期帧。

---

### 详细回答

#### 1. React 18 并发渲染与优先级调度
- **紧急更新（Urgent Updates）**：直接影响用户即时交互的动作（如输入框打字、点击“停止生成”、鼠标悬停），要求立即响应（0~16ms）。
- **过渡更新（Transition Updates）**：视图转换、大段富文本重绘等（如 AI 流式文本追加），用户对几毫秒的微延迟不敏感。
- **并发打断机制**：当主线程正在渲染沉重的 Markdown 时，若用户突然在输入框敲入一个字符，React 会立即暂停当前的 Markdown 渲染，优先处理输入框更新，避免界面假死。

#### 2. useTransition：在更新发起端降级
- 适合当你**掌控状态更新动作源头**时使用。
- 将流式消息的 `setStreamingContent` 包裹在 `startTransition` 中：
  ```javascript
  const [isPending, startTransition] = useTransition();

  function onReceiveChunk(newText) {
    startTransition(() => {
      setFullText(prev => prev + newText);
    });
  }
  ```

#### 3. useDeferredValue：在数据消费端延迟
- 传入高频变化的文本，返回延迟更新的值：
  ```javascript
  function MessageItem({ rawContent }) {
    const deferredContent = useDeferredValue(rawContent);
    return <ExpensiveMarkdown content={deferredContent} />;
  }
  ```

---

### 核心代码片段（极简记法）

```javascript
function AIChat() {
  const [streamText, setStreamText] = useState('');
  const [, startTransition] = useTransition();
  const deferredText = useDeferredValue(streamText);

  function handleChunk(chunk) {
    startTransition(() => setStreamText(prev => prev + chunk));
  }

  return (
    <>
      <FastInput /> {/* 用户打字永远流畅 */}
      <ExpensiveMarkdown content={deferredText} />
    </>
  );
}
```

---

### 面试加分项

- **节流与调度双管齐下**：`useTransition` 解决的是**调度优先级**，无法消除实际的 CPU 运算总量。在极高频推送下（如每秒 100+ chunk），仍需在网络接收层配合 `requestAnimationFrame` 做 16ms 批处理节流，双剑合璧效果最好。
