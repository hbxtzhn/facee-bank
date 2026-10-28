## 追问 1：监听 sendBeacon 时，为什么推荐使用 visibilitychange 而不是 unload / beforeunload？

**回答要点**：
在移动端浏览器（尤其是 iOS Safari）中，当用户切换应用或划掉后台时，`unload` 和 `beforeunload` **根本不会触发**；W3C 官方明确建议将 `visibilitychange`（结合 `document.visibilityState === 'hidden'`）作为页面生命周期结束的最可靠唯一点。

---

## 追问 2：如果服务端接口只支持 application/json，sendBeacon 默认是 text/plain 怎么办？

**回答要点**：
将数据包装为指定 MIME 类型的 `Blob` 对象：
`const blob = new Blob([jsonString], { type: 'application/json' });`
再传入 `navigator.sendBeacon(url, blob)`，浏览器请求头会自动带上 `Content-Type: application/json`。
