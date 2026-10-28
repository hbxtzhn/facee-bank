## 追问 1：模块联邦中，如果宿主与子应用的 React 版本出现微小偏差（如 18.2 vs 18.3），怎么处理？

**回答要点**：
在联邦配置中指定 `requiredVersion: '^18.0.0'` 并声明 `strictVersion: false`；模块联邦运行时会自动协商匹配满足 semver 的最高语义化版本，确保内存中始终仅初始化一个 React 单例实例。

---

## 追问 2：子应用之间的样式冲突怎么隔离？

**回答要点**：
推荐采用 **Tailwind CSS 搭配特定前缀（`prefix: 'chat-'`）** 或 **CSS Modules / Scoped CSS**；若需要强隔离，可将子应用包裹在 Web Components 的 Shadow DOM 内。
