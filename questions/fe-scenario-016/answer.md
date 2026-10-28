### 一句话总结

全站资源统计采用浏览器原生的 **`PerformanceObserver` 监听 `resource` 性能条目**。通过条目自动提取资源名称（`name`）、文件类型（`initiatorType`）、传输大小（`transferSize`）以及完整的网络瀑布流各阶段耗时（DNS、TCP、TTFB、Download）；通过按类型聚合分析，精准抓取拖慢页面的超大慢资源。

---

### 详细回答

#### 1. 核心属性与耗时计算
每个 PerformanceResourceTiming 包含微秒级高精时间戳：
- **总耗时（Duration）**：`entry.duration`；
- **DNS 查询耗时**：`entry.domainLookupEnd - entry.domainLookupStart`；
- **TCP 连接与 SSL 耗时**：`entry.connectEnd - entry.connectStart`；
- **TTFB 等待响应首字节**：`entry.responseStart - entry.requestStart`；
- **内容下载耗时**：`entry.responseEnd - entry.responseStart`。

#### 2. 识别资源是否命中缓存
- 若 `entry.transferSize === 0 && entry.decodedBodySize > 0`：代表命中本地强缓存（disk / memory cache）；
- 若体积很小且状态码为 304：代表命中协商缓存。

---

### 核心代码片段（极简记法）

```javascript
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((res) => {
    console.log(`[资源耗时] ${res.name} | 类型: ${res.initiatorType} | 耗时: ${res.duration.toFixed(1)}ms`);
    if (res.duration > 1000) {
      reportSlowResource({ url: res.name, time: res.duration }); // 上报大于1秒的慢资源
    }
  });
});

observer.observe({ type: 'resource', buffered: true });
```

---

### 面试加分项

- **Timing-Allow-Origin 跨域响应头**：必须指出，部署在独立 CDN 上的静态资源，若服务端没有在响应头添加 `Timing-Allow-Origin: *`，浏览器会隐蔽保护敏感时间线，导致重定向、DNS、TCP、TTFB 细分耗时全被清零，只能读取总 `duration`。
