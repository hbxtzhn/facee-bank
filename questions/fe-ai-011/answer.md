### 一句话总结

AI 场景下的 SSE 本质是**带状态的流式断点续传**。由于原生 `EventSource` 只支持 GET 且无法自定义请求头，生产中必须使用 `fetch` + `ReadableStream`。通过**服务端返回递增序列号（`id`）**实现断点续推与本地滑动窗口去重，配合**带 Jitter 的指数退避**防雪崩，并利用 `TextDecoder` 的 `stream: true` 解决弱网下的中文截断乱码。

---

### 详细回答

#### 1. 为什么不用原生 EventSource？
- **只支持 GET 请求**：AI 对话需要传递多轮上下文（几千字 Prompt），极易超出 URL 长度限制（414 URI Too Long）。
- **无法自定义 Header**：无法携带 `Authorization: Bearer <token>` 等鉴权头。
- **推荐方案**：采用 `fetch` + `ReadableStream`，配合 `AbortController` 实现自主可控的流式监听与中断。

#### 2. 断点续接与消息去重
- **递增 Sequence ID**：服务端推流的每个 chunk 带递增 `id`（如 `id: 42`），前端维护 `lastEventId`。
- **断线续推**：重连时通过请求头或 Payload 带上 `last_event_id: 42`，服务端直接从 43 接着推，避免大模型重新推理浪费 Token。
- **滑动窗口去重**：前端用定长 `Set` 记录最近接收的 ID，若因网络重传收到重复包直接静默丢弃。

#### 3. 指数退避重连（防雪崩）
- **重试间隔退避**：重试时间按 $1s 	o 2s 	o 4s 	o 8s$ 递增，并附加随机扰动（Jitter），防止成千上万个客户端同时重试冲垮后端。
- **错误类型熔断**：遇到 `401`、`400` 等不可恢复的客户端错误立即终止重试；仅对网络掉线或 `502/503/504` 等网关错误发起重试。

#### 4. 弱网长文本抖动优化
- **中文截断乱码**：UTF-8 汉字占 3 字节，TCP 分包可能将字符切在两半。**必须开启 `{ stream: true }`**，让解码器自动缓冲未完成的字节：
  ```javascript
  const decoder = new TextDecoder('utf-8');
  const text = decoder.decode(chunk, { stream: true });
  ```
- **打字机平滑队列（Jitter Buffer）**：把收到的字符放入 FIFO 队列，由 `requestAnimationFrame` 匀速吐出，抹平视觉颠簸。

---

### 核心代码片段（极简记法）

```javascript
// 核心：fetch 接收 ReadableStream + 断点续接
const res = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt, lastEventId })
});

const reader = res.body.getReader();
const decoder = new TextDecoder('utf-8');

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  const chunkText = decoder.decode(value, { stream: true }); // stream: true 必填防乱码
  processSSE(chunkText);
}
```

---

### 面试加分项

- **服务端协同认知**：断点重连不是前端单方面的事，必须服务端配合在 Redis 缓存生成中的流式队列；若服务端不支持，重连只能重新生成。
- **主动取消（Abort）**：用户离开或点击停止时，必须用 `AbortController.abort()` 掐断连接，并通知后端停止模型推理，避免持续计费。
