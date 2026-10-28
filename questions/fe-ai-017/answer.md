### 一句话总结

将多路流式 fetch 网络请求与 Markdown/JSON 解析全部**剥离到 Web Worker 独立线程**中执行；主线程仅接收解析好的结构化 UI 数据，通过 **`Transferable Objects`（零拷贝转移）或结构化克隆 + `MessageChannel`** 降低线程通信开销，彻底释放主线程保障 60fps 动画流畅度。

---

### 详细回答

#### 1. 为什么要把流式处理移入 Worker？
- 多路流式并发时（如边生成正文、边生成思维导图、边提取摘要），多个流的数据解码、正则匹配、AST 构建在单主线程会导致严重的丢帧和输入卡顿；
- Web Worker 拥有独立的事件循环和后台线程，计算再繁重也绝不卡死主界面。

#### 2. 通信架构设计
- **请求派发**：主线程发送 `{ type: 'START_STREAM', streamId: 'summary', url, prompt }` 到 Worker；
- **Worker 内部**：Worker 独立调用 `fetch(..., { signal })` 并读取流；
- **流式同步（批量节流 PostMessage）**：Worker 内部按 50ms 节流将解析好的文本差量批量发送给主线程，避免通信通道过度饱和。

---

### 核心代码片段（极简记法）

```javascript
// worker.js (子线程独立拉取流)
self.onmessage = async (e) => {
  const { url, payload } = e.data;
  const res = await fetch(url, { method: 'POST', body: JSON.stringify(payload) });
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    // 解析并回传给主线程
    self.postMessage({ type: 'CHUNK', text: decoder.decode(value, { stream: true }) });
  }
  self.postMessage({ type: 'DONE' });
};
```

---

### 面试加分项

- **SharedArrayBuffer 共享内存（极端高性能）**：对于需要双向高频交互的场景，可通过 `SharedArrayBuffer` 建立环形缓冲区，配合 `Atomics` 原语实现零通信延迟的状态同步。
