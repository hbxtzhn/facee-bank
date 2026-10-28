### 一句话总结

插件化框架采用**“微内核 + 扩展槽点（Extension Points） + 插件生命周期容器”**架构（类似 VS Code 插件机制）。核心框架仅提供宿主运行时与插件注册上下文（Plugin Context）；插件声明其贡献点（`contributes`：模型 Provider、自定义 Markdown 卡片、客户端执行 Tool），通过统一的沙箱机制与生命周期钩子接入宿主。

---

### 详细回答

#### 1. 核心设计：扩展槽点声明
- **模型接入槽（Model Provider Slot）**：注册新的 AI 厂商 API 适配器（如 Ollama 本地模型接入）；
- **自定义渲染槽（UI Component Slot）**：注册专属语法块的渲染卡片（如思维导图插件渲染 ````mindmap` 代码块）；
- **客户端工具槽（Client Tool Slot）**：注册可在前端执行的 Agent 工具（如浏览器截图、网页抓取、调用本地摄像头）。

#### 2. 插件生命周期与沙箱隔离
- 插件暴露 `activate(context)` 与 `deactivate()` 方法；
- 宿主提供受限的 `PluginContext` API（如 `context.models.register()`、`context.ui.registerBlockRenderer()`）；
- 第三方不信任插件可使用 Web Worker 或 QuickJS (WASM) 运行，防止恶意插件窃取主应用的登录凭据。

---

### 核心代码片段（极简记法）

```javascript
// 插件规范示例
export const MyChartPlugin = {
  id: 'custom-chart-plugin',
  activate(context) {
    // 1. 注册 Markdown 语法扩展渲染器
    context.ui.registerMarkdownRenderer('pie-chart', (code) => <MyPieChart data={code} />);

    // 2. 注册可供大模型调用的工具
    context.tools.register({
      name: 'get_geo_location',
      description: '获取用户当前经纬度',
      handler: async () => navigator.geolocation.getCurrentPosition(...)
    });
  }
};
```

---

### 面试加分项

- **权限清单机制（Manifest Permissions）**：插件必须在 `manifest.json` 中声明权限（如 `"permissions": ["geolocation", "network:api.foo.com"]`），用户安装时弹出授权确认弹窗，实现生产级安全管控。
