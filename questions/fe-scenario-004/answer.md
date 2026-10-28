### 一句话总结

电梯导航包含**“双向联动（滚动页面高亮导航菜单 + 点击菜单平滑滚动至对应楼层）”**。推荐采用 **`IntersectionObserver`（交叉观察器）替代传统滚动事件监听**，零主线程监听开销实现高精度的视口楼层探测；点击时通过 `element.scrollIntoView({ behavior: 'smooth' })` 驱动平滑过渡，并在过渡期间加锁防止滚动监听相互干扰。

---

### 详细回答

#### 1. 传统方案的痛点（scroll 事件）
- 传统做法：在 `window.onscroll` 中遍历每个楼层的 `offsetTop`，计算与 `scrollTop` 的相对位置；
- **痛点**：高频触发滚动事件，频繁读取 `offsetTop` 会导致**强制同步布局（Forced Synchronous Layout / 页面重排）**，滚动出现明显掉帧。

#### 2. 现代最优解：IntersectionObserver
- 创建一个观察器，配置 `rootMargin`（例如 `"-30% 0px -70% 0px"` 将判定线收拢在屏幕上部 1/3 区域）；
- 楼层只要触碰到该观察线，浏览器异步通知回调，自动获取当前处于活跃状态的楼层 ID，设置对应导航 Tab 高亮。

#### 3. 点击导航跳动防打架（加锁机制）
- 用户点击导航菜单 Tab 3 时，页面会平滑向下飞滚；
- 飞滚过程中会途径楼层 1 和楼层 2，若未加锁，导航栏高亮会快速在 1、2、3 之间乱跳；
- **解决**：点击时设置标志位 `isClickScrolling = true`，滚动动画结束或延迟 500ms 后再恢复滚动联动。

---

### 核心代码片段（极简记法）

```javascript
// 1. 高性能视口监听高亮
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      setActiveNavId(entry.target.id); // 激活对应导航
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });

document.querySelectorAll('.floor-section').forEach(el => observer.observe(el));

// 2. 点击平滑跳转
function scrollToFloor(id) {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}
```

---

### 面试加分项

- **吸顶效果的 CSS 纯声明式实现**：电梯导航菜单自身的粘性吸顶，直接使用纯 CSS `position: sticky; top: 0;` 即可，完全不需要任何 JS 监听高度动态切换 `fixed`，代码极简且性能极致。
