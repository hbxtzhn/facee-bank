## 追问 1：如果 a 元素处于 Shadow DOM 内部，外部的 b.contains(a) 能生效吗？

**回答要点**：
失效！
Shadow DOM 构建了独立的封装边界。若 a 处于 shadowRoot 内部，外部祖先的 `contains` 会直接返回 `false`。必须通过 `event.composedPath()` 获取真实的冒泡物理路径。

---

## 追问 2：如果 a 节点是一个文本节点（TextNode），contains API 依然有效吗？

**回答要点**：
依然有效！
`contains` 挂载在 `Node.prototype` 上，对元素节点（Element）、文本节点（Text）和注释节点（Comment）均完全通用。
