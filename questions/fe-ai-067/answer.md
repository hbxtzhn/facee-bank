### 一句话总结

采用 **Sentry 前端 SDK 结合 Scope 上下文注入与 Breadcrumbs（面包屑）自动录制**。在全局配置中通过 `Sentry.setContext()` 绑定当前激活的模型名称、网络协议（SSE/WS）与 Prompt 参数；利用自定义前置过滤器（`beforeSend`）在错误上报时对敏感个人隐私进行星号脱敏，配合 React ErrorBoundary 实现异常瞬时捕获与精准现场还原。

---

### 详细回答

#### 1. 为什么传统控制台错误在 AI 场景下极难排查？
- AI 错误通常依赖特定上下文（如：某个特定长度的中文 Prompt 在 Markdown 转义反引号时触发了正则死循环崩溃）；
- 传统 Sentry 只抓取调用栈，无法得知崩溃前用户输入了什么、当前使用的是哪个模型。

#### 2. Sentry Scope 维度上下文设计
- **`setTag('model_id', 'gpt-4o')`**：打上索引标签，在 Sentry 面板中一键筛选“所有特定模型的错误”；
- **`setContext('ai_request', { promptLength, temperature, streamActive: true })`**：记录结构化参数树；
- **Breadcrumbs 面包屑追踪**：记录最近 10 次的用户操作（如：点击选择文件 -> 输入 Prompt -> 收到首个 Chunk -> 发生解析异常）。

---

### 核心代码片段（极简记法）

```javascript
import * as Sentry from '@sentry/react';

// 发起 AI 请求前绑定上下文
Sentry.configureScope((scope) => {
  scope.setTag('ai_provider', 'openai');
  scope.setContext('generation_params', {
    model: 'gpt-4o',
    temperature: 0.7,
    promptLength: prompt.length
  });
  scope.addBreadcrumb({ category: 'ai.stream', message: 'SSE Connection opened' });
});

// 捕获异常
try {
  parseMarkdownChunk(badChunk);
} catch (err) {
  Sentry.captureException(err);
}
```

---

### 面试加分项

- **严苛的 PII 隐私合规拦截（beforeSend）**：绝不可将用户的完整身份证号、银行卡号或涉密商机 Prompt 明文发送到第三方 Sentry 平台。在 `beforeSend(event)` 钩子中编写正则表达式，将敏感内容替换为 `[REDACTED]` 后再外发，确保符合 GDPR / 网络安全合规。
