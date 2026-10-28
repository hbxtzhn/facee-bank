## 追问 1：手指横向滑动轮播图时，容易误触发下拉刷新，怎么避免手势冲突？

**回答要点**：
在 `touchmove` 中计算 X 轴与 Y 轴的移动绝对值差量：
若 `Math.abs(deltaX) > Math.abs(deltaY)`，说明用户意图是横向滑动，立即放弃下拉刷新逻辑，完全交给横向手势处理。

---

## 追问 2：移动端使用 transform 位移实现下拉，如何利用 GPU 硬件加速？

**回答要点**：
使用 `transform: translate3d(0, y, 0)` 或在元素样式中声明 `will-change: transform`，强制提升为独立的 GPU 合成层（Compositing Layer），杜绝主线程重排，保持 60fps 丝滑。
