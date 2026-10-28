### 一句话总结

`ResizeObserver` 是浏览器提供的专门用于**高精、高性能监听“特定 DOM 元素尺寸变化”**的观察器。它摆脱了传统只能监听整个浏览器窗口（`window.onresize`）的局限，能够精准感知**由内容动态增加、CSS 动画、折叠面板展开引起的局部容器尺寸微变**，且天然经过浏览器底层的渲染循环批处理，杜绝循环依赖与死循环回流。

---

### 详细回答

#### 1. 传统 `window.onresize` 的局限
- 只能监听页面顶层窗口变化；
- 若窗口大小不变，仅仅是左侧侧边栏折叠导致右侧主画布宽度被动撑大，`window.onresize` 毫无反应；
- 传统做法是用定时器轮询检测元素的 `offsetWidth`，极其消耗 CPU。

#### 2. ResizeObserver 核心特性
- **细粒度元素级监听**：`observer.observe(targetElement)`；
- **多种盒模型尺寸报告**：
  - `contentBoxSize`：内容盒尺寸；
  - `borderBoxSize`：包含边框和内边距的边框盒尺寸；
  - `devicePixelContentBoxSize`：物理像素真实大小（用于 Canvas 消除模糊）。

#### 3. 典型应用场景
- **自适应图表（ECharts / Highcharts）**：容器变大自动调用 `chart.resize()`；
- **虚拟列表与富文本**：动态测量每个 Markdown 块的实际高度；
- **响应式容器查询（Container Queries）Polyfill**。

---

### 核心代码片段（极简记法）

```javascript
const observer = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const { width, height } = entry.contentRect;
    console.log(`元素新尺寸: ${width} x ${height}`);
  }
});

// 开始监听特定 DOM 元素
observer.observe(document.querySelector('.chart-container'));
```

---

### 面试加分项

- **控制台报错「ResizeObserver loop limit exceeded」成因与解法**：当在 ResizeObserver 的回调函数内部又同步修改了该元素的样式或 DOM 结构导致其尺寸再次改变时，浏览器检测到了循环更新并在当前帧终止继续派发以防浏览器假死。解法是将回调内的样式修改用 `requestAnimationFrame` 推迟到下一帧执行。
