### 一句话总结

基于 **SSE 行协议状态机**解析格式块。标准 SSE 协议中通过 `event: <name>` 或在 `data:` 内容中携带自定义标记（如 `[DONE]`）；解析器按 `\n\n` 切分块后提取事件名和有效载荷，利用 **发布订阅模式（EventBus）或策略映射表（Strategy Map）** 精确分发到对应事件回调。

---

### 详细回答

#### 1. 常见服务端推流格式规范
- **协议级事件（Event-Type 形式）**：
  ```http
  event: error
  data: {"code": "RATE_LIMIT", "message": "请求过于频繁"}
  ```
- **内容级控制符（OpenAI 规范形式）**：
  ```http
  data: [DONE]
  ```

#### 2. 状态机分词解析
- 每个 SSE Block 以双换行 `\n\n` 分隔；
- 逐行扫描：
  - 若以 `event:` 开头，记录事件名 `eventName`；
  - 若以 `data:` 开头，提取内容主体；
  - 遇到 `[DONE]` 触发 `onComplete()` 回调并主动中断流读取；
  - 解析到 `error` 立即触发 `onError(parsedData)`。

---

### 核心代码片段（极简记法）

```javascript
function handleSSELine(line, emitter) {
  if (line.startsWith('data:')) {
    const data = line.slice(5).trim();
    if (data === '[DONE]') {
      emitter.emit('complete');
      return;
    }
    try {
      const json = JSON.parse(data);
      if (json.error) emitter.emit('error', json.error);
      else emitter.emit('message', json.delta);
    } catch {
      emitter.emit('message', data);
    }
  }
}
```

---

### 面试加分项

- **处理心跳注释行（Ping / Keep-alive）**：很多网关每 15 秒推一条 `: ping` 注释防止连接断开。解析器必须能识别并静默忽略以冒号 `:` 开头的 SSE 注释行，防止将其误当成非法数据报错。
