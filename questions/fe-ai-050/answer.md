### 一句话总结

嵌入式 SDK 采用**“无外部重依赖（Zero Dependency） + JSON-RPC / IPC 跨进程通信适配层 + 统一门面（Facade Pattern）”**设计。以不到 50KB 的纯原生 JS 打包；通过适配器屏蔽 VS Code Webview、Electron、浏览器 Iframe 的通信差异，对外暴露纯声明式的 `client.generateStream()` API 与基于 Promise / AsyncIterable 的标准生命周期接口。

---

### 详细回答

#### 1. 嵌入式宿主环境的异构性
- 同一个 AI 辅助核心可能需要嵌入到 VS Code 侧边栏（`acquireVsCodeApi()` 通信）、Chrome 浏览器扩展（`chrome.runtime.sendMessage`）、桌面 Electron（Node IPC）；
- SDK 必须提供通信适配器（Transport Adapter）抽象。

#### 2. 接口设计原则
- **极简初始化**：`const ai = new AISDK({ transport: new VSCodeTransport() })`；
- **强类型契约**：提供完整的 TypeScript 类型声明 `.d.ts`；
- **防污染**：严禁在 SDK 内部污染全局 `window` 或注入全局 CSS，所有样式和逻辑完全内聚或以纯数据返回。

---

### 核心代码片段（极简记法）

```javascript
class AISDK {
  constructor(transport) {
    this.transport = transport; // 注入不同的 IPC 驱动
  }

  // 统一异步迭代器门面
  async *chat(prompt) {
    const streamId = Math.random().toString();
    this.transport.send({ type: 'START', streamId, prompt });

    while (true) {
      const msg = await this.transport.receiveNext(streamId);
      if (msg.done) break;
      yield msg.chunk;
    }
  }
}
```

---

### 面试加分项

- **双向方法调用（JSON-RPC 2.0）**：不仅宿主调用 SDK，模型还可以通过 SDK 反向请求宿主执行操作（如“获取当前激活代码文件的内容”、“在第 20 行插入代码”），通过 JSON-RPC 规范管理请求 ID 与响应回调对应。
