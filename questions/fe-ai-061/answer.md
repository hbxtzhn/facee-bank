### 一句话总结

推荐采用**“功能特性切片（Feature-based Architecture）结合领域驱动分层”**。将代码组织从按技术类型（如把所有 components 堆在一起）升级为**按 AI 业务特性（`chat/`, `agent/`, `prompt-studio/`）自包含组织**；核心层抽象出独立的 `models/`（模型配置与 Provider 适配）、`tools/`（客户端执行工具集）与 `shared/`（纯 UI 与通用工具），保持高内聚低耦合。

---

### 详细回答

#### 1. 传统按技术类型组织的痛点
- 所有的 hooks、components、api 散落在全局目录中；
- 当 AI 功能包含独立的流式解析器、Markdown 特殊渲染卡片、状态机时，开发者需要在 10 个跨度极大的目录之间反复横跳，改一个 Agent 功能牵扯全仓。

#### 2. 标准生产级目录树规范
```text
src/
├── features/               # 业务特性切片（按业务域划分）
│   ├── chat/              # 聊天特性（包含该特性专属的 components/hooks/stores）
│   ├── agent-workflow/    # 智能体编排工作流
│   └── prompt-lab/        # Prompt 调试实验室
├── core/                   # AI 核心能力下沉层
│   ├── models/            # 厂商适配器（OpenAI, Anthropic, Ollama）
│   ├── tools/             # 客户端 Tool 注册表（计算器、地理位置、截图）
│   └── stream/            # SSE / WebSocket 传输层与流式解析器
├── components/ui/          # 通用设计系统（原子级按钮、弹窗、输入框）
├── types/                 # 跨模块共享 TS 类型与 Zod Schema
└── lib/                   # 纯工具函数（时间格式化、缓存助手）
```

---

### 核心代码片段（极简记法）

```text
// features/chat 内部实现完全自闭环：
features/chat/
├── components/MessageList.tsx
├── hooks/useStreamChat.ts
├── stores/chatStore.ts
└── index.ts               # 对外仅导出公共 API（Facade）
```

---

### 面试加分项

- **路径别名（Path Alias）与严格跨模块依赖规则**：在 `tsconfig.json` 中配置 `@/features/*`，并配合 ESLint 强行禁止 `features/chat` 内部代码直接深层引用 `features/prompt-lab` 的私有文件，跨模块必须走对方的 `index.ts` 导出，杜绝模块网状循环依赖。
