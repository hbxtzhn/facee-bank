### 一句话总结

WebSocket 提供**原生全双工（Full-Duplex）单 TCP 管道**。在客户端建立标准协议帧通道，**下行链路**接收大模型的逐字流式 Chunk、后台异步进度推送与人机协同事件；**上行链路**可随时在流式生成中途无延迟发送中断信令（`STOP_GENERATION`）或即时追加补充要求，彻底避免 SSE 单向连接只能靠重建 HTTP 请求交互的笨拙限制。

---

### 详细回答

#### 1. 为什么全双工在复杂 AI Agent 中比 SSE 更有优势？
- **SSE 的局限**：纯单向从服务端推流到客户端；若客户端想要在模型生成途中通知“不要继续写了，改写这段”，必须另开一个 HTTP POST 请求发送中断通知，有额外的网络往返延迟；
- **WebSocket 优势**：同一个连接上双向自由交流，可以在接收 Chunk 的同时即时发送控制信号，且支持服务端主动向前端发起工具确认求助。

#### 2. 双向消息协议设计
- 客户端到服务端（Client -> Server）：
  - `{ type: 'PROMPT', payload: { text } }`；
  - `{ type: 'INTERRUPT' }`（即时终止）；
  - `{ type: 'TOOL_CONFIRM', toolId: 'pay', approved: true }`；
- 服务端到客户端（Server -> Client）：
  - `{ type: 'CHUNK', delta: '...' }`；
  - `{ type: 'AGENT_STATUS', step: 'searching_web' }`；
  - `{ type: 'DONE' }`。

---

### 核心代码片段（极简记法）

```javascript
const ws = new WebSocket('wss://api.ai.com/v1/chat');

// 1. 随时随刻发送即时中断信令
function stopGeneration() {
  ws.send(JSON.stringify({ action: 'INTERRUPT' }));
}

// 2. 统一分发各类双向事件
ws.onmessage = (event) => {
  const { type, payload } = JSON.parse(event.data);
  switch (type) {
    case 'CHUNK': renderDelta(payload.text); break;
    case 'AGENT_STATUS': updateProgressUI(payload.status); break;
    case 'DONE': finishChat(); break;
  }
};
```

---

### 面试加分项

- **心跳保活与自动重连（Heartbeat & Exponential Backoff）**：WebSocket 极易被途经的路由器或负载均衡器因空闲超时静默断开。客户端必须每 30 秒发送一次 `{ type: 'ping' }` 保活包，断线后结合带随机抖动的指数退避算法自动拉起重连。
