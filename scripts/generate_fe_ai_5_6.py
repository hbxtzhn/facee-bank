import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-ai-041",
        "title": "请设计一个微前端+模块联邦的AI应用架构",
        "difficulty": "hard",
        "question": "请设计一个“微前端+模块联邦”的AI应用架构，支持独立部署聊天、编辑、可视化等子应用。",
        "answer": """### 一句话总结

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

- **子应用降级容错（Circuit Breaker）**：为远程模块加载包裹 `ErrorBoundary`。当某个子应用静态资源 CDN 故障或 404 时，基座捕获错误并展示优雅降级占位卡片，绝不连带崩溃整站。""",
        "followups": """## 追问 1：模块联邦中，如果宿主与子应用的 React 版本出现微小偏差（如 18.2 vs 18.3），怎么处理？

**回答要点**：
在联邦配置中指定 `requiredVersion: '^18.0.0'` 并声明 `strictVersion: false`；模块联邦运行时会自动协商匹配满足 semver 的最高语义化版本，确保内存中始终仅初始化一个 React 单例实例。

---

## 追问 2：子应用之间的样式冲突怎么隔离？

**回答要点**：
推荐采用 **Tailwind CSS 搭配特定前缀（`prefix: 'chat-'`）** 或 **CSS Modules / Scoped CSS**；若需要强隔离，可将子应用包裹在 Web Components 的 Shadow DOM 内。"""
    },
    {
        "id": "fe-ai-042",
        "title": "如何用Monorepo管理AI前端、Node中间层与共享类型统一代码库？",
        "difficulty": "medium",
        "question": "如何用Monorepo管理AI前端、Node.js中间层、共享类型定义、工具脚本的统一代码库？",
        "answer": """### 一句话总结

基于 **pnpm Workspaces + Turborepo（或 Nx）** 搭建现代 Monorepo 工程。将代码拆分为 `apps/web`（前端界面）、`apps/node-gateway`（BFF 计费鉴权中间层）与 `packages/shared-types`（模型与 Prompt 共享契约）；通过 workspace 软链接实现**“类型一处改动，前后端实时联动编译提示”**，配合 Turborepo 全局缓存实现秒级极速构建。

---

### 详细回答

#### 1. 痛点：多仓分离（Multi-repo）的维护灾难
- AI 模型接口迭代极快（字段频繁新增/弃用）；
- 前端与 Node BFF 跨仓维护时，TS 接口必须双边手动复制同步，经常因拼写漏更导致生产环境运行时报错。

#### 2. Monorepo 目录规划标准
```text
my-ai-project/
├── apps/
│   ├── web/               # Next.js / React 前端
│   └── gateway/           # NestJS / Fastify 模型中间层 (BFF)
├── packages/
│   ├── api-client/        # 前端调用 BFF 的 SDK
│   ├── shared-types/      # 核心领域实体、Zod Schema 与 TS 类型
│   └── ui/                # 共享 Design System 组件库
└── pnpm-workspace.yaml
```

#### 3. Turborepo 任务流拓扑编排
- 在根目录 `turbo.json` 中配置 pipeline：
  `"build": { "dependsOn": ["^build"], "outputs": [".next/**", "dist/**"] }`
- 当构建 `web` 时，Turborepo 会自动先编译依赖的 `shared-types`，并智能跳过未改动包的构建（Remote Caching）。

---

### 核心代码片段（极简记法）

```json
// pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```json
// apps/web/package.json 引入内部公共类型包
"dependencies": {
  "@org/shared-types": "workspace:*"
}
```

---

### 面试加分项

- **Changesets 自动化版本与发版**：在 Monorepo 中配合 `@changesets/cli`，针对每个 Pull Request 自动生成改动日志，合并后自动化打 tag 发布独立 npm 包。""",
        "followups": """## 追问 1：前端代码如果误引入了 Node.js 中间层的后端私密依赖（如包含数据库密码的模块），如何检测？

**回答要点**：
通过 ESLint 配置规则（如 `import/no-restricted-paths`）或 TS Project References 进行依赖层级隔离，严禁 `apps/web` 跨目录导入任何属于 `apps/gateway` 内部的源码。

---

## 追问 2：团队规模变大后，Monorepo 安装依赖或 CI 速度变慢怎么优化？

**回答要点**：
1. 开启 **Turborepo 远程缓存（Remote Cache）**；
2. 开启 pnpm 的 content-addressable store 硬链接机制；
3. CI 中配置针对受影响文件（`turbo run test --filter=...[origin/main]`）的增量测试与构建。"""
    },
    {
        "id": "fe-ai-043",
        "title": "设计一个插件化AI前端框架，允许第三方扩展模型、UI与工具调用",
        "difficulty": "hard",
        "question": "设计一个“插件化”AI前端框架，允许第三方开发者通过插件扩展模型接入、UI组件、工具调用。",
        "answer": """### 一句话总结

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

- **权限清单机制（Manifest Permissions）**：插件必须在 `manifest.json` 中声明权限（如 `"permissions": ["geolocation", "network:api.foo.com"]`），用户安装时弹出授权确认弹窗，实现生产级安全管控。""",
        "followups": """## 追问 1：第三方 UI 插件如果抛出 React 运行时报错，会不会把主聊天窗口搞白屏？

**回答要点**：
宿主在渲染所有动态插件提供的组件外层强制包裹独立 `ErrorBoundary`。插件组件一旦崩溃，就地展示“插件渲染异常”提示与刷新按钮，绝不影响主界面对话流程。

---

## 追问 2：插件的动态加载机制是怎么实现的？

**回答要点**：
基于原生 ES Modules 动态导入：`const plugin = await import(/* @vite-ignore */ pluginCdnUrl);`。宿主拉取 JS 脚本后实例化并调用其 `activate()` 钩子注册到内存槽点表中。"""
    },
    {
        "id": "fe-ai-044",
        "title": "在AI多租户SaaS平台中，如何设计前端支持动态主题、独立域名与开关？",
        "difficulty": "medium",
        "question": "在AI多租户SaaS平台中，如何设计前端架构以支持动态主题、自定义域名、独立功能开关？",
        "answer": """### 一句话总结

多租户前端架构采用**“域名解析租户标识（Tenant Resolver） + CSS 变量运行时主题换肤 + 特征开关（Feature Flags）动态能力树”**。首屏通过二级域名或 CNAME 识别当前租户并预先获取租户配置；将主题颜色下发注入 `:root` CSS 变量；界面菜单与模型列表根据租户购买套餐的功能开关（Feature Flag）动态裁减，实现千企千面的白牌（White-label）定制。

---

### 详细回答

#### 1. 自定义域名与租户识别
- **域名解析流程**：
  - 访问 `tenantA.ai.com` 或 CNAME `ai.companyB.com`；
  - 前端路由拦截或 Next.js Edge Middleware 提取 `host` 请求头；
  - 携带域名向配置网关请求该租户元数据（Logo、品牌名称、色系、已购模型列表）。

#### 2. CSS 变量动态一键换肤
- 杜绝针对每个租户单独打包一套 CSS；
- 全局使用 CSS 自定义属性（CSS Variables）：
  ```css
  :root {
    --primary-color: #1677ff;
    --chat-bubble-radius: 8px;
  }
  ```
- 接口返回配置后，一行 JS 动态注入：
  `document.documentElement.style.setProperty('--primary-color', tenant.themeColor);`

#### 3. 特征开关（Feature Flags）与模型权限控制
- 租户配置返回模块权限树：`{ enableCodeInterpreter: false, allowedModels: ['gpt-4o-mini'] }`；
- 前端通过 `<FeatureGate flag="enableCodeInterpreter">` 条件包裹，未购买高级特性的租户直接隐藏该入口。

---

### 核心代码片段（极简记法）

```javascript
// 1. 动态挂载租户品牌主题
function applyTenantTheme(theme) {
  const root = document.documentElement;
  root.style.setProperty('--primary-color', theme.brandColor);
  root.style.setProperty('--navbar-bg', theme.navBackground);
  document.title = theme.brandTitle;
}

// 2. 特征开关组件保护高阶功能
function FeatureGate({ flag, children }) {
  const tenantFlags = useTenantStore(s => s.features);
  return tenantFlags[flag] ? children : null;
}
```

---

### 面试加分项

- **防白屏防闪烁（FOUC 优化）**：租户配置拉取完成前界面容易闪烁。在 HTML `<head>` 中嵌入一小段内联 JS，在页面 DOM 解析前即刻根据本地缓存的租户主题设好 CSS 变量，消除色彩突变。""",
        "followups": """## 追问 1：不同租户要求在系统内上传不同的 Favicon 网站图标，前端怎么动态修改？

**回答要点**：
获取页面中 `<link rel="icon">` 元素指针，直接修改其 `href` 为接口返回的租户图标 URL：
`document.querySelector("link[rel*='icon']").href = tenant.faviconUrl;`

---

## 追问 2：如果租户配置了极其恶心的文字/背景对比度（如黄底白字），怎么保证可读性？

**回答要点**：
前端实现亮度计算算法：根据十六进制颜色值计算其相对亮度（Luminance）。若计算出品牌色偏亮，文字自动切换为深灰色；若品牌色偏深，文字自动切换为纯白，确保符合 WCAG 无障碍对比度标准。"""
    },
    {
        "id": "fe-ai-045",
        "title": "如何用DDD（领域驱动设计）划分AI前端核心领域与界限上下文？",
        "difficulty": "hard",
        "question": "如何用DDD（领域驱动设计）划分AI前端的核心领域（对话、模型、工具、知识库）与界限上下文？",
        "answer": """### 一句话总结

DDD 在前端的应用核心是**“消除以页面或纯视图为中心的组件面条代码”**。将应用切分为 **ChatContext（对话会话领域）、ModelRegistryContext（模型配置领域）、ToolEngineContext（工具执行领域）与 KnowledgeContext（知识库与检索领域）** 四个界限上下文；各上下文内部包含独立的**实体（Entities）、值对象（Value Objects）与聚合根（Aggregates）**，通过领域事件解耦交互。

---

### 详细回答

#### 1. 为什么前端极度需要 DDD？
- 传统前端往往将请求、数据拼接、UI 渲染写在同一个几十个 hooks 的庞大组件中；
- 当 AI 业务叠加多模态、工具调用、多 Agent 协作时，代码迅速退化为不可维护的灾难。

#### 2. 核心界限上下文划分
- **会话聚合（Chat Aggregate）**：
  - 聚合根：`Conversation`；
  - 实体：`Message`；
  - 值对象：`TokenUsage`、`MessageId`（不可变）；
- **工具调用领域（Tool Domain）**：
  - 职责：管理客户端 Tool 的参数 Schema 校验、权限拦截、执行与超时恢复；
- **防腐层（Anticorruption Layer, ACL）**：
  - 处于外部 AI 服务商（OpenAI, Anthropic）与核心领域之间，将异构的原始 API 转换为整洁的内部领域模型。

---

### 核心代码片段（极简记法）

```typescript
// 领域实体与业务行为充血模型
export class Conversation {
  private messages: Message[] = [];

  constructor(public readonly id: string) {}

  // 领域内聚方法，杜绝外部随便 push
  public appendStreamDelta(messageId: string, delta: string) {
    const msg = this.messages.find(m => m.id === messageId);
    if (!msg) throw new Error('Message not found');
    msg.appendContent(delta);
  }

  public get totalTokens(): number {
    return this.messages.reduce((sum, m) => sum + m.tokenUsage.count, 0);
  }
}
```

---

### 面试加分项

- **充血模型（Rich Domain Model） vs 贫血模型**：指出在前端传统 Redux 中数据只是一堆纯对象（贫血），业务逻辑散落在各组件；DDD 推荐将逻辑封装在实体方法内，使核心业务与具体渲染框架（React/Vue）彻底脱钩，单测覆盖率可达 100%。""",
        "followups": """## 追问 1：前端使用面向对象的 DDD 领域类，会不会与 React 推荐的不可变数据流冲突？

**回答要点**：
不冲突。
领域模型专注处理纯粹的核心业务逻辑；当需要将状态提交给 React UI 渲染时，在 Repository 或 Store 层通过 `.toSnapshot()` 方法导出一份结构共享的浅拷贝纯数据给 React 即可。

---

## 追问 2：防腐层（ACL）在前端具体是怎么落地的？

**回答要点**：
通常是一组纯函数适配器。当接收到不同厂商（如 DeepSeek、OpenAI）的原始 JSON 响应时，先经过 ACL 适配器转换映射，对外永远输出统一的内部 `DomainMessage` 对象。"""
    },
    {
        "id": "fe-ai-046",
        "title": "设计事件驱动架构，用EventEmitter解耦AI输入、处理与输出模块",
        "difficulty": "medium",
        "question": "设计一个“事件驱动”架构，用EventEmitter或MessageChannel解耦AI各个模块（输入、处理、输出）。",
        "answer": """### 一句话总结

事件驱动架构采用**“发布-订阅（Pub/Sub）事件总线”**切断输入框、网络请求引擎、Markdown 渲染器、TTS 语音播报模块之间的直接硬编码耦合。各模块仅对总线广播领域事件（如 `PROMPT_SUBMITTED`、`STREAM_CHUNK`、`GENERATION_FINISHED`）并监听自己关心的事件，实现模块间**高内聚、零依赖、自由拔插**。

---

### 详细回答

#### 1. 传统紧耦合调用的痛点
- 输入框组件在点击提交时，直接调用请求函数、直接更新消息 Store、直接触发滚动条滚动、直接启动 TTS 播放；
- 输入框组件代码迅速膨胀至上千行，牵一发而动全身。

#### 2. 事件总线解耦方案
- **模块 A（输入框）**：只做一件事——捕获用户敲击回车，广播 `bus.emit('ai:submit', { prompt })`；
- **模块 B（流式网络层）**：监听到 `ai:submit`，拉起 Fetch 流，不断向总线广播 `ai:chunk`；
- **模块 C（TTS 语音模块）**：独立监听到 `ai:chunk`，在后台静默做断句合成语音，完全不需要输入框知晓其存在。

---

### 核心代码片段（极简记法）

```javascript
import mitt from 'mitt';

// 1. 全局领域事件总线（利用 mitt 极致轻量）
export const aiBus = mitt();

// 2. 网络层：监听提交，广播流式数据
aiBus.on('ai:submit', async ({ prompt }) => {
  const stream = await fetchStream(prompt);
  for await (const chunk of stream) {
    aiBus.emit('ai:chunk', { delta: chunk });
  }
  aiBus.emit('ai:done');
});

// 3. 消费端（如语音合成）：按需订阅，彻底解耦
aiBus.on('ai:chunk', ({ delta }) => audioSpeaker.feed(delta));
```

---

### 面试加分项

- **TypeScript 类型强约束事件名与参数**：利用泛型类型 `mitt<EventsMap>`，防止事件名手误敲错或载荷数据类型不匹配，兼顾解耦与静态安全。""",
        "followups": """## 追问 1：在 React 组件中使用事件总线，最容易发生的内存泄漏是什么？怎么避免？

**回答要点**：
最常见 Bug 是在 `useEffect` 中注册了 `bus.on(event, handler)`，但在组件销毁清理函数中**忘记调用 `bus.off(event, handler)`**，导致闭包常驻内存且组件反复挂载时监听器成倍重复执行。

---

## 追问 2：如果同一事件的多个监听器之间有执行先后依赖（比如 A 必须先处理完 B 才能执行），怎么解？

**回答要点**：
事件总线设计初衷是无序解耦的。若存在强先后序依赖，说明应该升级为**流水线管道（Pipeline / Middleware 链条模式）**或状态图，而非扁平事件总线。"""
    },
    {
        "id": "fe-ai-047",
        "title": "在AI实时协作场景中，如何用OT或CRDT实现多用户并发编辑冲突解决？",
        "difficulty": "hard",
        "question": "在AI实时协作场景中，如何用OT（操作转换）或CRDT实现多用户并发编辑的冲突解决？",
        "answer": """### 一句话总结

多用户并发协同（如 AI 正在流式续写的同时，用户也在手动修改文本）推荐采用 **CRDT（无冲突复制数据类型，如 Yjs）**。OT 依赖中心化服务器严格定序与复杂的矩阵转换算法；而 CRDT 为每个字符分配全局唯一且单调递增的逻辑时间戳 ID，通过**偏序规则（Partial Order）在数学上保证最终一致性（Eventual Consistency）**，天然契合高频流式与离线无网络合并。

---

### 详细回答

#### 1. 痛点：AI 流式与人脑并发修改文本
- AI 正在第 10 行追加文字，用户同时在第 2 行删除了一个段落；
- 若只同步纯字符串，光标错位、文字覆盖截断不可避免。

#### 2. OT vs CRDT 核心选型
- **OT（操作转换，Google Docs 采用）**：
  - 发送的是操作意图（如 `insert(pos, char)`）；
  - 强依赖中心服务端进行操作转换（Transform）；服务端复杂度极高；
- **CRDT（以 Yjs 为代表，现代推荐）**：
  - 数据结构本身内嵌协作语义；
  - 每个字符包裹唯一标识（Client ID + Clock）；
  - **无需中心服务端参与**，任意两端收到 Patch 后直接执行合并算法，数学上证明最终结果必然绝对相同。

---

### 核心代码片段（极简记法）

```javascript
import * as Y from 'yjs';

const doc = new Y.Doc();
const yText = doc.getText('ai-document');

// 1. AI 流式追加（模拟输入）
function onAiStreamChunk(delta) {
  doc.transact(() => {
    yText.insert(yText.length, delta); // 以 CRDT 事务插入
  });
}

// 2. 绑定编辑器（如 Monaco / CodeMirror）实现自动协作同步
const binding = new MonacoBinding(yText, editor.getModel(), new Set([editor]), provider.awareness);
```

---

### 面试加分项

- **感知系统（Awareness System）**：Yjs 不仅同步文档，还内置 Awareness 协议。可以同步展示正在协同的其他用户的光标位置、头像名称，以及 AI 正在生成中的虚拟高亮光标。""",
        "followups": """## 追问 1：CRDT 记录了每一个字符的历史 ID，会不会导致内存随着文档变大而严重膨胀？

**回答要点**：
Yjs 采用了独特的 **Struct Store（连续块压缩）** 技术：对连续键入的字符自动合并为单个链表节点，将内存开销压缩到接近原生纯文本的水平，几十万字长文也能保持极快性能。

---

## 追问 2：网络断网数小时后重新连上，CRDT 是如何处理期间海量堆积的历史版本的？

**回答要点**：
Yjs 支持版本向量（State Vector）快速比对。客户端只需向远端发送一个几十字节的 State Vector，双方即可精确计算出各自缺失的增量 Update 二进制包，单次网络请求直接完成无缝合并。"""
    },
    {
        "id": "fe-ai-048",
        "title": "如何设计配置驱动的AI工作流引擎？前端通过JSON定义节点与分支",
        "difficulty": "hard",
        "question": "如何设计一个“配置驱动”的AI工作流引擎，前端通过JSON或YAML定义节点、连接线、条件分支？",
        "answer": """### 一句话总结

配置驱动工作流引擎采用**“有向无环图（DAG）JSON Schema 规范 + 节点驱动型可视化运行时（如 React Flow） + 拓扑排序执行引擎”**。前端通过 JSON 描述 `nodes`（输入、模型、分支、代码执行）与 `edges`（数据流动连线）；通过拓扑排序（Topological Sort）确定无环依赖序列，结合异步依赖注入引擎依次驱动节点求值。

---

### 详细回答

#### 1. 工作流 DAG 数据规范设计
```json
{
  "nodes": [
    { "id": "input_1", "type": "userInput" },
    { "id": "llm_1", "type": "llmNode", "config": { "model": "gpt-4o", "prompt": "{{input_1.text}}" } },
    { "id": "branch_1", "type": "conditionNode", "config": { "rules": [{ "expr": "len > 50", "target": "node_A" }] } }
  ],
  "edges": [
    { "source": "input_1", "target": "llm_1" },
    { "source": "llm_1", "target": "branch_1" }
  ]
}
```

#### 2. 前端画布可视化（React Flow）
- 将 JSON 中的 `nodes` 映射为自定义 React 组件（`LLMNodeComponent`、`CodeNodeComponent`）；
- 节点通过 Handle 锚点定义输入插槽与输出插槽；
- 画布拖拽、缩放、连线即时更新 JSON 树。

#### 3. 执行引擎：拓扑排序（Topological Sorting）与条件分支
- 检查入度为 0 的起始节点；
- 依次推进执行；遇到分支节点时，根据上一节点输出的变量值求值表达式，动态激活下游的边，未激活分支直接标记为跳过（Skipped）。

---

### 核心代码片段（极简记法）

```javascript
// 简单拓扑执行调度
async function executeDAG(nodes, edges, initialInput) {
  const context = { input: initialInput };
  // 简化的线性顺序执行（实际需根据 edge 拓扑排序）
  for (const node of nodes) {
    if (node.type === 'llm') {
      context[node.id] = await callLLM(node.config.prompt, context);
    } else if (node.type === 'condition') {
      const match = evaluateRule(node.config.rule, context);
      if (!match) break; // 中断或选择分支
    }
  }
  return context;
}
```

---

### 面试加分项

- **循环依赖环路检测（Cycle Detection）**：在用户连线建立 Edge 时，前端立即执行一次深度优先遍历（DFS）进行环路检查。若发现用户试图形成回路，禁止连接并弹出 Toast“工作流不允许形成死循环依赖”。""",
        "followups": """## 追问 1：节点执行过程中如果需要实时展示每个节点的运行中/成功/耗时状态，前端怎么驱动？

**回答要点**：
基于订阅发布总线：每个节点绑定唯一 `nodeId`。执行引擎在进入节点前广播 `{ nodeId, status: 'running' }`，执行后广播 `{ nodeId, status: 'success', duration: 120ms }`，React Flow 节点组件监听到后即时变绿或转菊花。

---

## 追问 2：如果某个节点执行失败，工作流如何支持从失败节点处继续重试（断点重跑）？

**回答要点**：
执行上下文缓存（Context Snapshot）：每个成功节点的输出持久化保存在执行记录中；重试时直接复用失败节点之前的所有前序产物，只针对失败节点及其下游发起重新求值。"""
    },
    {
        "id": "fe-ai-049",
        "title": "设计前后端分离AI应用：前端直调大模型API，后端仅做鉴权与计费代理",
        "difficulty": "medium",
        "question": "请设计一个“前后端分离”的AI应用，前端直接调用多个AI服务商API，后端仅做鉴权与计费代理。",
        "answer": """### 一句话总结

该架构采用**“短暂临时令牌（Ephemeral Ephemeral Token）机制 + 反向鉴权代理网关”**。前端绝不可明文硬编码任何大模型主 API Key；用户发起会话前先请求后端 BFF，后端核销用户套餐额度后下发**单次带签名且限制生效时间（如 5 分钟）的临时访问 Token**，前端携带该 Token 直连代理网关推流，兼具极速低延迟与绝对资金安全。

---

### 详细回答

#### 1. 为什么前端不能直接保存官方 API Key？
- 无论代码如何打包混淆，任何在前端客户端中暴露的 OpenAI / Anthropic 密钥，都会在 1 分钟内被黑客通过 Network 抓包提取，直接导致数十万元的盗刷欠费事故。

#### 2. 安全代理流转架构
1. **获取授权凭证**：前端向自身后端发送 `POST /api/auth/token`；
2. **后端鉴权与预扣费**：后端核验用户身份与余额，签发一份带有 HMAC 防伪签名的短效 JWT；
3. **直连边缘网关（Cloudflare Workers 等）**：
   - 前端直连代理 URL，在 Header 中携带短效 JWT；
   - 边缘网关验证签名并扣减使用配额后，在网关层动态注入真实的大模型 API 密钥并透明转发给大模型；
   - 模型响应通过 SSE 直连推流回前端。

---

### 核心代码片段（极简记法）

```javascript
// 1. 先向自身业务后端申请临时推流凭证
const { tempToken, gatewayUrl } = await fetch('/api/token').then(r => r.json());

// 2. 前端携带临时凭据直连网关，安全直推
const res = await fetch(gatewayUrl, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${tempToken}`, // 临时 Token，泄漏自动过期
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ prompt: '你好' })
});
```

---

### 面试加分项

- **前端客户端密钥模式（BYOK - Bring Your Own Key）**：如果是面向开发者的开源或本地工具，允许用户在设置中填入自己的 API Key。前端仅将密钥加密保存在用户的本地 LocalStorage 中，每次请求直接直连官方接口，零经过第三方服务器，打消用户隐私顾虑。""",
        "followups": """## 追问 1：前端直连大模型 API 时，如果遇到跨域（CORS）限制怎么处理？

**回答要点**：
官方大模型接口通常不允许未配置的浏览器跨域直连，或直连有安全隐患。
必须通过配置了 CORS 白名单的轻量反向代理中间层（如 Nginx、Cloudflare Workers 或 Vercel Edge）做请求中转。

---

## 追问 2：如果用户在流式生成过程中异常中断，临时 Token 的费用怎么精确结算？

**回答要点**：
代理网关在流式管道中持续统计实际输出的 Chunk 字节数或 Token 数量，当连接断开时，网关异步向结算中心上报一条实际消耗事件（Usage Event），实现多退少补的精准结算。"""
    },
    {
        "id": "fe-ai-050",
        "title": "在AI嵌入式场景（如IDE插件）中，如何设计轻量级SDK供宿主调用？",
        "difficulty": "medium",
        "question": "在AI嵌入式场景（如IDE插件）中，如何设计轻量级SDK，提供一致的API供宿主应用调用？",
        "answer": """### 一句话总结

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

- **双向方法调用（JSON-RPC 2.0）**：不仅宿主调用 SDK，模型还可以通过 SDK 反向请求宿主执行操作（如“获取当前激活代码文件的内容”、“在第 20 行插入代码”），通过 JSON-RPC 规范管理请求 ID 与响应回调对应。""",
        "followups": """## 追问 1：Webview 嵌入式场景下，页面重新加载时宿主通信容易断开丢失，SDK 怎么做重连保活？

**回答要点**：
SDK 内置握手心跳机制（Handshake Protocol）：在初始化时向宿主轮询发送 `ping`，收到宿主回复的 `pong` 后才将 SDK 状态标记为 `ready` 并放行请求，未就绪前的调用暂存在内存缓冲区。

---

## 追问 2：嵌入到别人网页的 SDK 如何彻底防止 CSS 样式冲突？

**回答要点**：
采用 **Web Components 的 Shadow DOM（Open 模式）** 挂载 UI 容器。Shadow DOM 能构建天然的样式隔离屏障，外部宿主网页的任何 CSS 规则均无法渗透影响 SDK 内部组件。"""
    },
    {
        "id": "fe-ai-051",
        "title": "在前端实现Agent循环时，如何管理工具调用的异步执行与超时？",
        "difficulty": "hard",
        "question": "在前端实现一个Agent循环时，如何管理工具调用的异步执行、超时处理与结果合并？",
        "answer": """### 一句话总结

Agent 循环采用**“ReAct（Reason + Act）有限状态自旋驱动”**。大模型输出 `tool_calls` 后，前端通过**动态工具分发中心（Tool Dispatcher）结合 `Promise.allSettled` 并发调度**；每个工具调用独立挂载带超时的 `AbortSignal.timeout()`；若工具抛错，将格式化后的错误信息伪装为正常 observation 反馈给大模型，驱动模型自主反思纠错，避免单点异常崩溃整体循环。

---

### 详细回答

#### 1. 为什么工具执行错误不能直接抛出异常中断？
- 工具执行失败（如网络超时、参数错误）在 Agent 中是常态；
- 若前端直接 `throw Error`，整个 Agent 任务直接死亡；
- **正确做法**：将错误转化为 observation：`{ error: "404 Not Found" }` 回传给大模型，让模型自发调整参数重试或切换备选工具。

#### 2. 工具调用的异步控制三防线
1. **超时熔断**：每个客户端工具绑定硬超时（如 5 秒），避免用户等死；
2. **并发安全控制**：支持声明工具的互斥性（如纯查询可并发 `allSettled`，写入工具必须串行队列执行）；
3. **最大步数限制（Max Iterations）**：强约束最多循环 10 次，防止模型陷入自我对话的无底洞死循环。

---

### 核心代码片段（极简记法）

```javascript
async function executeToolWithTimeout(toolFn, args, timeoutMs = 5000) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const result = await Promise.race([
      toolFn(args, controller.signal),
      new Promise((_, reject) => controller.signal.addEventListener('abort', () => reject(new Error('工具执行超时'))))
    ]);
    clearTimeout(timer);
    return { success: true, data: result };
  } catch (err) {
    return { success: false, error: err.message }; // 错误转反馈文本
  }
}
```

---

### 面试加分项

- **人机交互确认插槽（Human-in-the-Loop）**：如果工具标记为 `riskLevel: 'high'`（如支付、发送邮件），拦截执行挂起，向前端 UI 触发一个 Modal 弹窗等待用户点击“批准”或“拒绝”，实现安全可控执行。""",
        "followups": """## 追问 1：大模型单次返回了 5 个并行的工具调用，如何防止冲垮前端资源？

**回答要点**：
基于 `p-limit` 或自定义并发池控制最大并行度（如限制最大并发数为 3）；执行完毕后使用 `Promise.allSettled` 收集所有产物，按原始序号回填。

---

## 追问 2：如果大模型死循环重复调用同一个报错的工具怎么办？

**回答要点**：
维护一个本地的“工具调用指纹记录表（Tool Call Hash History）”。如果发现模型连续 3 次传入完全相同的参数调用同一个已报错工具，主动在 Prompt 中注入强力警告：“该工具已连续失败 3 次，禁止再次调用，请根据现有信息直接给出结论”。"""
    },
    {
        "id": "fe-ai-052",
        "title": "设计前端本地向量检索系统，用ONNX Runtime做句子嵌入与相似度匹配",
        "difficulty": "hard",
        "question": "请设计一个前端本地的向量检索系统，用TensorFlow.js或ONNX Runtime计算句子嵌入并做相似度匹配。",
        "answer": """### 一句话总结

该系统采用**“轻量量化小模型（如 all-MiniLM-L6-v2 ONNX 量化版） + ONNX Runtime Web 推理引擎 + 内存余弦相似度（Cosine Similarity）矩阵运算”**。纯前端本地执行文本分词并推理生成 384 维向量；与 IndexedDB 预存的文档向量集进行点积比对，实现**零服务器依赖、零成本、毫秒级且百分之百保护隐私**的本地知识库检索（Client-side RAG）。

---

### 详细回答

#### 1. 为什么要在前端做本地向量化？
- **隐私保护**：用户本地敏感笔记、密码文本完全不出浏览器；
- **零服务端成本**：分担大模型向量化 API 的调用费用；
- **离线可用**：在无网络环境下依然支持本地智能语义搜索。

#### 2. 三步实现流水线
1. **模型加载与缓存**：
   下载量化为 8 位的轻量模型（体积约 20MB），由浏览器 CacheStorage 或 IndexedDB 永久缓存；
2. **文本转向量（Inference）**：
   使用 `@xenova/transformers`（封装了 ONNX Runtime Web）：
   ```javascript
   const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
   const output = await extractor('如何做性能优化', { pooling: 'mean', normalize: true });
   const queryVector = output.data; // Float32Array
   ```
3. **向量检索（余弦相似度）**：
   遍历本地知识库向量，计算向量点积：$\cos(\theta) = \sum A_i B_i$，降序返回 Top K 相关片段。

---

### 核心代码片段（极简记法）

```javascript
// 向量归一化后的点积即为余弦相似度
function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
  }
  return dotProduct;
}

// 快速匹配本地文档 Top K
function searchTopK(queryVec, docVectors, k = 3) {
  return docVectors
    .map(doc => ({ ...doc, score: cosineSimilarity(queryVec, doc.vector) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}
```

---

### 面试加分项

- **WebGPU 加速**：ONNX Runtime Web 支持指定执行提供者为 WebGPU（`executionProviders: ['webgpu']`），在支持的浏览器上向量推理耗时可从 WASM 的 100ms 骤降至 10ms 以内。""",
        "followups": """## 追问 1：如果本地有数万条文本向量，逐一循环计算余弦相似度会掉帧卡死，怎么优化？

**回答要点**：
1. **移入 Web Worker 并发计算**；
2. **利用近似最近邻算法（HNSW / Hierarchical Navigable Small World）**，避免全量暴力扫描，通过图索引实现对数时间复杂度检索。

---

## 追问 2：浏览器关闭重新打开后，预加载的模型还要重新下载吗？

**回答要点**：
不需要！
`@xenova/transformers` 底层默认利用浏览器的 `caches` API（CacheStorage）对 ONNX 模型权重二进制文件进行持久化缓存，再次打开零网络流量秒级载入。"""
    },
    {
        "id": "fe-ai-053",
        "title": "在AI产品中，前端可以通过哪些技术手段帮助降低Token成本？",
        "difficulty": "medium",
        "question": "在AI产品中，前端可以通过哪些技术手段（如缓存、压缩、懒加载）帮助降低Token成本？",
        "answer": """### 一句话总结

前端降低 Token 成本的核心是**“把关输入入口 + 会话上下文智能裁剪 + 本地结果去重缓存”**。通过 **Prompt 客户端去空格精简**、**滑动窗口截断历史轮次**、**向量相似度命中直接走前端本地缓存**，以及**防抖避免无效提问**，在网络请求发出前拦下 30%~50% 的不必要 Token 消耗。

---

### 详细回答

#### 1. 会话上下文滑动窗口（Sliding Window）
- 多轮对话如果将 50 轮历史无脑发给后端，Token 呈二次方级爆炸；
- 前端维护滑动窗口：只携带**系统 Prompt（System Role） + 最近 4~6 轮对话**；超出的历史消息自动在前端折叠，或前端调用本地小模型做轻量摘要后发送。

#### 2. 本地相似度缓存（Semantic Cache）
- 对用户提问在本地计算 Hash 或向量检索；
- 若用户问了与 5 分钟前完全相同或语义相似度 > 0.98 的问题，直接调取 IndexedDB 缓存的旧回答，提示“已从本地缓存秒级命中”，完全不发接口。

#### 3. 客户端 Prompt 清洗与压缩
- 过滤无效换行、冗余连续空格、剔除长文本中无关的 HTML/Markdown 样式标签；
- 上传代码文件时，前端预先剔除注释行和无意义的空格缩进后再喂给模型。

---

### 核心代码片段（极简记法）

```javascript
// 会话上下文滑动窗口控制
function prepareContextMessages(allMessages, maxRounds = 4) {
  const systemMsg = allMessages.find(m => m.role === 'system');
  const recentDialogs = allMessages.filter(m => m.role !== 'system').slice(-maxRounds * 2);

  // 始终保留 System Prompt，中间历史裁剪，只带最新多轮
  return systemMsg ? [systemMsg, ...recentDialogs] : recentDialogs;
}
```

---

### 面试加分项

- **预知 Token 计数提醒（Token Pre-flight Estimator）**：在用户输入框右下角利用轻量分词器动态展示“当前提问约消耗 120 Tokens”，当用户粘贴了数万字超长文本时弹出“建议开启自动浓缩模式”提醒，引导用户自发节约用量。""",
        "followups": """## 追问 1：只带最近 4 轮对话，用户如果问“我一开始提到的名字是什么”导致大模型失忆怎么办？

**回答要点**：
采用“滑动窗口 + 关键实体提取”：当早期对话滑出窗口时，由模型或本地规则提取出其中的核心键值对（如用户姓名、目标编程语言）存入持久化的 `Memory` 上下文字段，作为系统 Prompt 的一部分持续携带。

---

## 追问 2：为什么不能把所有 Token 节约策略全部交给后端做，前端插手的价值在哪？

**回答要点**：
前端是直接与用户交互的第一触点：
1. 前端能即时感知用户的输入取消、按键防抖和页面销毁，能够**在网络发出前主动拦截**；
2. 前端做本地语义缓存零延迟秒开，能带来极致的用户体验提升。"""
    },
    {
        "id": "fe-ai-054",
        "title": "如何建立AI生成内容质量评估体系？前端交互层面如何设计反馈？",
        "difficulty": "medium",
        "question": "如何建立AI生成内容的质量评估体系？前端可在交互层面提供哪些反馈机制（如评分、标注、修正）？",
        "answer": """### 一句话总结

前端反馈是**强化学习人类反馈（RLHF）与模型迭代的数据金矿**。在交互层设计**“显式轻量反馈（点赞/点踩 + 标签归因） + 隐式行为埋点（复制/重新生成/停留时长） + 原生行内高亮纠错标注（Inline Editing）”**三层体系，全方位捕获高质量偏好数据集回传数据飞轮。

---

### 详细回答

#### 1. 显式轻量反馈（Explicit Feedback）
- **点赞 / 点踩（Thumbs Up/Down）**：放置在每条回答底部；
- **二级归因弹窗**：点击“点踩”后，不宜立刻关闭，浮出低侵入气泡收集细分原因（如“事实错误”、“未遵循指令”、“含有有害内容”），降低用户反馈门槛。

#### 2. 隐式行为数据捕获（Implicit Feedback）
- 用户往往不主动点赞，但其行为真实反映质量：
  - **正面信号**：点击“一键复制”代码、点击“导出文档”、在该回答区域停留精读 > 15 秒；
  - **负面信号**：在回答刚吐出 3 个字瞬间点击“停止生成”、紧接着点击“重新生成”、或者追问“你说的完全不对”。

#### 3. 行内直接修改（Direct Correction）
- 允许用户双击 AI 的回答进入“编辑模式”直接修正错别字或调整语句；
- 这一操作能产生最珍贵的 **`<Prompt, BadOutput, HumanCorrectedOutput>` 监督微调黄金对齐数据对**。

---

### 核心代码片段（极简记法）

```javascript
// 隐式满意度埋点示例
function trackAIQuality(messageId) {
  let startTime = Date.now();

  return {
    onCopy: () => reportMetric(messageId, 'IMPLICIT_POSITIVE', { action: 'COPY' }),
    onRegenerate: () => reportMetric(messageId, 'IMPLICIT_NEGATIVE', { action: 'REGENERATE' }),
    onLeave: () => {
      const duration = Date.now() - startTime;
      if (duration > 15000) reportMetric(messageId, 'IMPLICIT_POSITIVE', { duration });
    }
  };
}
```

---

### 面试加分项

- **反馈闭环可视化**：当用户点踩并提交修正后，界面提示“感谢您的修正，已将建议反馈给模型训练组”，让用户拥有真实的参与感与掌控感。""",
        "followups": """## 追问 1：前端如何防止恶意用户频繁狂刷点赞/点踩污染训练数据集？

**回答要点**：
1. 客户端设备指纹与用户 ID 绑定，单条消息仅允许投票一次且支持撤销；
2. 前端上报埋点接口增加防抖与频次限制（Rate Limiting）；
3. 服务端分析反作弊评分（如只停留 0.1 秒的无意义连击直接剔除）。

---

## 追问 2：A/B 测试两个不同大模型生成结果时，前端界面如何设计评估？

**回答要点**：
采用 **双盲竞技场模式（Arena Side-by-side）**：同一个 Prompt 左右两栏同时流式输出，隐去模型名称（标记为 Model A 和 Model B），用户阅读后点击“左边更好 / 右边更好 / 都不好”，投票后揭晓真实模型并沉淀 ELO 天梯积分数据。"""
    },
    {
        "id": "fe-ai-055",
        "title": "在处理AI幻觉时，前端可以设计哪些实时提示与用户教育交互？",
        "difficulty": "medium",
        "question": "在处理AI幻觉（Hallucination）时，前端可以设计哪些实时提示与用户教育交互？",
        "answer": """### 一句话总结

治理 AI 幻觉的核心是**“前端可视化事实溯源（Source Citation） + 不确定性置信度着色 + 交互式反事实校验”**。通过将生成内容中的断言与检索知识库片段建立**带角标的数字引用链接**，悬停高亮展示原文证据；对低置信度表述添加下划线预警，并在关键决策场景强制弹出免责确认。

---

### 详细回答

#### 1. 可点击的事实引用角标（Citations）
- 类似 Perplexity 交互：文本中插入 `[1]`、`[2]` 引用徽章；
- **交互设计**：
  - 鼠标悬停（Hover）在角标上：弹出侧滑抽屉展示来源网页标题、权威域名与原文章节切片；
  - 点击跳转至知识库原始 PDF 并自动定位至对应高亮行。

#### 2. 置信度热力图（Confidence Visualizer）
- 大模型接口支持返回 token logprobs（对数概率）；
- 前端将概率转换为置信度数值（0~100%）：
  - 高置信度：正常字色；
  - 极低置信度（可能胡说八道）：文字底部加虚线波浪提示，Hover 提示“该段落缺乏明确事实依据，请谨慎核实”。

#### 3. 显式免责与反思引导
- 输入框常驻微提示：“AI 生成的内容可能产生错误，关键决策请核对原始事实”；
- 提供一键“交叉验证”按钮：点击后自动触发另一款大模型或调用搜索引擎对该回答进行事实性查证。

---

### 核心代码片段（极简记法）

```javascript
// 渲染带来源溯源角标的 Markdown
function CitationBadge({ sourceId, sourceData }) {
  return (
    <Tooltip content={<div className="source-preview">{sourceData.snippet}</div>}>
      <sup className="citation-badge" onClick={() => window.open(sourceData.url)}>
        [{sourceId}]
      </sup>
    </Tooltip>
  );
}
```

---

### 面试加分项

- **代码块一键执行沙箱防幻觉**：对于 AI 生成的代码，前端内嵌 WebContainer 或 Sandpack 在线沙箱提供“一键运行验证”按钮，用户运行无报错才放心地复制，用真实运行结果对抗代码幻觉。""",
        "followups": """## 追问 1：如果大模型伪造了一个根本不存在的虚假 URL 链接，前端怎么防御？

**回答要点**：
前端在解析 Markdown 中的超链接时，必须进行安全过滤与活性检测：
1. 校验 URL 协议合法性（只放行 `http:` 和 `https:`，过滤 `javascript:` 伪协议防 XSS）；
2. 外链跳转时展示安全警示跳板页（“您正在离开本站，该链接由 AI 提供，注意资金安全”）。

---

## 追问 2：流式生成过程中，角标 [1] 如果被打碎成 '[' 和 '1' 两个 chunk 到达，如何防止界面闪烁？

**回答要点**：
使用流式正则缓冲：在渲染前扫描末尾未闭合的角标符号（如匹配到末尾是 `[` 时暂缓输出，等下一个 chunk 凑齐 `[1]` 时再作为整体组件原子化渲染）。"""
    },
    {
        "id": "fe-ai-056",
        "title": "如何实现前端本地敏感词过滤与内容安全审核？",
        "difficulty": "medium",
        "question": "如何实现前端本地的敏感词过滤与内容安全审核，在发送至AI服务前进行初步筛查？",
        "answer": """### 一句话总结

前端本地合规过滤采用**“Aho-Corasick 多模式匹配算法（AC 自动机）或前缀树（Trie Tree）结合拼音/变体归一化”**。在请求发出前对 Prompt 执行毫秒级本地扫描；提前拦截明显的涉政、暴恐、个人敏感隐私（手机号、身份证、API Key）数据，实现零网络开销、即时拦截提示并保护企业隐私不外泄。

---

### 详细回答

#### 1. 为什么用 AC 自动机而不是写 10,000 个正则表达式？
- 若用数组 `words.some(w => text.includes(w))`，时间复杂度是 $O(M \times N)$，词库过万时页面直接卡死；
- **AC 自动机（Aho-Corasick）**：预先根据敏感词构建字典树并设置失败指针（Fail Pointer），只需对目标文本**单次线性扫描**（时间复杂度 $O(N)$），扫描万字长文仅需几毫秒。

#### 2. 对抗文本变体与混淆（Text Normalization）
- 用户经常通过拼音、繁体字、空格插入、特殊符号分隔绕过检测（如 `敏 感 词`、`mǐngǎn`）；
- 前端在匹配前执行标准化流水线：
  1. 繁体转简体；
  2. 剔除标点与空格缩进；
  3. 全角字符转半角。

#### 3. 隐私数据脱敏（PII Sanitization）
- 正则匹配手机号、中国大陆身份证号、银行卡号、JWT 凭证；
- 提示用户：“检测到您的输入包含手机号，已自动替换为 `[PHONE]` 脱敏发送”。

---

### 核心代码片段（极简记法）

```javascript
// 基于 Trie 树的前缀快速匹配骨架
class SensitiveWordFilter {
  constructor(wordList) {
    this.root = {};
    for (const word of wordList) {
      let node = this.root;
      for (const char of word) {
        node[char] = node[char] || {};
        node = node[char];
      }
      node.isEnd = true;
    }
  }

  hasSensitive(text) {
    for (let i = 0; i < text.length; i++) {
      let node = this.root;
      for (let j = i; j < text.length; j++) {
        if (!node[text[j]]) break;
        node = node[text[j]];
        if (node.isEnd) return true; // 命中敏感词！
      }
    }
    return false;
  }
}
```

---

### 面试加分项

- **安全防御纵深认知（Defense in Depth）**：必须清醒认识到**前端的本地过滤永远只能用于“提升体验与粗筛”**，绝不能作为唯一安全防线。黑客可轻松通过控制台绕过前端 JS，因此后端和模型网关必须保留最终严格的安全过滤关卡。""",
        "followups": """## 追问 1：敏感词库通常有几万个词，打包在前端 JS 里会导致包体积剧增，怎么解决？

**回答要点**：
1. 构建时将词库压缩为 **布隆过滤器（Bloom Filter）或紧凑二进制 TypedArray**，几十万词可压缩至几百 KB；
2. 采用动态分包异步拉取并永久缓存于 IndexedDB，首屏不打包词库。

---

## 追问 2：敏感词如果命中，前端交互上怎么提示最友好？

**回答要点**：
输入框下方弹出非侵入式琥珀色警告气泡：“您的输入中包含不合规词汇「***」，请修改后再试”，并将光标自动选中该词，切忌简单粗暴报一个“系统错误”让用户摸不着头脑。"""
    },
    {
        "id": "fe-ai-057",
        "title": "请设计一个前端实验平台，支持对模型参数与Prompt进行A/B测试",
        "difficulty": "medium",
        "question": "请设计一个前端实验平台，支持对AI模型参数（温度、top_p）、Prompt模板、UI布局进行A/B测试。",
        "answer": """### 一句话总结

实验平台采用**“统一分流哈希引擎（Deterministic Hash Allocator） + 声明式实验上下文（Experiment Context） + 埋点链路贯穿”**。根据用户唯一 ID 与实验 Key 计算散列值分流（如 50% 对照组走旧 Prompt，50% 实验组走新版带有 CoT 的 Prompt）；所有网络请求与点击转化埋点自动携带实验版本 Tag，为数据看板提供闭环归因依据。

---

### 详细回答

#### 1. 核心架构设计
- **分流一致性（Stickiness）**：同一个用户多次刷新必须稳定命中同一分组，避免体验精神分裂；
- **分层正交（Layered Orthogonal Experiments）**：
  - 第一层：算法参数实验（温度 0.2 vs 0.7）；
  - 第二层：UI 交互实验（侧边栏抽屉 vs 居中全屏对话）；
  - 两层实验互不影响，各自独立正交哈希。

#### 2. 前端消费与声明式注入
通过 React Context 提供 `useExperiment(expKey)` Hook，组件按需读取当前分流结果与变体配置：
```javascript
const { variant, config } = useExperiment('prompt_v2_exp');
// variant: 'control' | 'treatment'
// config: { temperature: 0.3, promptTemplate: '...' }
```

---

### 核心代码片段（极简记法）

```javascript
import MurmurHash3 from 'imurmurhash';

function getExperimentVariant(userId, experimentKey, variants = ['A', 'B']) {
  // 基于一致性哈希稳定命中
  const hash = MurmurHash3(`${userId}:${experimentKey}`).result();
  const index = Math.abs(hash) % variants.length;
  return variants[index];
}

// 消费
const userGroup = getExperimentVariant(currentUser.id, 'ai_temp_test');
const temperature = userGroup === 'A' ? 0.2 : 0.8;
```

---

### 面试加分项

- **白名单强制调试模式（QA Override）**：在 URL 参数中支持 `?_exp_override=ai_temp_test:B`，方便测试和产品人员一键强行指定实验分支验证效果，无需反复切换账号。""",
        "followups": """## 追问 1：实验分流逻辑是放在前端计算好，还是每次由后端接口下发好？

**回答要点**：
推荐混合模式：首屏由后端将该用户当前所有命中的实验配置清单打包随页面一次性下发（SSR 注入或初始化接口）；前端 SDK 本地纯内存求值，消除每次调用的网络等待。

---

## 追问 2：A/B 测试的核心指标（North Star Metric）在 AI 场景下看什么？

**回答要点**：
综合关注：
1. **正向指标**：用户提问轮数、留存率、点赞率、采纳率（Acceptance Rate）；
2. **负向指标**：点踩率、提前停止生成率、单次会话 Token 成本。"""
    },
    {
        "id": "fe-ai-058",
        "title": "如何用WebAssembly在前端运行轻量AI模型实现离线推理？",
        "difficulty": "hard",
        "question": "如何用WebAssembly在前端运行轻量级AI模型（如TinyLLM、蒸馏模型），实现离线推理？",
        "answer": """### 一句话总结

前端离线推理采用**“WebLLM / llama.cpp 编译为 WASM + WebGPU 硬件着色器加速 + 流式内存量化加载”**。将 4-bit 量化后的轻量模型（如 Qwen2-0.5B、Phi-3-mini）直接部署在静态 CDN 上；前端借助 WebGPU 并发调度 GPU 计算核心执行矩阵运算，实现**完全断网环境下在浏览器内实时吐字推理**。

---

### 详细回答

#### 1. 为什么纯 WASM CPU 推理大模型不现实？
- 大语言模型单次生成需要不断遍历几十亿个参数矩阵；
- 纯 CPU 算力极为有限，WASM CPU 跑 1B 模型通常只有 1~2 Token/s，卡顿无法使用；
- 必须依赖 **WebGPU API**，直接调用显卡的 Compute Shader 实现硬件并行加速。

#### 2. 模型下载与缓存工程
- 即使是 4-bit 量化模型，体积也有 1~2 GB；
- **分块流式加载**：将大模型权重切分为多个 50MB 的 `.bin` 文件并发下载；
- **进度通知**：向用户展示精确的“模型离线包下载中 45%”进度条；
- **Cache API 永久固化**：存入浏览器 CacheStorage，用户后续打开零耗流量。

---

### 核心代码片段（极简记法）

```javascript
import * as webllm from '@mlc-ai/web-llm';

// 1. 初始化 WebGPU 推理引擎
const engine = new webllm.MLCEngine();
engine.setInitProgressCallback((report) => console.log(report.text)); // 进度更新

// 2. 加载本地/CDN 模型
await engine.reload('Qwen2-0.5B-Instruct-q4f16_1-MLC');

// 3. 纯本地流式推理（断网也能跑！）
const chunks = await engine.chat.completions.create({
  messages: [{ role: 'user', content: '前端怎么做离线化？' }],
  stream: true
});
for await (const chunk of chunks) {
  console.log(chunk.choices[0]?.delta?.content || '');
}
```

---

### 面试加分项

- **设备兼容性降级矩阵**：在加载模型前调用 `navigator.gpu?.requestAdapter()`，若检测到低端集成显卡或内存小于 4GB 的移动设备，友好提示“当前设备硬件算力不足，已自动切换为云端模型”，防止撑爆浏览器内存崩溃。""",
        "followups": """## 追问 1：WebGPU 在移动端 iOS Safari 上的支持度如何？

**回答要点**：
iOS 17+ 已经开始逐步支持 WebGPU，但默认配置对单个 Tab 的显存配额有严格限制（通常在 1~2GB 上下），运行超大模型容易触发 OOM（Out of Memory）导致页面黑屏刷新，因此移动端应优先运行 0.5B 级别的小模型。

---

## 追问 2：浏览器关闭重新打开，下载好的 1GB 模型文件会被浏览器自动清理吗？

**回答要点**：
默认可能被浏览器在存储空间紧张时当成普通缓存清理。
解决办法是调用 **`navigator.storage.persist()`** 请求“持久化存储权限”。一旦用户或系统授权，该域名下的 CacheStorage 数据将变为永久持久化，浏览器绝不会静默清理。"""
    },
    {
        "id": "fe-ai-059",
        "title": "在AI多轮对话中，如何设计上下文窗口的管理策略？",
        "difficulty": "medium",
        "question": "在AI多轮对话中，如何设计上下文窗口的管理策略（如滑动窗口、关键信息提取、自动摘要）？",
        "answer": """### 一句话总结

上下文管理策略采用**“层级金字塔模型（Hierarchical Pyramid）”**。在首部固化不可撼动的 **System Prompt（设定与约束）**；尾部保留最新 $N$ 轮的 **精确滑动窗口（Raw Turns）**；中部被淘汰的超长早期历史则在后台**异步浓缩为自动摘要（Rolling Summary）与关键记忆事实表（Key Facts）**，实现无限轮次对话而 Token 恒定在安全水位。

---

### 详细回答

#### 1. 传统无脑携带全量历史的危害
- 触发大模型上下文截断上限报错（Context Window Exceeded）；
- Token 费用以指数级递增；
- 发生“中间遗忘（Lost in the Middle）”，历史消息过长反而导致模型找不到关键指令。

#### 2. 三级上下文编排设计
1. **Layer 1：持久系统人格（Pinned System Context）**：包含核心业务指令和用户全局 Profile；
2. **Layer 2：动态压缩记忆（Dynamic Memory Summary）**：
   - 当总 Token 接近阈值（如预警线的 70%）时；
   - 触发后台静默调用一次小模型：“总结以下第 1~20 轮对话的要点与已达成结论”；
   - 将原 20 轮消息替换为一条系统级 Summary 消息；
3. **Layer 3：最新上下文视口（Recent Sliding Window）**：保持原汁原味的最近 3~5 轮对话，确保指代词（如“它”、“刚才那个”）理解准确。

---

### 核心代码片段（极简记法）

```javascript
function assembleContext(systemPrompt, summaryText, recentMessages) {
  const context = [{ role: 'system', content: systemPrompt }];

  if (summaryText) {
    context.push({ role: 'system', content: `【前序背景总结】: ${summaryText}` });
  }

  // 拼接最近活跃窗口
  return context.concat(recentMessages);
}
```

---

### 面试加分项

- **前端透明感知**：在界面消息流中，被折叠压缩的历史上方展示一条优雅的分界提示线：“以上历史已被自动浓缩为记忆点（点击可展开完整回顾）”，既保障 Token 优化，又赋予用户完全的知情权。""",
        "followups": """## 追问 1：前端如何精准计算当前历史消息所消耗的真实 Token 数量？

**回答要点**：
引入与模型对应轻量分词库（如基于 WebAssembly 封装的 `gpt-tokenizer` 或 `@dqbd/tiktoken`）；在前端直接传入字符串执行 `encoding.encode(text).length`，与服务端分词算法 100% 字节对齐。

---

## 追问 2：如果在摘要浓缩时，模型把关键的密码或代码 Bug 细节给漏掉了怎么办？

**回答要点**：
配合使用“向量化记忆检索（RAG）”作为补充：被浓缩沉淀的原始消息切片存入本地向量库，当最新提问触发关键词匹配时，精准捞出原始具体对话切片重新贴在 Prompt 中，两全其美。"""
    },
    {
        "id": "fe-ai-060",
        "title": "如何实现AI生成结果的一键格式化（Markdown转富文本、代码缩进等）？",
        "difficulty": "medium",
        "question": "如何实现AI生成结果的“一键格式化”（如Markdown转富文本、代码缩进、表格对齐）？",
        "answer": """### 一句话总结

一键格式化采用**“AST 抽象语法树转换流水线 + Prettier 浏览器端运行时 + Clipboard API 多 MIME 类型写入”**。利用 `unified / remark` 将 Markdown 解析为语法树并规范化重排；代码块交给在浏览器中运行的 `prettier/standalone` 自动美化缩进；复制时同时写入 `text/html` 与 `text/plain`，支持一键无损粘贴至飞书、Notion 或 Word。

---

### 详细回答

#### 1. 痛点：为什么普通复制会导致排版全乱？
- 大模型生成的表格往往存在 Markdown 竖线未对齐、代码缺少缩进空格；
- 若只复制纯文本到剪贴板，粘贴到富文本编辑器（如微信公众号、飞书文档）时会退化为原始的 `###` 和一团乱码。

#### 2. 三步格式化技术链路
1. **代码美化（Prettier Standalone）**：
   引入浏览器专用打包的 `prettier/standalone`，对检测出的 JS/Python 代码执行格式化，对齐括号与缩进；
2. **Markdown 树状清洗（Remark Pipeline）**：
   规范列表间距、自动补齐表格缺失的表头单元格；
3. **双通道剪贴板写入（HTML + PlainText）**：
   利用 `navigator.clipboard.write([new ClipboardItem({ 'text/html': htmlBlob, 'text/plain': textBlob })])`。

---

### 核心代码片段（极简记法）

```javascript
// 一键带格式复制到剪贴板
async function copyAsRichText(markdownText, renderedHtml) {
  const textBlob = new Blob([markdownText], { type: 'text/plain' });
  const htmlBlob = new Blob([renderedHtml], { type: 'text/html' });

  // 现代 Clipboard API 同时注入富文本与纯文本
  await navigator.clipboard.write([
    new ClipboardItem({
      'text/plain': textBlob,
      'text/html': htmlBlob
    })
  ]);
}
```

---

### 面试加分项

- **Word / 邮件专用内嵌内联样式转换（Juice）**：Word 和旧版邮件客户端不支持外部 CSS 类名。在转换 HTML 时通过类似 `juice` 的轻量处理将 CSS 样式转换为 `style="..."` 行内内嵌样式，粘贴到 Word 中排版分毫不差。""",
        "followups": """## 追问 1：Prettier 的 standalone 打包体积较大（包含各种语言解析器约几 MB），怎么避免拖慢主页面？

**回答要点**：
采用动态 `import()` 按需加载！
用户不点击“代码格式化”按钮，绝不下发 Prettier 资源；并且将格式化计算任务放到 Web Worker 中执行，防止几十万行超长代码格式化时冻结 UI。

---

## 追问 2：在非 HTTPS 环境或者旧浏览器下，Clipboard API 报错怎么办？

**回答要点**：
必须编写降级容灾逻辑：动态创建一个隐藏的 `textarea`，设值后调用旧版 `document.execCommand('copy')` 并捕获异常，确保在任何极端环境下复制功能不崩溃。"""
    }
]

for item in DATA:
    qdir = os.path.join(QUESTIONS_DIR, item['id'])
    os.makedirs(qdir, exist_ok=True)
    with open(os.path.join(qdir, 'question.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {item['title']}\n\n{item['question']}\n")
    with open(os.path.join(qdir, 'answer.md'), 'w', encoding='utf-8') as f:
        f.write(item['answer'].strip() + '\n')
    with open(os.path.join(qdir, 'followups.md'), 'w', encoding='utf-8') as f:
        f.write(item['followups'].strip() + '\n')

print(f"Generated {len(DATA)} questions successfully (fe-ai-041 ~ fe-ai-060)!")
