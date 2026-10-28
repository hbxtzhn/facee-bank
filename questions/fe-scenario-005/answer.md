### 一句话总结

核心采用**“`visibilitychange` 事件监听 + `navigator.sendBeacon`（或 `fetch keepalive`）后备通道 + 本地 IndexedDB 离线暂存”**。在页面切换为不可见（`hidden`）瞬间，将内存中积压的埋点队列批量通过 `sendBeacon` 脱机投递；若因断网发送失败，落盘存入 IndexedDB，待用户下次冷启动应用时自动读取补报。

---

### 详细回答

#### 1. 为什么不能等到 unload 阶段？
- 移动端划掉 App、按 Home 键切后台或锁屏时，**`unload` 和 `beforeunload` 不保证触发**；
- W3C 标准与各大浏览器推荐将 **`visibilitychange`（`document.visibilityState === 'hidden'`）** 作为保存状态与发送统计的黄金切入点。

#### 2. 可靠发送通道选型阶梯
- **首选**：`navigator.sendBeacon(url, data)`，请求由浏览器底层网络线程托管，不阻塞页面销毁；
- **备选**：`fetch(url, { method: 'POST', body: data, keepalive: true })`，功能更全面；
- **极端兜底（本地持久化）**：若离线断网，将积压数组序列化存入 `localStorage` 或 IndexedDB。

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden' && eventQueue.length > 0) {
    const payload = JSON.stringify(eventQueue);
    const success = navigator.sendBeacon('/api/track', payload);
    if (success) {
      eventQueue.length = 0; // 清空积压队列
    } else {
      localStorage.setItem('OFFLINE_TRACK_LOGS', payload); // 失败落盘
    }
  }
});
```

---

### 面试加分项

- **冷启动回放机制**：应用入口初始化时，检查 `localStorage` 中是否存在上一次未发送成功的离线埋点数据。若有，补发请求并上报附带标记 `is_retroactive: true`，确保数据完整性达到 99.9% 以上。
