## 追问 1：发现页面存在 200ms 的长任务，前端有哪些立竿见影的优化手段？

**回答要点**：
1. **时间切片（Time Slicing）**：用 `requestIdleCallback`、`MessageChannel` 或 `scheduler.yield()` 将大循环拆成小片段；
2. **多线程卸载**：把耗时的数据处理、复杂加解密移入 Web Worker；
3. **防抖节流**：避免高频事件触发连环重算。

---

## 追问 2：PerformanceObserver 监听时，如果长任务发生在 observer 初始化之前，能捕获到吗？

**回答要点**：
在配置项中开启 **`buffered: true`**：
`observer.observe({ type: 'longtask', buffered: true })`；
浏览器会将初始化之前已经在缓冲区里记录的历史长任务一并回放给回调函数。
