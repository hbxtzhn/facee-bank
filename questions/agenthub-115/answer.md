### 一句话总结

流式协议需要独立终态与取消传播，关闭连接不自动说明模型和工具已停止。

### 回答要点

1. 客户端区分文本增量、状态和终态，只有明确完成才展示为完整答案；缓冲、代理与网络断开可能导致部分可见。

2. 服务端把断开或停止映射到受控取消，阻止新工具与发送，保留必要终态。已生效的外部动作仍需不确定性记录。

3. 原生 EventSource 与基于 fetch 的流式方案能力不同，需按请求方法、认证和主动取消需求选型，不能一概说 SSE 只能某一种客户端实现。

### 常见误区与边界

不要把流连接关闭当作成功完成信号。

### 资料核对

[MDN：Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)。官方资料用于核对通用 API 语义，不证明任何项目已启用相应能力。

### 关联复习

[同专题关联题](../agenthub-116/question.md)
