### 一句话总结

富文本划词底层的物理层依赖浏览器原生的 **`Selection`（选区集合）与 `Range`（连续文本范围）对象**，其在逻辑层抽象为**“基于虚拟文档模型（如 Slate / ProseMirror 的绝对字符偏移量）的精准路径定位”**。通过获取起止文本节点的 `(anchorNode, anchorOffset)` 到 `(focusNode, focusOffset)`，将物理 DOM 节点映射为富文本 AST 树上的数据范围，实现精准划词高亮与样式包裹。

---

### 详细回答

#### 1. 浏览器原生选区三剑客
- **`Selection`**：用户选中的整体表示（`window.getSelection()`）；
- **`Anchor（锚点）`**：鼠标按下的起始位置（包含对应 DOM 文本节点与字符偏移量）；
- **`Focus（焦点）`**：鼠标释放或拖拽移动的终点（支持从右往左反向划选）；
- **`Range`**：一个规范化的、始终由左向右包含 `startContainer` 到 `endContainer` 的文本片段。

#### 2. 原生 DOM 划词修改样式的传统做法（DOM 操作）
- 获取 `range = selection.getRangeAt(0)`；
- 创建包裹元素：`const span = document.createElement('span'); span.className = 'highlight';`；
- 执行环绕：`range.surroundContents(span)`。
- **致命缺陷**：若用户划选跨越了标签边界（比如选了半个加粗段落和半个普通段落），`surroundContents` 会直接抛出 DOMException 异常崩溃！

#### 3. 现代富文本引擎（ProseMirror / Slate）的抽象映射
- **绝不直接操作不可靠的 DOM Range！**
- 内部建立严格的线性坐标系：文档中每一个字符对应一个单调递增的绝对位置索引（Position）；
- 划选时将 DOM Range 转换为内部状态 `{ from: 42, to: 88 }`；
- 在纯数据层面生成一条不可变的 `Transaction`，重新渲染出合法的虚拟 DOM 树，彻底消除跨标签撕裂问题。

---

### 核心代码片段（极简记法）

```javascript
// 获取划词选区与位置
const selection = window.getSelection();
if (selection.rangeCount > 0) {
  const range = selection.getRangeAt(0);
  console.log('起始节点:', range.startContainer, '起始偏移:', range.startOffset);
  console.log('结束节点:', range.endContainer, '结束偏移:', range.endOffset);
}
```

---

### 面试加分项

- **划词状态的持久化与恢复（Highlight Persistence）**：如果需要将用户的划词高亮保存到后端并在下次打开时还原，绝不能存易变的 DOM XPath。应结合字符绝对偏移（Character Offsets）或使用 DOM 序列化开源标准库（如 `web-highlighter`），记录前缀锚文本（Contextual Anchor）做容错模糊对齐。
