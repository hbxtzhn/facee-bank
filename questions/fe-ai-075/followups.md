## 追问 1：既然 WebSocket 功能这么全面，为什么绝大多数 AI 聊天（如 ChatGPT 官网）首选还是 SSE？

**回答要点**：
1. **运维与架构成本**：SSE 基于标准 HTTP，天然兼容现有的 CDN 缓存、代理鉴权、负载均衡与 HTTP/2 多路复用，对服务器状态无强长连接绑定；
2. **断网重连优势**：SSE 协议原生支持 `Last-Event-ID` 自动重连；
3. 对于普通“一问一答”场景，SSE 的架构复杂度远低于 WebSocket。

---

## 追问 2：浏览器关闭页面时，WebSocket 能确保把最后一条断开信令发出去吗？

**回答要点**：
不一定可靠。
在 `beforeunload` 时调用 `ws.send()`，由于浏览器进程即将被强制杀死，TCP 缓冲区可能未来得及刷新。高可靠场景需配合在 `pagehide` 中调用 `navigator.sendBeacon()` 作为保底上报。
