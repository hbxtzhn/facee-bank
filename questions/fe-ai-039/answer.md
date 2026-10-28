### 一句话总结

核心在于**“稳定引用传参 + 细粒度更新隔离 + 自定义 memo 比对器”**。将消息项提取为独立子组件并用 `React.memo` 包裹，自定义对比仅当自身 `content` 或 `status` 变更时才重刷；所有透传给子组件的事件回调（如“重新生成”、“复制”）必须通过 `useCallback` 稳定函数引用，避免父组件每收到一个 Token 都让全量历史卡片做无谓的虚拟 DOM Diff。

---

### 详细回答

#### 1. 为什么普通的 React.memo 经常失效？
- **内联匿名函数破坏引用**：父组件写了 `<MessageItem onCopy={() => copy(m.id)} />`，父组件每渲染一次都会创建一个新函数对象，`React.memo` 浅比较判定 props 发生变化，全量重刷！
- **传递了冗余的父组件状态**：把整个大对象甚至 `streamingId` 传下去。

#### 2. 标准规范写法
1. **稳定事件回调**：使用 `useCallback` 包裹，配合参数传递或者将状态移入状态库；
2. **精准对比（arePropsEqual）**：
   ```javascript
   const MessageItem = React.memo(MessageItemComponent, (prev, next) => {
     return prev.message.id === next.message.id &&
            prev.message.content === next.message.content &&
            prev.message.status === next.message.status;
   });
   ```

---

### 核心代码片段（极简记法）

```javascript
// 1. 纯净子组件并锁定比对
const MessageItem = React.memo(({ id, content, onRegenerate }) => {
  return (
    <div>
      <Markdown>{content}</Markdown>
      <button onClick={() => onRegenerate(id)}>重试</button>
    </div>
  );
});

// 2. 父组件保证回调不变
function ChatList({ messages }) {
  const handleRegenerate = useCallback((id) => {
    retryMessage(id);
  }, []); // 依赖项为空，引用永久稳定

  return messages.map(msg => (
    <MessageItem key={msg.id} id={msg.id} content={msg.content} onRegenerate={handleRegenerate} />
  ));
}
```

---

### 面试加分项

- **useEvent 提案模式**：对于回调内部需要读取动态状态又想保持函数引用不变的场景，使用 `useEvent`（或通过 `useRef` 保存回调本体），彻底解除 useCallback 必须配置一堆依赖项的烦恼。
