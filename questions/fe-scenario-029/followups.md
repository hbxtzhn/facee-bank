## 追问 1：如果划选时从右向左划，Selection 和 Range 的表现有何不同？

**回答要点**：
`Selection` 能够区分划选方向：反向划选时 `anchorOffset > focusOffset`，`selection.isCollapsed` 为 false；
而 `Range` 永远会被浏览器自动归一化为正向：`range.startOffset` 永远处于左侧较小值，`endOffset` 处于右侧较大值。

---

## 追问 2：如何在输入框（<input> 或 <textarea>）中实现代码选区或光标位置读取？

**回答要点**：
表单输入元素不产生标准 DOM Range。
必须直接通过表单专有原生属性：`input.selectionStart` 与 `input.selectionEnd` 获取光标字符下标，并通过 `input.setSelectionRange(start, end)` 进行程序化选区控制。
