## 追问 1：Webview 嵌入式场景下，页面重新加载时宿主通信容易断开丢失，SDK 怎么做重连保活？

**回答要点**：
SDK 内置握手心跳机制（Handshake Protocol）：在初始化时向宿主轮询发送 `ping`，收到宿主回复的 `pong` 后才将 SDK 状态标记为 `ready` 并放行请求，未就绪前的调用暂存在内存缓冲区。

---

## 追问 2：嵌入到别人网页的 SDK 如何彻底防止 CSS 样式冲突？

**回答要点**：
采用 **Web Components 的 Shadow DOM（Open 模式）** 挂载 UI 容器。Shadow DOM 能构建天然的样式隔离屏障，外部宿主网页的任何 CSS 规则均无法渗透影响 SDK 内部组件。
