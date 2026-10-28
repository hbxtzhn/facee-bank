### 一句话总结

`navigator.sendBeacon` 是浏览器专门为**“页面卸载/跳出时异步可靠上报数据（如埋点、停留时长、报错日志）”**设计的原生 API。它以 **POST** 方式异步排队发送请求，**完全脱离当前页面的生命周期限制**，即使页面被瞬间关闭，浏览器后台也会保证数据包可靠送达服务器，且绝不阻塞页面卸载与新页面导航。

---

### 详细回答

#### 1. 传统页面离开上报方式的致命缺陷
- **同步 XHR（`xhr.open(..., false)`）**：会严重卡死浏览器主线程，用户感知到明显的关闭卡顿，现代浏览器已在 unload 事件中将其全面废弃；
- **普通异步 fetch / 异步 XHR**：页面销毁时，浏览器为释放资源会**直接强制掐断未决的网络连接**，导致高达 30%~50% 的离开埋点丢失；
- **同步构造空图片（`new Image().src = ...`）**：在旧版浏览器中能短暂卡住页面，但在新版 Chrome 中同样会被强制取消。

#### 2. sendBeacon 的核心优势
- **后台脱钩排队**：请求交由浏览器底层进程托管，页面无论多快关闭都不影响请求发送；
- **非阻塞性能**：完全异步执行，对用户感知零卡顿，不影响跳出跳转流畅度；
- **API 极简**：返回布尔值 `true` / `false` 表示浏览器是否成功将任务塞入发送队列。

#### 3. 局限性与避坑点
- **只能发 POST 请求**；
- **无法读取响应结果**：无法获取服务器返回的 Response 数据（纯单向投递）；
- **Payload 体积受限**：浏览器对排队中的 beacon 数据施加了 64KB 的配额上限，超出直接返回 `false` 拒绝排队。

---

### 核心代码片段（极简记法）

```javascript
// 在 visibilitychange 或 pagehide 事件中可靠上报
window.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    const data = JSON.stringify({ event: 'page_exit', duration: 42 });
    const blob = new Blob([data], { type: 'application/json' });
    navigator.sendBeacon('/api/analytics', blob);
  }
});
```

---

### 面试加分项

- **fetch keepalive 替代方案**：现代 Fetch API 提供了 `{ keepalive: true }` 配置（如 `fetch('/api', { method: 'POST', body, keepalive: true })`），其行为与 sendBeacon 完全一致，但支持自定义复杂的请求头并能发送更多 HTTP Method，是目前最新的标准实践。
