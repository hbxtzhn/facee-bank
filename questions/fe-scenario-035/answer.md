### 一句话总结

Axios **完全支持取消请求**。现代 Axios（v0.22.0+）全面拥抱浏览器原生标准的 **`AbortController` 与 `AbortSignal`**（已废弃旧版自研的 `CancelToken`）；底层通过将信号源传递给底层的 XMLHttpRequest 的 `xhr.abort()` 或 Fetch API，瞬间从浏览器网络层强行切断 TCP 数据流传输，并使对应的 Promise 进入 reject 异常分支。

---

### 详细回答

#### 1. 现代标准方案：AbortController
- 创建控制器：`const controller = new AbortController();`；
- 发起请求时透传信号：`axios.get('/api/search', { signal: controller.signal })`；
- 随时随刻取消：`controller.abort()`；
- 捕获异常：通过 `axios.isCancel(err)` 或 `err.name === 'CanceledError'` 判定该错误由主动取消引起，无需向用户弹出报错。

#### 2. 常见核心业务场景
- **Tab 标签快速切换（防竞态条件）**：用户从 Tab A 点击切换到 Tab B，必须立即取消 Tab A 尚未返回的网络请求，防止 Tab A 的慢数据晚于 Tab B 返回而篡改界面；
- **搜索输入联想框（弃旧迎新）**；
- **页面组件卸载（Unmount）**：在 React `useEffect` 清理函数中取消请求，防止组件销毁后仍在内存中触发 `setState` 内存泄漏警告。

---

### 核心代码片段（极简记法）

```javascript
const controller = new AbortController();

axios.get('/api/large-data', { signal: controller.signal })
  .catch(err => {
    if (axios.isCancel(err)) {
      console.log('请求被成功主动取消:', err.message);
    }
  });

// 用户点击取消按钮或离开页面
controller.abort();
```

---

### 面试加分项

- **服务端是否感知取消？** 必须指出：前端调用 `abort()` 仅代表**“客户端切断了 TCP 连接并不再接收后续 Response”**。如果请求已经到达服务端并开始执行繁重的数据库写事务，服务端若未配置断开监听，依然会默默把操作执行完毕。取消前端请求不能百分百阻止服务端已触发的逻辑。
