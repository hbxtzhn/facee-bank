### 一句话总结

实时统计窗口大小采用 **`window.addEventListener('resize', throttledHandler)` 结合 `window.innerWidth` / `innerHeight`**。由于拖拽调整浏览器边框时每秒可能触发数百次 resize 事件，必须使用 **`requestAnimationFrame` 或 100ms 节流（Throttle）** 控制执行频率；若需将数据持久上报至后台，则必须结合 **防抖（Debounce）** 在用户停止调整窗口 1 秒后再执行网络提交。

---

### 详细回答

#### 1. 采集字段标准（视口宽高的选择）
- **`window.innerWidth / innerHeight`**：包含滚动条的可视视口大小（响应式布局最核心参考标准）；
- **`document.documentElement.clientWidth / clientHeight`**：不包含滚动条的页面根元素实际排版宽度；
- **`window.screen.width / height`**：显示器物理分辨率大小（全屏尺寸，不变）。

#### 2. 高频事件的性能灾难与治理
- 用户拖拽窗口边角时，resize 事件是以屏幕刷新率（60Hz~144Hz）疯狂派发的；
- 若在回调函数中频繁读取 DOM 或执行复杂布局重算，主线程会剧烈掉帧；
- **治理法则**：
  - 本地 UI 响应：用 `requestAnimationFrame` 限制为最高 60fps 单帧一次；
  - 远程统计上报：用 `debounce(reportApi, 1000)`，仅在用户拖拽停下后上报一次最终尺寸。

---

### 核心代码片段（极简记法）

```javascript
// 基于 requestAnimationFrame 实现极致流畅的节流监听
let isTicking = false;

window.addEventListener('resize', () => {
  if (!isTicking) {
    window.requestAnimationFrame(() => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      console.log(`当前视口: ${w} x ${h}`);
      isTicking = false;
    });
    isTicking = true;
  }
});
```

---

### 面试加分项

- **移动端软键盘弹起的避坑（VisualViewport API）**：在移动端，用户点击输入框唤醒软键盘时，`window.innerHeight` 在某些 Android 机型上会剧烈变小，在 iOS 上则可能不变。现代标准推荐使用 **`window.visualViewport.height`** 监听真实的视觉视口变化，完美应对键盘弹起遮挡问题。
