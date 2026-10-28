### 一句话总结

页面关闭监听分为**“UI 交互阻拦（使用 `beforeunload`）”**与**“无感知状态上报与资源清理（优先使用 `visibilitychange` 与 `pagehide` 配合 `sendBeacon`）”**两类。现代浏览器已废弃在关闭事件中发起同步网络请求或弹窗，任何网络通信必须交由底层的 `navigator.sendBeacon` 或 `fetch keepalive` 托管。

---

### 详细回答

#### 1. 场景 A：弹出“确定要离开吗？有内容未保存”
- **唯一合法事件**：`beforeunload`；
- **标准实现**：调用 `e.preventDefault()` 并设置 `e.returnValue = ''`；
- **注意**：现代浏览器出于安全防骚扰，已彻底禁止开发者自定义弹窗中的文字内容，一律展示系统默认警告。

#### 2. 场景 B：静默发送离线埋点与保存数据
- **推荐事件**：`visibilitychange`（`document.visibilityState === 'hidden'`）或 `pagehide`；
- **为什么不用 unload？** 移动端 Safari 等环境直接划走应用时 `unload` 经常不触发；
- **网络发送方式**：必须使用 `navigator.sendBeacon(url, data)`。

---

### 核心代码片段（极简记法）

```javascript
// 1. 阻止用户误触关闭（二次确认）
window.addEventListener('beforeunload', (event) => {
  if (hasUnsavedChanges) {
    event.preventDefault();
    event.returnValue = ''; // 触发浏览器原生确认弹窗
  }
});

// 2. 可靠执行离线统计与清理
window.addEventListener('pagehide', () => {
  navigator.sendBeacon('/api/leave', JSON.stringify({ userId: 123 }));
});
```

---

### 面试加分项

- **区分“刷新”与“关闭”**：在浏览器底层两个动作触发相同事件。可通过比较 `performance.navigation.type === 1`（或全新 `performance.getEntriesByType('navigation')[0].type === 'reload'`）在页面加载时精准识别上一次是刷新还是初次进入。
