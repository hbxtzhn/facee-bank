## 追问 1：在 React 组件中如何封装一个通用的 useWindowSize Hook？

**回答要点**：
基于 `useSyncExternalStore`（React 18 最优解）或 `useState` + `useEffect`；在 `useEffect` 中监听 `resize` 事件并在清理函数中执行 `removeEventListener`。

---

## 追问 2：SSR（服务端渲染如 Next.js）下执行 window.innerWidth 报错 window is not defined 怎么破？

**回答要点**：
在服务端渲染期间 `window` 对象不存在。
必须在初始化状态时提供默认安全兜底值（如 `{ width: 1920, height: 1080 }`），并在客户端挂载后的 `useEffect` 中才读取真实的 `window.innerWidth` 更新状态。
