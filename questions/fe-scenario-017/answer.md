### 一句话总结

防止重复请求必须构建**“UI 交互禁用 + 请求层唯一 Key 拦截（AbortController 取消或锁定时序） + 服务端幂等 Token 兜底”**三层防御。对于提交类操作在点击瞬间通过状态变量禁用按钮；在 Axios / Fetch 拦截器中根据“请求方法+URL+参数”生成唯一 Hash 键，若前序相同请求未完成直接中止后发请求或自动取消旧请求。

---

### 详细回答

#### 1. 视图层（UI 禁用 / Loading 锁）
- 点击提交按钮后，按钮立即设为 `disabled` 并展示旋转 Spinner；
- 必须放在 `finally` 中解锁，确保无论成功或报错都能恢复可点击状态。

#### 2. 请求拦截层（Axios CancelToken / AbortController 拦截器）
- **策略 A（保旧废新，适合表单提交）**：前序请求正在进行中，新的相同请求直接被拦截抛弃；
- **策略 B（弃旧迎新，适合搜索框输入防抖查询）**：前序请求还没返回，用户输入了新关键字，使用 `AbortController.abort()` 掐断上一个请求，只保留最新请求。

#### 3. 生产级唯一请求 Hash 判定
- 生成规则：`key = [method, url, JSON.stringify(params), JSON.stringify(data)].join('&')`；
- 维护内存 `pendingRequests = new Map()`；发起前 `has(key)` 判定拦截，响应后 `delete(key)`。

---

### 核心代码片段（极简记法）

```javascript
const pendingMap = new Map();

function generateReqKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.data)}`;
}

// Axios 请求拦截器防重
axios.interceptors.request.use((config) => {
  const reqKey = generateReqKey(config);
  if (pendingMap.has(reqKey)) {
    // 拦截重复请求
    return Promise.reject(new Error('请勿频繁重复提交！'));
  }
  pendingMap.set(reqKey, true);
  return config;
});

// 响应拦截器清理释放
axios.interceptors.response.use(
  (res) => { pendingMap.delete(generateReqKey(res.config)); return res; },
  (err) => { pendingMap.delete(generateReqKey(err.config)); return Promise.reject(err); }
);
```

---

### 面试加分项

- **服务端分布式幂等 Token（Idempotency Key）**：指出黑客可以直接跨过前端界面调用接口。对于金融支付和创建订单，进入表单页面时先向后端申请一个唯一的 `idempotent_token`，提交时携带，后端通过 Redis 分布式锁拦截重复 Token，实现 100% 幂等。
