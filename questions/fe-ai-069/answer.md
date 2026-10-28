### 一句话总结

构建优化采用**“动态异步导入按需分包（Dynamic Chunking） + ESM 深度 Tree Shaking + 构建与浏览器双层持久缓存”**。将巨型依赖（Monaco Editor 代码编辑器、Mermaid 架构图、KaTeX 数学排版）全部隔离为独立异步 Chunk，利用动态 `import()` 按需拉取；配置稳定的 `[contenthash]` 结合 Vite 底层的 Rollup 消除无用导出，将首屏主 JS 体积削减 70% 以上。

---

### 详细回答

#### 1. 痛点：AI 前端应用的“体积刺客”
- 一个完整的 AI 应用往往集成了：代码高亮库（Highlight.js / Prism）、富文本/语法树（Remark / Unified）、数学公式（KaTeX）、矢量绘图（Mermaid/ECharts）；
- 若全打包在 `index.js`，首屏体积轻松突破 5MB，弱网下加载需 10 秒以上。

#### 2. 代码分割最佳实践（manualChunks）
- 在 Vite 中通过 `rollupOptions.output.manualChunks` 明确分包：
  - 核心骨架（React + Zustand）：打入 `vendor`；
  - 语法高亮引擎：打入 `async-highlight`；
  - 图表引擎：打入 `async-charts`。

#### 3. 生产级持久缓存（Long-term Cache）
- 输出文件名规范：`[name].[contenthash:8].js`；
- Nginx 对带 hash 的静态文件配置永久强缓存：`Cache-Control: public, max-age=31536000, immutable`；
- `index.html` 配置协商缓存：`Cache-Control: no-cache`，发版后秒级生效。

---

### 核心代码片段（极简记法）

```javascript
// vite.config.js 深度分包配置
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'markdown-vendor': ['marked', 'dompurify'],
          'chart-vendor': ['mermaid', 'echarts'],
          'editor-vendor': ['monaco-editor']
        }
      }
    }
  }
});

// 组件内动态异步按需拉取
const HeavyMermaid = React.lazy(() => import('./HeavyMermaidBlock'));
```

---

### 面试加分项

- **预加载策略（Modulepreload）**：现代 Vite 默认会在 HTML 中注入 `<link rel="modulepreload">`。在首屏加载空闲时，浏览器会在后台静默预拉取 Markdown 解析器 Chunk，等用户真正收到首个 Token 时该模块已在内存就绪，消除动态 import 的网络等待。
