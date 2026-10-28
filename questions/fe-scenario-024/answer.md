### 一句话总结

核心采用**“微任务/时间窗口批处理防抖（Debounce Window）”**或**“单例活跃锁（Active Toast Mutex）”**。在全局 Axios 响应拦截器中拦截报错时，不直接调用 `toast.error()`，而是将错误投递到带有 50~100ms 延迟的时间窗口中去重合并；或者维护全局布尔标志位，只要当前屏幕上已有错误弹窗处于展示状态，后续同类错误全部静默吞吐。

---

### 详细回答

#### 1. 为什么不用简单的 Lodash debounce？
- 单纯的防抖函数会延迟执行最后一次，并且若报错信息各不相同（如接口 A 报 401，接口 B 报 500），简单防抖可能会把关键的 401 给吞掉。

#### 2. 最优解：消息队列批处理与归并（Message Batching）
- 当第一个错误到达时，开启一个短暂的时间切片（如 50ms）；
- 期间到达的所有报错全部压入当前批次数组；
- 时间窗口结束时统一决断：
  - 若包含登录失效 401，只弹一个“登录已过期，请重新登录”；
  - 若全是普通网络异常，弹出一个统合提示“网络异常，部分数据加载失败”；
  - 彻底杜绝 5 个黑色弹窗像扑克牌一样层叠刷屏。

---

### 核心代码片段（极简记法）

```javascript
let toastTimer = null;
const errorPool = new Set();

function showSafeToast(errMsg) {
  errorPool.add(errMsg);

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    const combinedMessage = Array.from(errorPool).join('；') || '请求失败，请稍后重试';
    Toast.error(combinedMessage);
    errorPool.clear(); // 清空错误池
  }, 100); // 100ms 窗口内的错误全部聚合合并
}
```

---

### 面试加分项

- **组件库原生单例模式（destroyOnClose）**：像 Ant Design 等优秀的组件库本身支持全局单例覆盖：`message.error({ content: '...', key: 'global_error_toast' })`。只需声明固定的 `key`，连续调用 5 次也只会更新同一个 DOM 节点的文本，从组件库底层天然杜绝多重弹窗。
