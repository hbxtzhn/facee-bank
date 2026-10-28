## 追问 1：全局状态库（如 Zustand store）应该放在 src/stores 还是按 feature 存放？

**回答要点**：
特性专属的状态（如当前会话的流式中间 Buffer、单条消息展开折叠态）严格放在该 `features/chat/stores` 内部；仅有跨整个系统共享的全局状态（如当前登录用户 Profile、全局租户主题）才提取到 `src/stores`。

---

## 追问 2：目录结构如何适配微前端或者后续拆分为 Monorepo？

**回答要点**：
按 Feature-based 划分的代码天然具备**向独立子包抽离的独立性**。后续若要升级为 Monorepo，只需将 `features/agent-workflow` 目录直接物理剪切到 `packages/agent-workflow`，并在其内部添加 `package.json` 即可瞬间无缝拆分。
