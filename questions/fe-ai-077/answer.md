### 一句话总结

该架构采用**“主线程调度中枢 + 多 Web Worker 独立沙箱推理 + 多数表决/评审融合仲裁机（Consensus Arbiter）”**。将请求同时派发给三个运行不同轻量模型或调用不同 API 的 Worker 并发生成；在主线程采用**文本相似度投票（Majority Voting）**或将各家结果合成提示词由第四个评判模型做最终裁决，极大压低单模型的幻觉率并产出最优答案。

---

### 详细回答

#### 1. 为什么需要“模型投票（Model Ensemble）”？
- 单个 AI 模型无论多强大，都存在固有的盲区与事实幻觉；
- 在高可靠性要求场景（如法律条款校验、复杂数学计算、医疗常识初筛），让多个模型独立作答并交叉比对，能显著提高输出的正确率。

#### 2. Worker 并发与主线程架构
- **Worker 池划分**：
  - `Worker 1`：运行轻量本地 Qwen 模型；
  - `Worker 2`：请求 DeepSeek 接口；
  - `Worker 3`：请求 Claude 接口；
- **并发触发**：`Promise.allSettled([w1.run(), w2.run(), w3.run()])`；
- **仲裁策略（Arbitration）**：
  - 若为分类/单选题：直接统计众数（Mode）；
  - 若为长文本开放题：使用 LCS（最长公共子序列）提取各模型的一致性事实，剔除孤立差异点。

---

### 核心代码片段（极简记法）

```javascript
async function ensembleQuery(prompt) {
  // 1. 并行派发给三个独立模型 Worker
  const results = await Promise.all([
    callModelWorker('model-a.js', prompt),
    callModelWorker('model-b.js', prompt),
    callModelWorker('model-c.js', prompt)
  ]);

  // 2. 仲裁融合（以文本相似度多数票决为例）
  const finalAnswer = arbitrateBestAnswer(results);
  return finalAnswer;
}
```

---

### 面试加分项

- **超时淘汰机制（Straggler Mitigation）**：多个模型并发时，必然有一个响应最慢（木桶效应）。配置动态阈值：只要前两个模型已返回且耗时已达设定上限，立即忽略最慢的长尾模型，直接基于前两个结果进行融合，防止整体延迟被个别慢模型拖死。
