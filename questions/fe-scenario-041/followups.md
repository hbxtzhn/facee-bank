## 追问 1：flex 属性的单值写法中，flex: initial 代表什么？

**回答要点**：
`flex: initial` 等价于 `flex: 0 1 auto`（不放大、可缩小、尺寸依内容而定），这也是任何 flex 子项未设置 flex 时的浏览器原生默认值。

---

## 追问 2：flex-basis 的优先级与 width 相比谁更高？

**回答要点**：
在 Flex 布局的主轴方向上，`flex-basis` 的优先级**高于 `width`**。若同时设置了 `width: 200px` 与 `flex-basis: 100px`，浏览器最终以 `flex-basis` 的 100px 作为基准分配尺寸。
