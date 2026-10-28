## 追问 1：PerformanceObserver 监听 resource 资源耗时时，跨域的 CDN 静态脚本拿不到详细的 TCP/DNS 时间，全是 0，为什么？

**回答要点**：
浏览器的安全隐私保护限制（Timing-Allow-Origin）。
若 CDN 响应头中未配置 `Timing-Allow-Origin: *`，浏览器出于安全原因会将资源请求细分的 redirect、DNS、TCP、SSL 等敏感网络耗时字段全部抹零，只暴露总时长。

---

## 追问 2：PerformanceObserver 本身会占用主线程性能吗？

**回答要点**：
开销极低。
浏览器底层会在 C++ 内核层异步排队收集指标，仅在每帧渲染间隙或空闲时批量触发一次 JS 回调，相比手动高频计算 `performance.getEntries()` 节约数倍 CPU。
