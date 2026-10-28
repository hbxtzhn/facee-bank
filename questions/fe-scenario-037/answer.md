### 一句话总结

最优雅标准的原生 API 是 **`b.contains(a)`**（若 a 是 b 的后代或 a 就是 b 本身则返回 `true`）；反向查找可以使用 **`a.closest(selector)`** 向上溯源祖先；亦可利用底层高阶位运算符 **`b.compareDocumentPosition(a)`** 进行精确的节点拓扑位置判定。

---

### 详细回答

#### 1. 方案一：Node.contains()（最常用，推荐）
- `b.contains(a)`；
- 返回值：布尔值；
- **注意点**：如果 `a === b`，`contains` 也会返回 `true`。若业务要求必须是“纯子孙后代（排除自身）”，需要补一行判定：`b !== a && b.contains(a)`。

#### 2. 方案二：Element.closest()（反向查询）
- 从自身开始逐级向上查找匹配指定 CSS 选择器的最近祖先：
  ```javascript
  const isDescendant = !!a.closest('#parent-b-id');
  ```

#### 3. 方案三：compareDocumentPosition（位掩码高精判断）
- 返回两个节点相对位置的二进制位掩码：
  - `DOCUMENT_POSITION_CONTAINED_BY (16)`：代表被包含；
  ```javascript
  const isChild = !!(b.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_CONTAINED_BY);
  ```

---

### 核心代码片段（极简记法）

```javascript
// 判定 a 是否为 b 的真后代节点
function isStrictChild(a, b) {
  return a !== b && b.contains(a);
}
```

---

### 面试加分项

- **手写向上递归遍历（Polyfill 思想）**：如果面试官追问“禁止用自带 API 手写实现”，可基于 `parentNode` 编写极简的 `while` 循环向上回溯：
  ```javascript
  function isChildManual(a, b) {
    let node = a.parentNode;
    while (node) {
      if (node === b) return true;
      node = node.parentNode;
    }
    return false;
  }
  ```
