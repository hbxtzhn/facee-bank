### 一句话总结

流式进度预测采用**“滑动窗口计算实时速率（Tokens/s） + 任务总预期长度预测 + 阻尼平滑算法”**。根据前序接收的 Token 计算瞬时生成速度，结合用户 Prompt 意图对总 Token 数进行经验预估，并通过平滑移动平均（EMA）消除时间预测突变跳动，给用户稳定的心理预期。

---

### 详细回答

#### 1. 为什么不能用固定倒计时？
- AI 推理受服务器负载、网络抖动、模型思考（CoT）等因素影响，速度是波动的；
- 必须基于真实网络采样的动态速度进行推算。

#### 2. 三步计算模型
1. **采样窗口与瞬时速率**：
   记录最近 $N$ 秒内接收的 Token 数量差：
   $	ext{Speed} = rac{\Delta 	ext{Tokens}}{\Delta 	ext{Time}}$
2. **总 Token 预估（经验模型）**：
   根据任务类型预估基准总长度（例如“生成代码”默认 800 Token，“摘要”默认 200 Token）；
3. **剩余时间与阻尼平滑**：
   $	ext{RemainingTime} = rac{	ext{EstimatedTotal} - 	ext{CurrentTokens}}{	ext{Speed}}$
   利用指数移动平均（EMA）过滤速度颠簸，避免倒计时从 5 秒跳到 20 秒又跳回 3 秒。

---

### 核心代码片段（极简记法）

```javascript
class TokenSpeedEstimator {
  constructor() {
    this.history = []; // [{ time, count }]
  }

  record(tokenCount) {
    const now = performance.now();
    this.history.push({ time: now, count: tokenCount });
    // 仅保留最近 3 秒的采样点
    this.history = this.history.filter(item => now - item.time <= 3000);
  }

  getSpeed() { // 计算 token / 秒
    if (this.history.length < 2) return 20; // 默认初始速率
    const first = this.history[0];
    const last = this.history[this.history.length - 1];
    const duration = (last.time - first.time) / 1000;
    return duration > 0 ? (last.count - first.count) / duration : 20;
  }
}
```

---

### 面试加分项

- **终点停滞体验优化（Zeno's Paradox 防御）**：若真实生成长度超过了预估总长度，进度条不能超过 100% 也不能卡死。应采用类似浏览器加载条的对数减速效果（逐渐逼近 99% 但永不走满），直到收到 `[DONE]` 瞬间拉满完成。
