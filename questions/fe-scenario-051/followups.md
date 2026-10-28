## 追问 1：被 Keep-Alive 缓存的组件，原本绑定的 useEffect 会被触发清理吗？

**回答要点**：
如果采用 display: none 方案，组件根本没有真正 unmount，因此不会触发 `useEffect` 的清理函数；
需要自定义生命周期 Hook（如 `useActivate` / `useDeactivate`）通过事件驱动模拟页面的进入与离开。

---

## 追问 2：缓存页面重新激活时，如何准确恢复页面原先的滚动条位置？

**回答要点**：
在离开页面时监听 `scroll` 事件记录当时的 `window.scrollY`；
重新激活时在 `requestAnimationFrame` 回调中调用 `window.scrollTo(0, cachedScrollY)` 丝滑还原。
