## 追问 1：拖拽时鼠标移动如果经过了文字区域，会导致文字被大面积蓝色高亮选中，怎么解决？

**回答要点**：
在 `mousedown` 回调开始时调用 `e.preventDefault()` 阻止默认选择行为，并在容器样式上加上 `user-select: none;`。

---

## 追问 2：如何同时兼容移动端触摸屏（Touch）拖拽？

**回答要点**：
使用 W3C 现代标准的 **Pointer Events API**（`onpointerdown`, `onpointermove`, `onpointerup`），配合 `el.setPointerCapture(e.pointerId)`，一套代码通吃鼠标、触控笔与手指触摸。
