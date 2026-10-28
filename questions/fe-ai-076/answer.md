### 一句话总结

利用 SSE 原生支持的 **多事件类型分发（Named Events，`event: <name>`）** 特性。服务端在同一个 HTTP 连接中推送不同类型的事件帧（如 `event: progress` 推送百分比与当前步骤说明，`event: preview` 推送部分草稿 AST，`event: chunk` 推送正式文本）；前端通过 `addEventListener` 按事件类型分别更新进度条组件与预览画布，实现层次分明的多维感知。

---

### 详细回答

#### 1. 为什么不用纯 data 混合解析？
- 如果把进度、状态、文本全塞在 `data: {"type": "..."}` 里面，客户端必须每次都进行 JSON 解析，且破坏了协议分层；
- SSE 标准规范天然原生支持针对事件类型进行订阅。

#### 2. SSE 多事件流线格式规范
```http
event: progress
data: {"percent": 40, "message": "正在检索企业本地向量知识库..."}

event: chunk
data: {"delta": "根据知识库检索结果，"}

event: preview_image
data: {"lowResUrl": "data:image/webp;base64,..."}

event: done
data: {}
```

#### 3. 前端消费与多组件解耦驱动
- 进度条组件只订阅 `progress` 事件；
- 文本渲染组件只订阅 `chunk` 事件；
- 图片预览卡片只订阅 `preview_image` 事件；
- 各组件数据流清晰互不干扰。

---

### 核心代码片段（极简记法）

```javascript
// 基于 fetch ReadableStream 分发具名事件
function parseSSEEvent(eventBlock, emitter) {
  const matchEvent = eventBlock.match(/event:\s*(\w+)/);
  const matchData = eventBlock.match(/data:\s*(.+)/);

  const eventName = matchEvent ? matchEvent[1] : 'message';
  const data = matchData ? JSON.parse(matchData[1]) : {};

  emitter.emit(eventName, data); // 对应触发 progress / chunk / preview
}
```

---

### 面试加分项

- **进度条平滑动画（Spring Animation）**：服务端下发的进度数据通常是阶梯式的（如从 20% 突跳到 60%）。前端进度条应使用 CSS `transition: width 0.5s ease-out` 或弹簧插值函数，让进度条优雅匀速流动，消除视觉突兀跳跃感。
