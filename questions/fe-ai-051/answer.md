### 一句话总结

Agent 循环采用**“ReAct（Reason + Act）有限状态自旋驱动”**。大模型输出 `tool_calls` 后，前端通过**动态工具分发中心（Tool Dispatcher）结合 `Promise.allSettled` 并发调度**；每个工具调用独立挂载带超时的 `AbortSignal.timeout()`；若工具抛错，将格式化后的错误信息伪装为正常 observation 反馈给大模型，驱动模型自主反思纠错，避免单点异常崩溃整体循环。

---

### 详细回答

#### 1. 为什么工具执行错误不能直接抛出异常中断？
- 工具执行失败（如网络超时、参数错误）在 Agent 中是常态；
- 若前端直接 `throw Error`，整个 Agent 任务直接死亡；
- **正确做法**：将错误转化为 observation：`{ error: "404 Not Found" }` 回传给大模型，让模型自发调整参数重试或切换备选工具。

#### 2. 工具调用的异步控制三防线
1. **超时熔断**：每个客户端工具绑定硬超时（如 5 秒），避免用户等死；
2. **并发安全控制**：支持声明工具的互斥性（如纯查询可并发 `allSettled`，写入工具必须串行队列执行）；
3. **最大步数限制（Max Iterations）**：强约束最多循环 10 次，防止模型陷入自我对话的无底洞死循环。

---

### 核心代码片段（极简记法）

```javascript
async function executeToolWithTimeout(toolFn, args, timeoutMs = 5000) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const result = await Promise.race([
      toolFn(args, controller.signal),
      new Promise((_, reject) => controller.signal.addEventListener('abort', () => reject(new Error('工具执行超时'))))
    ]);
    clearTimeout(timer);
    return { success: true, data: result };
  } catch (err) {
    return { success: false, error: err.message }; // 错误转反馈文本
  }
}
```

---

### 面试加分项

- **人机交互确认插槽（Human-in-the-Loop）**：如果工具标记为 `riskLevel: 'high'`（如支付、发送邮件），拦截执行挂起，向前端 UI 触发一个 Modal 弹窗等待用户点击“批准”或“拒绝”，实现安全可控执行。
