### 一句话总结

日志系统采用**“客户端环形内存缓冲区（Ring Buffer） + 结构化日志 Schema + 分级批量刷盘”**架构。定义包含全局 `traceId`、时间戳、日志级别与分类的标准化 JSON 格式；日常将 `DEBUG`、`INFO` 存入内存队列（仅保留最近 200 条）；一旦触发 `ERROR` 异常，一次性将内存中的前序操作回溯日志打包连带上传，兼顾极低网络开销与事故现场完美复原。

---

### 详细回答

#### 1. 为什么不能每打印一行 `console.log` 就发一次请求？
- 流式生成高频调用，频繁网络上报会严重挤占带宽；
- 绝大多数正常日志无需长期上报沉淀，只有报错前后的“案发现场日志”才具有高价值。

#### 2. 结构化日志标准 Schema
```typescript
interface LogItem {
  traceId: string;       // 贯穿前端与后端的链路 ID
  sessionId: string;     // 会话 ID
  timestamp: number;     // 毫秒时间戳
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
  category: 'USER_ACTION' | 'NETWORK' | 'STREAM' | 'RENDER';
  message: string;
  metadata?: Record<string, unknown>;
}
```

#### 3. 环形回溯缓冲区（Ring Buffer）
- 内存中维护固定容量数组（如 100 条）；
- 当写满时新日志覆盖最旧的日志；
- 当捕获到未处理的 Promise 拒绝或代码崩溃时，立即将这 100 条“历史轨迹”全部转存上报。

---

### 核心代码片段（极简记法）

```javascript
class RingLogBuffer {
  constructor(limit = 100) {
    this.limit = limit;
    this.buffer = [];
  }

  log(level, category, message, metadata = {}) {
    const entry = { time: Date.now(), level, category, message, metadata };
    if (this.buffer.length >= this.limit) this.buffer.shift();
    this.buffer.push(entry);

    if (level === 'ERROR') this.flush(); // 报错时立即全量刷盘上报！
  }

  flush() {
    const logs = [...this.buffer];
    navigator.sendBeacon('/api/logs/batch', JSON.stringify(logs));
  }
}
```

---

### 面试加分项

- **全链路 TraceId 贯通（Trace Context）**：在前端发起 Fetch 请求时，请求头注入 `x-trace-id: <uuid>`；后端微服务与模型推理网关在全链路日志中打印该 ID，排查疑难客诉时只需搜一个 ID 即可串联起从浏览器点击、Nginx、业务网关到 GPU 推理的完整链路。
