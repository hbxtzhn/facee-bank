## 追问 1：组件销毁时，如何正确释放 ResizeObserver？

**回答要点**：
调用 `observer.unobserve(targetElement)` 取消特定元素监听，或调用 `observer.disconnect()` 彻底清空所有监听器，防止闭包引发组件内存泄漏。

---

## 追问 2：Canvas 在高清屏（Retina）上缩放容易发虚模糊，ResizeObserver 怎么解决？

**回答要点**：
利用 `entry.devicePixelContentBoxSize`：直接获取物理像素级别的宽度和高度设置给 `canvas.width` 和 `canvas.height`，彻底消除由于 DPR 换算舍入误差带来的图像模糊。
