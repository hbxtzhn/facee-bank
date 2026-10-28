## 追问 1：如果 useCallback 的依赖项写空数组 []，但在函数内部读取了外部组件的 count 变量，会发生什么？

**回答要点**：
会发生**闭包陷阱（Stale Closure）**！
因为函数只在初次挂载时被创建一次，永远锁定了初次渲染时 `count = 0` 的快照值，后续无论外部 count 怎么变化，函数内部打印的永远是旧值 0。

---

## 追问 2：React Compiler（React 忘却编译器）会如何改变这一切？

**回答要点**：
React 19 推出的 React Compiler 能在构建期自动分析 AST 并精准注入依赖缓存，未来开发者将无需手动编写一行 `useMemo` 或 `useCallback`，从底层彻底根除心智负担。
