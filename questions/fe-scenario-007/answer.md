### 一句话总结

`PerformanceObserver` 是现代浏览器标准的**“性能事件异步观察器”**。它废弃了旧版轮询查询 `performance.timing` 的被动模式，以**事件驱动（Event-driven）异步订阅性能时间线条目（`navigation`, `resource`, `paint`, `largest-contentful-paint`, `longtask` 等）**；不仅零轮询开销、不污染主线程，还能精准捕获 SPA 路由切换与动态加载资源的实时性能流水线。

---

### 详细回答

#### 1. 传统 `performance.timing` 的硬伤
- **静态快照**：只记录页面首次冷启动的单一时间点，SPA 单页应用后续的路由跳转完全无法体现；
- **主线程轮询开销**：必须写 `setInterval` 去轮询某些指标是否生成，极易阻塞主线程；
- **已被 W3C 标准全面废弃（Deprecated）**。

#### 2. PerformanceObserver 核心工作流
1. 实例化 `new PerformanceObserver(callback)`；
2. 调用 `observe({ type: '...', buffered: true })` 开启订阅；
3. 浏览器在特定性能事件发生时，异步批量回调传递条目列表；
4. 按需断开 `observer.disconnect()`。

#### 3. 常见监听类型清单
- `navigation`：DNS、TCP、TTFB、DOM 解析耗时；
- `paint`：FP（首次绘制）、FCP（首次内容绘制）；
- `largest-contentful-paint`：LCP 最大内容绘制；
- `first-input`：FID 首次输入延迟；
- `resource`：每一个图片、JS、CSS 资源的下载流水线。

---

### 核心代码片段（极简记法）

```javascript
// 异步捕获 FCP 与 LCP 指标
const observer = new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    if (entry.name === 'first-contentful-paint') {
      console.log('FCP 耗时:', entry.startTime);
    }
  }
});

// buffered: true 确保捕获已经发生过的事件
observer.observe({ type: 'paint', buffered: true });
```

---

### 面试加分项

- **`buffered: true` 的不可替代性**：如果监控 SDK 是异步延迟加载的，当 SDK 执行时，FP 和 FCP 早就发生完毕了。声明 `buffered: true` 会指示浏览器去自身的内部时间轴缓存区中提取并补发过去的性能条目，杜绝数据遗漏。
