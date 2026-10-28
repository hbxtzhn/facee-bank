### 一句话总结

上下文管理策略采用**“层级金字塔模型（Hierarchical Pyramid）”**。在首部固化不可撼动的 **System Prompt（设定与约束）**；尾部保留最新 $N$ 轮的 **精确滑动窗口（Raw Turns）**；中部被淘汰的超长早期历史则在后台**异步浓缩为自动摘要（Rolling Summary）与关键记忆事实表（Key Facts）**，实现无限轮次对话而 Token 恒定在安全水位。

---

### 详细回答

#### 1. 传统无脑携带全量历史的危害
- 触发大模型上下文截断上限报错（Context Window Exceeded）；
- Token 费用以指数级递增；
- 发生“中间遗忘（Lost in the Middle）”，历史消息过长反而导致模型找不到关键指令。

#### 2. 三级上下文编排设计
1. **Layer 1：持久系统人格（Pinned System Context）**：包含核心业务指令和用户全局 Profile；
2. **Layer 2：动态压缩记忆（Dynamic Memory Summary）**：
   - 当总 Token 接近阈值（如预警线的 70%）时；
   - 触发后台静默调用一次小模型：“总结以下第 1~20 轮对话的要点与已达成结论”；
   - 将原 20 轮消息替换为一条系统级 Summary 消息；
3. **Layer 3：最新上下文视口（Recent Sliding Window）**：保持原汁原味的最近 3~5 轮对话，确保指代词（如“它”、“刚才那个”）理解准确。

---

### 核心代码片段（极简记法）

```javascript
function assembleContext(systemPrompt, summaryText, recentMessages) {
  const context = [{ role: 'system', content: systemPrompt }];

  if (summaryText) {
    context.push({ role: 'system', content: `【前序背景总结】: ${summaryText}` });
  }

  // 拼接最近活跃窗口
  return context.concat(recentMessages);
}
```

---

### 面试加分项

- **前端透明感知**：在界面消息流中，被折叠压缩的历史上方展示一条优雅的分界提示线：“以上历史已被自动浓缩为记忆点（点击可展开完整回顾）”，既保障 Token 优化，又赋予用户完全的知情权。
