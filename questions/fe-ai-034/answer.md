### 一句话总结

优化代码编辑器的核心是**“分层渲染（Layered Architecture） + AST 解析移入 Web Worker + 视口行级虚拟化”**。语法解析与 Linter 检查在后台 Worker 中异步执行，主线程仅按当前视口视行范围更新 DOM；将光标、文本、背景高亮和错误下划线分层独立渲染，避免单字输入引发全量重绘。

---

### 详细回答

#### 1. 痛点：Monaco / CodeMirror 为何会卡？
- 代码编辑器若每敲一个字都同步触发一次完整词法分析（Lexer）和语法树重构，当文件超过几千行时耗时达几十毫秒，导致输入延迟。

#### 2. 三大核心优化手段
1. **后台 Worker 异步高亮（Tree-sitter / TextMate）**：
   词法解析全部在子线程跑完，将结果简化为 Token 数组：`[{ line: 12, start: 4, end: 10, class: 'keyword' }]`，主线程仅做样式类名套用；
2. **行级虚拟渲染（Line Virtualization）**：
   即使文件有一万行，当前屏幕也仅渲染可视的 40~50 个 `div.line` 节点；
3. **分层绘制（Layered Canvas/DOM）**：
   - 文本层、语法高亮层、波浪线下划线层分离；
   - 错误波浪线利用纯 CSS `text-decoration` 配合 SVG 纹理绘制，杜绝手动计算绝对定位小图片。

---

### 核心代码片段（极简记法）

```javascript
// 错误波浪线纯 CSS 高性能绘制
const wavyUnderlineStyle = `
  text-decoration: underline wavy #ff4d4f;
  text-decoration-skip-ink: none; /* 避免文字字切断波浪线 */
`;
```

---

### 面试加分项

- **增量词法分析（Incremental Parsing）**：使用 Tree-sitter 等支持增量更新的解析器。用户在第 50 行输入一个字符，只重新解析受影响的局部 AST 节点，复用其余 99% 的旧语法树。
