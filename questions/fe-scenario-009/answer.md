### 一句话总结

最标准可靠的原生 API 是 **Page Visibility API（监听 `visibilitychange` 事件结合 `document.visibilityState`）**。当值等于 `'visible'` 时代表页签处于激活可见状态，`'hidden'` 代表页签被切到后台、最小化或被遮挡；亦可辅助结合 `window.onfocus` 与 `window.onblur` 判断焦点切换。

---

### 详细回答

#### 1. Page Visibility API（标准方案）
- **`document.hidden`**：只读布尔值；
- **`document.visibilityState`**：
  - `'visible'`：页面在当前屏幕上至少部分可见；
  - `'hidden'`：页面完全不可见（用户切换了 Tab、浏览器最小化或电脑锁屏）；
- **事件监听**：`document.addEventListener('visibilitychange', () => { ... })`。

#### 2. focus / blur 与 visibilitychange 的关键差异
- 用户在双显示器环境下，在主屏幕看网页，鼠标点击了副屏幕的聊天工具；
- 此时网页触发了 `blur`（失去焦点），但页面仍然在屏幕上是**完全可见的**！
- 若用 `blur` 暂停视频播放会导致极差体验，因此**度量页面是否被看始终以 `visibilitychange` 为准**。

#### 3. 常见实战应用场景
- **暂停耗电任务**：页面切后台时立即暂停 Canvas 复杂动画、停止视频播放、调低 WebSocket 心跳频率；
- **唤醒即时轮询**：用户切回页面瞬间，立即向服务器发起一次增量拉取，秒级同步最新未读红点。

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    resumeAnimation(); // 切回前台：恢复动画/拉取最新数据
    startHeartbeat();
  } else {
    pauseAnimation();  // 切到后台：暂停定时器以节省 CPU
    stopHeartbeat();
  }
});
```

---

### 面试加分项

- **浏览器切后台定时器降频（Timer Throttling）**：指出浏览器出于省电考虑，会对处于 `hidden` 状态的页签中的 `setInterval` 强制施加最低 1000ms（甚至更长）的休眠惩罚。重要定时器切后台时必须有心理准备，不可依赖其精准计时。
