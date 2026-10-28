### 一句话总结

该架构采用**“基座宿主应用（Host） + 动态模块联邦（Module Federation）远程子应用”**。基座应用负责全局统一的鉴权、网络 SSE 通道、全局状态总线与模型接入配置；聊天卡片、流程图编排器、多模态画布作为独立仓储开发与构建发布为 Remote 模块，基座通过动态加载远程 `remoteEntry.js` 按需挂载子应用，实现团队自治与零停机发版。

---

### 详细回答

#### 1. 为什么 AI 复杂产品适合模块联邦？
- 现代 AI 应用功能庞杂（如 ChatGPT 同时集成智能体 Store、Canvas 协同编辑、代码解释器、DALL-E 画板）；
- 模块联邦允许多个子团队独立开发、独立部署，在运行时直接共享全局 React 运行时与公共组件库，打包体积大幅缩减。

#### 2. 核心架构三层划分
- **宿主层（Host）**：路由中枢、单点登录、模型网关客户端、全局状态通道；
- **共享依赖（Shared Dependencies）**：配置 `singleton: true` 共享 `react`, `react-dom`, `zustand`, `lucide-react`，消除子应用重复加载；
- **业务远程应用（Remotes）**：
  - `ai-chat`：多轮对话、流式 Markdown 渲染；
  - `ai-workflow`：低代码 DAG 节点拖拽连线编排；
  - `ai-canvas`：画布白板与图形图表渲染。

---

### 核心代码片段（极简记法）

```javascript
// host 的 vite.config.js (利用 @originjs/vite-plugin-federation)
federation({
  name: 'ai-host',
  remotes: {
    chatApp: 'http://cdn.ai.com/chat/assets/remoteEntry.js',
    workflowApp: 'http://cdn.ai.com/workflow/assets/remoteEntry.js'
  },
  shared: ['react', 'react-dom', 'zustand']
});

// 动态按需挂载
const RemoteChat = React.lazy(() => import('chatApp/ChatWidget'));
```

---

### 面试加分项

- **子应用降级容错（Circuit Breaker）**：为远程模块加载包裹 `ErrorBoundary`。当某个子应用静态资源 CDN 故障或 404 时，基座捕获错误并展示优雅降级占位卡片，绝不连带崩溃整站。
