### 一句话总结

该面板采用**“指标采集探针（Metrics Probe） + 时间序列聚合 + ECharts / Tremor 可视化仪表盘”**。采集各模型的 TTFT 首字延迟、P95/P99 响应耗时、429/500 错误率以及 Prompt/Completion 实际消耗的 Token 数量；前端根据不同模型官方单价矩阵实时折算为美元/人民币成本，辅助工程团队对模型进行性价比选型与限流治理。

---

### 详细回答

#### 1. 核心四大维度的度量指标
- **吞吐与延迟**：
  - 首字延迟（TTFT，Time To First Token）；
  - 全文生成总耗时；
  - P95 / P99 极端长尾延迟分布；
- **稳定性**：
  - 接口成功率（`200 OK` 比例）；
  - 429 限流频率、504 网关超时频率；
- **资源与成本**：
  - 输入/输出 Token 累计用量；
  - 动态计费计算器：$	ext{Cost} = 	ext{Tokens}_{	ext{in}} 	imes P_{	ext{in}} + 	ext{Tokens}_{	ext{out}} 	imes P_{	ext{out}}$。

#### 2. 前端面板交互与呈现
- **折线图（Time Series）**：实时展示过去 1 小时各模型的延迟波动曲线；
- **饼图/环形图**：展示团队各业务线对不同模型（Claude 3.5 vs GPT-4o vs DeepSeek）的调用量占比；
- **异常警报高亮**：若某模型近 5 分钟错误率超过 5%，面板卡片亮起红色呼吸告警，并展示“建议一键熔断切换为备选模型”操作开关。

---

### 核心代码片段（极简记法）

```javascript
// 计算各模型实时折算费用
const PRICE_PER_1K = {
  'gpt-4o': { prompt: 0.005, completion: 0.015 },
  'deepseek-chat': { prompt: 0.0001, completion: 0.0002 }
};

function calculateCost(model, promptTokens, completionTokens) {
  const p = PRICE_PER_1K[model];
  if (!p) return 0;
  return (promptTokens / 1000) * p.prompt + (completionTokens / 1000) * p.completion;
}
```

---

### 面试加分项

- **异常告警通知联动（Webhook）**：面板不仅能看，还能设置阈值规则（如 P99 超过 15 秒）。一旦触发，由前端通过飞书/钉钉 Webhook 自动发送群告警，实现工程监控闭环。
