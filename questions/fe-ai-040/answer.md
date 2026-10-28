### 一句话总结

多模态分阶段渲染采用**“渐进式流水线（Progressive Pipeline）”**。第一阶段（0ms）立即吐出**流式纯文本骨架**满足用户即时可读；第二阶段渲染**轻量表格与数据预览**；第三阶段（延迟异步加载）以**低分辨率占位图（LQIP）+ 异步 Web Worker 解析重图表**，避免资源集中竞争阻塞首屏呈现。

---

### 详细回答

#### 1. 核心瓶颈：为什么多模态会拖垮首屏？
- 生成的图片动辄数 MB，表格和复杂渲染引擎（如 ECharts）脚本体积庞大；
- 若必须等所有模态就绪后一次性全量挂载，用户会面对长达 5~8 秒的白屏或卡顿。

#### 2. 三阶段渲染流水线
- **阶段 1：首字文本秒出（TTFT）**：
  纯文本渲染成本极低，优先通过流式展示结论摘要；
- **阶段 2：交互结构化数据（表格与代码）**：
  收到数据先用极简原生 HTML `<table>` 快速呈现，后续空闲时再注水（Hydrate）为支持排序过滤的高级表格组件；
- **阶段 3：重资源异步加载（图片与图表）**：
  - 图片先渲染带模糊滤镜的 Low-Quality 占位图或骨架图；
  - 图表采用动态 `import()` 懒加载核心图表库，首屏不打包多余第三方重体积脚本。

---

### 核心代码片段（极简记法）

```javascript
function MultiModalResponse({ data }) {
  return (
    <>
      {/* 阶段 1：纯文本即时渲染 */}
      <p>{data.summaryText}</p>

      {/* 阶段 2：表格按需挂载 */}
      {data.tableData && <SimpleTable data={data.tableData} />}

      {/* 阶段 3：图片懒加载 + 占位 */}
      {data.imageUrl && (
        <img 
          src={data.imageUrl} 
          loading="lazy" 
          placeholder="blur" 
          alt="AI Generated" 
        />
      )}
    </>
  );
}
```

---

### 面试加分项

- **预知宽高占位防 CLS（Cumulative Layout Shift）**：大模型生成图片时，在元数据中提前下发图片原始宽高比（如 `aspect_ratio: "16:9"`）。前端在图片未加载完成前通过 CSS `aspect-ratio` 预留出精准空白高度，彻底杜绝图片加载完毕时页面突然跳动的恶劣视觉抖动。
