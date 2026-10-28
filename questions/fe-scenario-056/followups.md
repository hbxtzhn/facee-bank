## 追问 1：如果一个 input 没有写 onChange，只写了 value="abc"，会发生什么？

**回答要点**：
输入框会被锁死！用户在键盘上敲任何字符都无法输入，且 React 控制台会抛出明显的警告：“You provided a `value` prop to a form field without an `onChange` handler”。

---

## 追问 2： defaultValue 和 value 属性有何根本区别？

**回答要点**：
`defaultValue` 仅在组件初次 mount 时作为原生 DOM 的初始占位值赋值一次，后续它的变动不会影响输入框状态；而 `value` 始终与输入框当前显示的文本保持实时双向绑定。
