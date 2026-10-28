### 一句话总结

监控方案采用**“Web-Vitals 浏览器性能基线 + AI 专属业务指标探测器（TTFT、Token/s、打断率） + sendBeacon 批量异步聚合上报”**。结合 `PerformanceObserver` 采集首屏加载与布局抖动；重点度量 AI 对话独有的**首字时间（TTFT）与端到端推流速率**，将技术指标与用户提问 Token 规模多维交叉关联，建立可视化全链路监控大盘。

---

### 详细回答

#### 1. 传统前端指标 vs AI 专属性能指标
- **传统 Web Vitals**：
  - **FCP / LCP**：首屏最大内容绘制；
  - **CLS（Cumulative Layout Shift）**：由于流式文本不断撑开高度，AI 界面极易发生严重的 CLS 布局抖动，是重点监控对象；
- **AI 独有核心指标（必须度量）**：
  - **TTFT（Time To First Token）**：用户点击发送到首个汉字渲染出来的延迟（衡量模型思考与网关冷启动性能）；
  - **TPS（Tokens Per Second）**：流式推流速率；
  - **User Abort Rate（打断率）**：用户提前点击“停止”的比例（打断率高说明生成质量差或速度慢）。

#### 2. 上报架构设计
- 使用 Google 官方 `web-vitals` 库监听；
- 采集完成后，使用 `navigator.sendBeacon('/api/metrics', blob)` 异步非阻塞上报，不与主业务请求抢占带宽。

---

### 核心代码片段（极简记法）

```javascript
import { onLCP, onCLS } from 'web-vitals';

// 1. 监听基础指标
onLCP(metric => reportMetric('LCP', metric.value));
onCLS(metric => reportMetric('CLS', metric.value));

// 2. 测量 AI 首字延迟与生成速率
function trackAIPerformance(sessionId) {
  const t0 = performance.now();
  let firstTokenTime = null;
  let tokenCount = 0;

  return {
    onFirstToken: () => {
      firstTokenTime = performance.now() - t0;
      reportMetric('AI_TTFT', firstTokenTime, { sessionId }); // 毫秒
    },
    onToken: () => tokenCount++,
    onDone: () => {
      const totalTime = (performance.now() - t0) / 1000;
      const tps = tokenCount / totalTime;
      reportMetric('AI_TPS', tps, { sessionId, totalTokens: tokenCount });
    }
  };
}
```

---

### 面试加分项

- **动态采样率控制（Sampling Rate）**：大流量平台全量上报会冲垮监控后端。对成功会话按 5% 比例动态采样上报，对报错会话（Error / 500 / 429）执行 100% 强制全量上报，平衡监控覆盖度与服务器开销。
