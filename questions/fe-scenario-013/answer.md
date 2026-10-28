### 一句话总结

统计单次 PV 内网络请求数有两种通用路径：**“底层网络原生条目扫描（`performance.getEntriesByType('resource')`）”**用于统计所有静态资源与 Ajax 请求总数；或者**“全局 Monkey Patch 拦截（统一劫持 Axios / Fetch / XMLHttpRequest）”**统计业务接口并绑定当前的全局 `pv_id`，在页面跳出或下次切换路由时汇总上报。

---

### 详细回答

#### 1. 方案一：PerformanceObserver 原生被动监听（全覆盖）
- 浏览器底层会忠实记录每一个发出的请求（HTML、CSS、JS、IMG、Fetch、XHR）；
- 通过 `performance.getEntriesByType('resource').length` 即可秒级获取全站资源总请求数。

#### 2. 方案二：全局拦截器（聚焦业务 API 统计）
- 通常产品关心的不是加载了几个图标，而是**“这次 PV 究竟调用了多少次后端接口”**；
- 在全局 Axios 拦截器或 `window.fetch` 代理中打点自增：
  - 发起请求：`reqCount++`；
  - 携带统一标记：请求头注入 `X-PV-ID: <current_pv_id>`，方便后端精准串联聚合。

#### 3. SPA 单页应用的 PV 切换边界
- 在单页应用中，路由切换（`hashchange` / `popstate` / History API）代表产生了一次新的 PV；
- 每次路由变更时：归档上一个 PV 的请求计数并上报，重置计数器并生成全新 `pv_id`。

---

### 核心代码片段（极简记法）

```javascript
let currentPvRequestCount = 0;

// 劫持原生 fetch 自动计数
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  currentPvRequestCount++;
  return originalFetch.apply(this, args);
};

// 路由离开时统计上报并重置
function onPvEnd(pvId) {
  reportPvStats({ pvId, totalApiRequests: currentPvRequestCount });
  currentPvRequestCount = 0; // 重置
}
```

---

### 面试加分项

- **请求健康度衍生指标**：除了单纯统计总数，还可以统计**请求并发峰值（Max Concurrent Requests）**与**接口报错率（Failed API Ratio）**，一旦某个 PV 内接口调用次数突增 10 倍，往往意味着代码陷入了死循环轮询 Bug。
