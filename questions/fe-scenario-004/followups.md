## 追问 1：如果页面最底部最后一个楼层内容高度很矮（比如只有 200px），怎么滚它都无法到达视口顶部判定线，怎么让它高亮？

**回答要点**：
边界处理：当检测到滚动条已经触底（`scrollTop + clientHeight >= scrollHeight - 5`）时，强制无条件将最后一个导航菜单标记为高亮状态。

---

## 追问 2：CSS 的 scroll-behavior: smooth 在旧版浏览器兼容性不佳怎么办？

**回答要点**：
引入开源微型 Polyfill（如 `smoothscroll-polyfill`），或基于 `requestAnimationFrame` 自研结合缓动曲线（Easing function）的平滑位移动画函数。
