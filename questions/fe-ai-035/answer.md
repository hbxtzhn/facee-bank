### 一句话总结

该策略属于**“富渲染与轻渲染按需降级（Content Degradation）”**。处于视口内的消息挂载完整的 React 富组件（富文本 Markdown、可编辑代码块、Mermaid 架构图、KaTeX 数学公式）；一旦滚动离开视口，自动卸载重组件并降级为**带有固定高度骨架的轻量纯文本（Plain Text）**，释放 80% 的内存与 DOM 节点。

---

### 详细回答

#### 1. 为什么全量渲染富组件会导致页面崩溃？
- Mermaid.js 图表、ECharts 实例、KaTeX 渲染树会生成成千上万个嵌套 SVG 和 DOM 节点；
- 对话进行到 50 轮时，页面 DOM 节点数突破数万个，滚动极度卡顿，内存占用达数 GB。

#### 2. IntersectionObserver 动态降级设计
- 每个消息卡片外层包裹探测器：
  ```javascript
  const { ref, inView } = useInView({ rootMargin: '200px 0px' });
  ```
- **在视口内（`inView: true`）**：渲染 `<FullRichMarkdown message={msg} />`；
- **离开视口（`inView: false`）**：
  - 记录脱离前的真实 DOM 高度（防止高度塌陷导致滚动条跳动）；
  - 替换渲染为 `<div style={{ height: recordedHeight }}>{msg.plainTextSummary}</div>`。

---

### 核心代码片段（极简记法）

```javascript
function AdaptiveMessageItem({ message }) {
  const [isInView, setIsInView] = useState(false);
  const [cachedHeight, setCachedHeight] = useState(null);
  const domRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIsInView(entry.isIntersecting);
      if (entry.isIntersecting) {
        setCachedHeight(domRef.current.offsetHeight); // 记录真实高度
      }
    }, { rootMargin: '300px' });

    observer.observe(domRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={domRef} style={{ minHeight: cachedHeight ? `${cachedHeight}px` : 'auto' }}>
      {isInView ? <HeavyMarkdownAST content={message.text} /> : <div className="plain-preview">{message.text.slice(0, 100)}...</div>}
    </div>
  );
}
```

---

### 面试加分项

- **结合 `content-visibility: auto`**：现代 Chrome 原生支持的单行 CSS 魔法：
  `content-visibility: auto; contain-intrinsic-size: 0 120px;`
  浏览器会在屏幕外自动跳过该元素的渲染与样式计算，效果与 JS 降级类似且性能更高。
