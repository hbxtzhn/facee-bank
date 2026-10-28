### 一句话总结

超长 AI 内容渲染的核心是**“动态高度虚拟列表（Dynamic Height Virtualization） + Markdown 块级预估缓存”**。将大文档按段落、代码块拆分为独立 Block，仅渲染可视视口及上下缓冲区内的 DOM 节点；利用 **`ResizeObserver` 动态测量真实高度更新索引偏移树**，并在流式追加时实时维持滚动锚定。

---

### 详细回答

#### 1. 为什么不能用固定高度虚拟列表？
- AI 生成的 Markdown 段落高度完全未知（短则一行标题，长则几百行代码块）；
- 必须支持**动态高度测量与预估（Estimated Height）**。

#### 2. 核心算法机制
1. **预估占位（Spacer）**：初始化时赋予每个块默认高度（如 60px），计算总容器虚拟高度；
2. **可视窗口计算**：根据滚动条的 `scrollTop`，通过二分查找计算出当前视口应该展示的起始索引 `startIndex` 和结束索引 `endIndex`；
3. **真实测量（Measure）**：节点渲染后，通过 `ResizeObserver` 采集实际 DOM 高度，修正高度字典并累加更新后续节点的位移 `offset`。

---

### 核心代码片段（极简记法）

```javascript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualAIDocument({ blocks, parentRef }) {
  const virtualizer = useVirtualizer({
    count: blocks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // 初始预估高度
    overscan: 3 // 上下多预加载 3 个块防白屏
  });

  return (
    <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
      {virtualizer.getVirtualItems().map((item) => (
        <div key={item.key} style={{ position: 'absolute', top: 0, transform: `translateY(${item.start}px)` }}>
          <MarkdownBlock content={blocks[item.index]} />
        </div>
      ))}
    </div>
  );
}
```

---

### 面试加分项

- **流式追加时的滚动锚定（Scroll Anchoring）**：在文档末尾持续吐字时，高度不断剧烈变化。必须在每次高度变动时配合 `scrollBy` 或 CSS `overflow-anchor: auto`，防止视口被新增内容顶飞。
