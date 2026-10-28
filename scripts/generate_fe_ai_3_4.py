import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-ai-021",
        "title": "在大型AI应用中，如何用Zustand管理多轮对话、生成任务与配置？",
        "difficulty": "medium",
        "question": "在大型AI应用中，如何用Zustand或Redux Toolkit管理多轮对话、生成任务、用户配置等复杂状态？",
        "answer": """### 一句话总结

大型 AI 应用推荐使用 **Zustand 结合切片模式（Slice Pattern）与 Immer 中间件**。将状态解耦为 `chatSlice`（消息树与流式增量）、`taskSlice`（后台异步推理队列与状态机）和 `settingsSlice`（模型参数与本地持久化），通过**细粒度选择器（Selectors）**订阅局部状态，避免流式吐字触发全页面重渲染。

---

### 详细回答

#### 1. 为什么 Zustand 比传统 Redux 更适合流式 AI 应用？
- **零样板代码**：无需编写冗长的 Action Types 和 Reducer，直接通过 Action 函数就地更新；
- **支持瞬态更新（Transient Updates）**：流式推送每秒 30 次，Zustand 允许绕过 React 重新渲染直接通过 `getState()` 或订阅监听修改 DOM，性能极高；
- **闭包安全与原生异步支持**：在异步 Stream 流中可以随时 `get()` 读取最新状态，杜绝闭包陷阱。

#### 2. 切片架构（Slice Pattern）模块划分
- **`chatSlice`**：存储当前激活会话的 `messages` 列表、当前正在流式追加的 `activeMessageId` 与 Buffer；
- **`taskSlice`**：管理并发任务池，记录正在进行的后台 Agent 任务及其进度与 `AbortController`；
- **`settingsSlice`**：用户偏好、当前选定模型、温度参数，配合 `persist` 中间件自动落盘 `localStorage`。

---

### 核心代码片段（极简记法）

```javascript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export const useChatStore = create(immer((set) => ({
  messages: [],
  // 增量流式更新（结合 Immer 避免深拷贝性能开销）
  appendChunk: (msgId, chunk) => set((state) => {
    const msg = state.messages.find(m => m.id === msgId);
    if (msg) msg.content += chunk;
  })
})));

// 消费端使用细粒度选择器，只有该字段变动才重渲染
const content = useChatStore(state => state.messages.find(m => m.id === id)?.content);
```

---

### 面试加分项

- **选择器浅比较（shallow）**：在组件消费时使用 `useChatStore(selectSubState, shallow)`，避免每次生成新对象引用导致的组件无效重刷。""",
        "followups": """## 追问 1：在 React 外部（比如纯 JS 工具函数中），Zustand 如何读取和修改状态？

**回答要点**：
Zustand 的 Store 实例自带静态方法：直接调用 `useChatStore.getState()` 读取当前最新状态，调用 `useChatStore.setState({ ... })` 触发更新，完全不依赖 React 组件生命周期。

---

## 追问 2：为什么高频流式推流时不推荐在 Context 中直接维护消息列表？

**回答要点**：
React Context 的任何值变更都会无条件遍历触发所有消费该 Context 的子组件重新渲染，哪怕子组件使用了 `React.memo` 也会失效，导致页面出现灾难级的卡顿掉帧。"""
    },
    {
        "id": "fe-ai-022",
        "title": "设计一个状态快照系统支持AI对话完整状态序列化与恢复",
        "difficulty": "medium",
        "question": "设计一个“状态快照”系统，支持将AI对话的完整状态（包括流式中间结果）序列化保存与恢复。",
        "answer": """### 一句话总结

状态快照系统采用**“状态树纯 JSON 序列化 + 不可序列化对象（如 AbortController）解耦映射 + 版本迁移适配器”**。将整个会话的状态、参数、消息列表提取为纯数据 Schema 存入 IndexedDB/文件导出；恢复时通过反序列化工厂函数重建非纯数据逻辑对象，实现跨设备导出导入和意外刷新瞬时恢复。

---

### 详细回答

#### 1. 核心挑战：非纯数据对象的剥离
- 会话状态中包含大量的函数、网络句柄和不可序列化对象（如 `AbortController`、`EventSource` 实例、`AudioContext`）；
- 快照设计原则：**存储只存纯数据（State），逻辑和网络连接由运行时（Runtime）按需重建**。

#### 2. 快照结构体设计
```typescript
interface ChatSnapshotV1 {
  version: 1;
  snapshotId: string;
  createdAt: number;
  sessionMeta: { id: string; model: string; temperature: number };
  messages: Array<{ id: string; role: string; content: string; status: 'completed' | 'interrupted' }>;
}
```

#### 3. 版本迁移升级（Migration Pipeline）
随着业务迭代，快照 Schema 可能会改变（如新增了 `tools` 字段）。设计版本迁移函数管道：
若读取到 `version === 1`，自动经过 `migrateV1ToV2(snapshot)` 转换为最新结构，防止旧版本会话导入崩溃。

---

### 核心代码片段（极简记法）

```javascript
// 导出快照（过滤掉非纯数据）
function createSnapshot(storeState) {
  return JSON.stringify({
    version: 2,
    timestamp: Date.now(),
    messages: storeState.messages.map(m => ({ id: m.id, role: m.role, text: m.text })),
    settings: storeState.settings
  });
}

// 恢复快照
function restoreSnapshot(jsonStr, store) {
  const data = JSON.parse(jsonStr);
  const validData = runMigrations(data); // 执行版本升级校验
  store.setState({ messages: validData.messages, settings: validData.settings });
}
```

---

### 面试加分项

- **流式中断恢复状态机**：如果保存快照时某条消息恰好处于流式生成一半的状态，快照将其标记为 `status: 'interrupted'`，恢复后界面渲染“生成中断”卡片并显示“继续生成”按钮，点击后自动发起断点续传。""",
        "followups": """## 追问 1：如果快照体积超过 100MB（包含了用户上传的多模态高分辨率大图），序列化导致页面卡死怎么办？

**回答要点**：
图片或二进制附件不要转成 Base64 塞在快照 JSON 中。
应将大文件以 `Blob` 格式独立存入 IndexedDB 的附件对象表，快照 JSON 中仅保留附件的唯一 `attachmentId` 引用指针，使 JSON 序列化体积控制在百 KB 以内。

---

## 追问 2：跨设备导入快照时，如何保证安全性？

**回答要点**：
必须使用 Zod 对反序列化的快照数据进行严格的运行时校验，过滤掉任何可能包含恶意 XSS 脚本的内容（如富文本中的 `<script>` 或恶意 iframe）。"""
    },
    {
        "id": "fe-ai-023",
        "title": "如何用XState或状态图建模AI Agent的完整工作流？",
        "difficulty": "hard",
        "question": "如何用XState或状态图（Statechart）建模AI Agent的完整工作流（包括工具调用、条件分支、错误处理）？",
        "answer": """### 一句话总结

管理复杂 Agent 的核心是**杜绝布尔值状态爆炸（Boolean Explosion）**。通过有限状态机（FSM）或状态图（Statechart，如 XState），将 Agent 的运行划分为**互斥的顶层状态**；把工具调用和模型调用抽象为**异步参与者（Actors）**，并通过**守卫条件（Guards）**判断继续循环或结束，配合声明式的重试逻辑实现稳定受控的工作流。

---

### 详细回答

#### 1. 为什么“布尔标志位地狱”会彻底崩溃？
- 反例：定义了 `isLoading`、`isThinking`、`isToolRunning`、`isWaitingUser`，极易产生非法的状态组合，导致 UI 闪烁和逻辑冲突。
- 状态机优势：同一时刻有且仅有一个主状态，根本不会产生状态矛盾。

#### 2. XState 建模的核心四要素
- **Context**：存放对话历史与工具入参；
- **Events**：外部触发动作（如用户点击发送 `SUBMIT`、流式返回工具调用 `TRIGGER_TOOL`）；
- **Guards**：条件守卫（如重试次数是否超限）；
- **Actors**：将异步模型请求和本地工具执行封装为可调用的 Actor。

---

### 核心代码片段（极简记法）

```javascript
import { setup, createMachine } from 'xstate';

export const agentMachine = setup({
  guards: { canRetry: ({ context }) => context.retryCount < 3 }
}).createMachine({
  id: 'agent',
  initial: 'idle',
  context: { retryCount: 0 },
  states: {
    idle: { on: { RUN: 'thinking' } },
    thinking: {
      invoke: {
        src: 'callLLM',
        onDone: [
          { guard: 'needTool', target: 'acting' },
          { target: 'completed' }
        ],
        onError: [
          { guard: 'canRetry', target: 'thinking' },
          { target: 'failed' }
        ]
      }
    },
    acting: {
      invoke: {
        src: 'executeTool',
        onDone: { target: 'thinking' } // 工具结果回填继续思考
      }
    },
    completed: { type: 'final' },
    failed: {}
  }
});
```

---

### 面试加分项

- **人机协同（Human-in-the-Loop）**：在敏感工具调用前插入 `waitingApproval` 状态，强依赖用户手动点击授权后才流转到执行。""",
        "followups": """## 追问 1：如果一个复杂任务中，模型同时返回了多个独立的工具调用，状态机如何处理？

**回答要点**：
使用 XState 的并行状态（Parallel States）或在 Actor 内部使用 `Promise.allSettled` 并发调度，全部完成后触发聚合事件统一流转回思考状态。

---

## 追问 2：状态机的持久化与页面刷新恢复怎么做？

**回答要点**：
XState 支持通过 `getPersistedSnapshot()` 导出状态树 JSON，刷新后传入 `createActor(machine, { snapshot })` 即可瞬间无缝恢复。"""
    },
    {
        "id": "fe-ai-024",
        "title": "在微前端架构下，多个AI功能模块如何共享当前模型版本状态？",
        "difficulty": "medium",
        "question": "在微前端架构下，多个AI功能模块需要共享“当前模型版本”状态，如何设计跨应用状态同步方案？",
        "answer": """### 一句话总结

微前端跨应用状态共享采用**“主应用全局发布订阅中心（EventBus / Actions） + 跨应用 CustomEvent 或 BroadcastChannel”**解耦通信。主应用作为单一真实数据源（SSOT）下发当前模型版本，子应用通过微前端生命周期 props 注入响应式 store 引用或监听全局事件，实现无框架绑定的跨技术栈即时联动。

---

### 详细回答

#### 1. 常见方案选型对比
- **方案 A：Qiankun 的 `initGlobalState`（官方标准）**：
  主应用提供全局状态管理，子应用通过 `onGlobalStateChange` 监听变化，`setGlobalState` 触发更新；
- **方案 B：CustomEvent 自定义事件（零依赖通用）**：
  基于 `window.dispatchEvent(new CustomEvent('ai:model_change', { detail }))` 广播，兼容任意框架；
- **方案 C：BroadcastChannel API（支持跨标签页）**：
  同源下多应用、多 Tab 均能瞬间感知模型版本切换。

#### 2. 数据流治理：防止死循环广播
- 规定：**模型版本的最终修改权由主应用收敛**。子应用若想变更模型，发起请求通知主应用更新，由主应用统一向下广播，避免多个子应用互相广播产生死循环更新。

---

### 核心代码片段（极简记法）

```javascript
// 主应用初始化全局模型状态
import { initGlobalState } from 'qiankun';

const actions = initGlobalState({ currentModel: 'gpt-4o' });

// 子应用内部监听变化
export async function mount(props) {
  props.onGlobalStateChange((state, prev) => {
    if (state.currentModel !== prev.currentModel) {
      updateLocalModelConfig(state.currentModel);
    }
  });
}
```

---

### 面试加分项

- **共享状态版本对齐（TypeScript 契约）**：跨应用的全局通信事件载荷容易产生字段拼写偏差。通过在 Monorepo 中发布 `@org/micro-events` 契约包，对 `detail` 参数进行编译期强类型约束。""",
        "followups": """## 追问 1：子应用如果是 React，如何把全局模型状态优雅地接入本地的组件 Hook 中？

**回答要点**：
利用 React 18 的 `useSyncExternalStore` Hook！
将微前端的全局订阅方法包装为外部数据源，组件直接订阅即可实现高效且不掉帧的响应式渲染。

---

## 追问 2：如果子应用处于沙箱中（fakeWindow），自定义事件能冒泡到主应用吗？

**回答要点**：
普通挂载在 `fakeWindow` 上的监听器可能无法捕获外部事件。微前端框架通常会将标准事件 API（如 `addEventListener`）代理转发到顶层真实 `window` 上，确保跨沙箱事件通信畅通。"""
    },
    {
        "id": "fe-ai-025",
        "title": "请设计一个乐观更新策略，并在AI流式返回时逐步修正",
        "difficulty": "medium",
        "question": "请设计一个“乐观更新”策略，在用户发送AI请求后立即在UI中显示预期结果，再根据实际流式响应逐步修正。",
        "answer": """### 一句话总结

AI 乐观更新的核心是**“临时占位实体（Optimistic Entity） + 状态平滑过渡 + 失败无痕回滚”**。用户点击发送瞬间，UI 立即挂载一条带临时 ID 的 Assistant 占位消息并展示骨架打字动效；当首个流式 Chunk 到达时无缝将占位态转为真实生成态；若遇接口限流或报错，则自动将该条消息标记为失败并保留重发按钮。

---

### 详细回答

#### 1. 为什么 AI 场景极度需要乐观更新？
- 大模型存在较长的首字延迟（TTFT，通常 1~3 秒）；
- 若没有乐观更新，用户点击“发送”后输入框被清空，但界面毫无反应，用户会误以为卡死而频繁重复点击。

#### 2. 三阶段生命周期
1. **即时乐观呈现（0ms）**：
   - 用户消息立即入队；
   - 插入一条 `{ id: 'temp_assistant', content: '', status: 'pending' }`，界面渲染脉冲波或打字光标；
2. **渐进式覆写（首字到达）**：
   - 将 `status` 切为 `'streaming'`，用服务端返回的真实 `messageId` 替换临时 ID；
   - 逐字追加内容；
3. **异常回滚（Rollback）**：
   - 若遇到 500/429 报错，将该消息切换为错误卡片，用户输入的文字自动放回输入框或提供“一键重试”。

---

### 核心代码片段（极简记法）

```javascript
function sendPrompt(prompt) {
  const tempUserMsg = { id: Date.now(), role: 'user', content: prompt };
  const tempAiMsg = { id: `temp_${Date.now()}`, role: 'assistant', content: '', isOptimistic: true };

  // 1. 立即更新 UI
  setMessages(prev => [...prev, tempUserMsg, tempAiMsg]);

  // 2. 发起请求并流式修正
  fetchStream(prompt, {
    onFirstChunk: (realId) => {
      // 替换真实 ID
      updateMessage(tempAiMsg.id, { id: realId, isOptimistic: false });
    },
    onChunk: (delta) => appendChunk(delta),
    onError: () => markMessageFailed(tempAiMsg.id)
  });
}
```

---

### 面试加分项

- **微动效协同**：乐观更新不仅仅是塞一条空数据，配合 CSS 缓动动画让输入框文字飞入消息流，消除感知延迟。""",
        "followups": """## 追问 1：如果连续快速发送多条乐观消息，如何保证消息之间的先后顺序不发生倒错？

**回答要点**：
维护一个本地单调递增的客户端版本号（`clientSeq`）或队列链表。即使网络响应可能乱序，前端始终严格按照本地入队时间戳进行渲染排序。

---

## 追问 2：乐观更新回滚时，如何保存用户输入的内容防止丢失？

**回答要点**：
失败时切忌直接把该条消息从 DOM 中物理删除！
应该将其标记为 `status: 'failed'`，并在下方展示“重试”按钮和“编辑重新发送”按钮，将原始 Prompt 保留展示，保护用户的心血。"""
    },
    {
        "id": "fe-ai-026",
        "title": "如何用Immer优化AI对话列表的不可变更新？",
        "difficulty": "easy",
        "question": "如何用immer或immutable.js优化AI对话列表的不可变更新，避免深拷贝导致的性能问题？",
        "answer": """### 一句话总结

高频流式推流下，手写深拷贝解构（`[...list, { ...item, text }]`）每次都会创建全新对象引用，导致性能与 GC 压力剧增。**Immer 基于 ES6 Proxy 实现结构共享（Structural Sharing）**，允许以“可变（Mutable）”的直观写法修改深层嵌套的草稿（Draft），底层仅对被修改的节点及其父路径创建新对象，其余节点完全复用旧内存引用。

---

### 详细回答

#### 1. 传统展开运算符（Spread Operator）的痛点
- AI 对话消息通常是嵌套结构：`conversations[activeId].messages[targetIndex].content`；
- 原生深层不可变更新写法极度反人类，层层解构不仅容易写错，而且每一次流式 Token 都会对中间所有层级分配新内存，触发高频垃圾回收（GC Pause）导致页面微卡顿。

#### 2. Immer 的结构共享魔法
- Immer 会给源对象包装一层 Proxy 形成 `draft`；
- 你直接写 `draft.content += token`；
- 执行完毕后，Immer 冻结变更并仅生成改动链路上的浅拷贝，未修改的其他数百条历史消息**内存指针保持不变**。
- **React.memo 完美生效**：未修改的历史消息组件其 props 引用不变，直接跳过重渲染！

---

### 核心代码片段（极简记法）

```javascript
import { produce } from 'immer';

// 高频流式追加：极简直观，且结构共享
const nextMessages = produce(messages, (draft) => {
  const currentMsg = draft.find(m => m.id === activeId);
  if (currentMsg) {
    currentMsg.content += newChunk; // 直观可变修改！
  }
});
```

---

### 面试加分项

- **对流式场景的高频微调（enablePatches）**：Immer 支持生成 JSON Patch。在多人实时协同对话场景中，通过 `produceWithPatches` 可以直接导出最小变更 Diff 操作包通过 WebSocket 广播，带宽占用极小。""",
        "followups": """## 追问 1：在每秒 50 次 Token 的极高频流式推流下，Immer 本身的 Proxy 开销会不会成为瓶颈？

**回答要点**：
会有轻微开销。在极端追求性能的场景下：
1. 流式生成期间仅在内存中维护纯可变字符串 Buffer；
2. 配合 `requestAnimationFrame` 做帧级节流；
3. 仅在节流刷新 UI 时调用一次 Immer，将 Proxy 创建频次限制在每秒 30~60 次以内，完全无性能压力。

---

## 追问 2：Immer 配合 Redux Toolkit / Zustand 时怎么使用？

**回答要点**：
Redux Toolkit 的 `createSlice` 内部已经默认集成了 Immer，在 reducer 里直接写赋值修改即可；Zustand 则只需添加 `immer` 中间件包裹 store 定义函数即可。"""
    },
    {
        "id": "fe-ai-027",
        "title": "设计一个状态版本控制系统，支持AI对话历史的任意回退与分支合并",
        "difficulty": "hard",
        "question": "设计一个“状态版本控制”系统，支持AI对话历史的任意回退、分支创建与合并（类似Git）。",
        "answer": """### 一句话总结

对话历史版本控制采用**“有向无环图（DAG）/ 对话树结构”**建模。每个消息节点维护唯一 `id`、`parentId` 与 `childrenIds`；“重新生成”或“分支编辑”本质是在父节点上创建子分支，前端通过**指针（Current Leaf Pointer）**追踪当前活跃的会话路径，实现类似 Git 的时光倒流、分支切换与对比合并。

---

### 详细回答

#### 1. 传统线性数组建模的致命缺陷
- 绝大多数应用将消息存为数组 `Message[]`；
- 当用户对第 3 条消息点击“重新生成”时，旧回答会被粗暴覆盖，用户无法查看之前的回答，也无法进行多分支探索。

#### 2. 对话树（Tree-based Architecture）核心设计
- **节点定义**：
  ```typescript
  interface Node {
    id: string;
    parentId: string | null;
    content: string;
    children: string[]; // 支持多个子分支
  }
  ```
- **当前路径回溯**：
  给定当前叶子节点 ID，自底向上通过 `parentId` 递归查找，即可在线性时间 $O(D)$ 内提取出当前分支的完整对话上下文。

#### 3. 分支切换交互
- 在拥有多个分支的节点下方展示翻页器组件：`< 2 / 3 >`；
- 点击切换时，更新当前激活的叶子节点指针，视图瞬间切换为对应分支。

---

### 核心代码片段（极简记法）

```javascript
// 获取当前激活分支的线性消息列表
function getActiveBranchMessages(nodesMap, currentLeafId) {
  const branch = [];
  let curr = nodesMap[currentLeafId];

  while (curr) {
    branch.unshift(curr);
    curr = curr.parentId ? nodesMap[curr.parentId] : null;
  }
  return branch; // 返回给 UI 渲染的平铺数组
}
```

---

### 面试加分项

- **分支 Diff 对比视图**：允许用户选择同一个问题的两个不同模型生成分支，双栏并排渲染，直观对比不同 Prompt 或不同模型的生成质量。""",
        "followups": """## 追问 1：如果要将对话树持久化到后端数据库，表结构怎么设计？

**回答要点**：
经典邻接表（Adjacency List）设计：每行记录包含 `id`、`session_id`、`parent_id`、`content`，配合 `parent_id` 建立索引；查询时通过 SQL 递归公共表表达式（WITH RECURSIVE）一次性拉取整棵树。

---

## 追问 2：如果分支过多导致内存膨胀，前端如何优化？

**回答要点**：
非活跃分支的沉重内容（如生成的图片 Base64、富媒体卡片）在前端仅保留元数据，正文从内存卸载；当用户切换到该分支时再从 IndexedDB 按需拉取并激活。"""
    },
    {
        "id": "fe-ai-028",
        "title": "在离线优先AI应用中，如何用TanStack Query管理本地缓存与网络同步？",
        "difficulty": "medium",
        "question": "在离线优先的AI应用中，如何用RxJS或@tanstack/query管理本地缓存与网络状态的同步？",
        "answer": """### 一句话总结

离线优先 AI 应用采用 **TanStack Query（React Query）结合 `persistClient` 插件与离线突变队列（Offline Mutation Queue）**。以本地 IndexedDB 作为持久化二级缓存，在离线断网状态下由缓存即时响应会话历史；网络恢复后自动触发后台增量同步与失败任务自动回放。

---

### 详细回答

#### 1. 为什么 TanStack Query 契合离线优先？
- 内置开箱即用的网络状态感知：`networkMode: 'offlineFirst'`；
- 当网络断开时，请求不会报错，而是自动进入暂停挂起状态（`paused`）；
- 一旦浏览器触发 `online` 事件，自动无缝恢复请求。

#### 2. 持久化插件：createSyncStoragePersister
- 配置 `persistQueryClient`：将 React Query 内存中的 Query Cache 同步镜像写入 IndexedDB；
- 哪怕用户在飞机离线模式下冷启动页面，React Query 瞬间从 IndexedDB 载入上次的对话数据，实现零秒秒开。

#### 3. 离线提问暂存（Offline Mutations）
- 用户断网时输入问题并点击发送；
- 突变（Mutation）将提问追加至本地缓存中渲染，同时将网络任务存入离线持久化队列；
- 联网瞬间按顺序依次将队列任务推送到服务端。

---

### 核心代码片段（极简记法）

```javascript
import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createIDBPersister } from './idbPersister';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst', // 离线优先读取本地
      gcTime: 1000 * 60 * 60 * 24 * 7 // 保留7天本地缓存
    }
  }
});

// 持久化到 IndexedDB
persistQueryClient({ queryClient, persister: createIDBPersister() });
```

---

### 面试加分项

- **数据冲突仲裁（Last-Write-Wins vs 向量时钟）**：当用户在离线状态下编辑了某条消息，而在另一台联网设备上也修改了同一会话，重新联网时根据版本号和时间戳进行自动合并或提示冲突解决。""",
        "followups": """## 追问 1：离线状态下，大模型推理本身如何进行？

**回答要点**：
若完全离线，可通过 WebAssembly / WebGPU 在前端本地运行轻量蒸馏模型（如 WebLLM 运行 Llama 3-8B 或 ONNX Runtime Web）；若本地硬件无法支撑，则只允许离线浏览历史并排队暂存任务，提示联网后自动推理。

---

## 追问 2：TanStack Query 如何处理长文本流式请求？

**回答要点**：
TanStack Query 擅长传统的 Promise 请求，流式通常配合 `useMutation` 触发：在 mutation 函数中拉取 stream，并在 `onChunk` 回调中通过 `queryClient.setQueryData` 手动更新缓存树。"""
    },
    {
        "id": "fe-ai-029",
        "title": "如何用Jotai或Recoil原子机制实现AI生成参数细粒度响应式更新？",
        "difficulty": "medium",
        "question": "如何用Recoil或Jotai的原子（Atom）机制实现AI生成参数的细粒度响应式更新（如温度、top_p）？",
        "answer": """### 一句话总结

传统集中式 Store 修改单个参数（如滑动调节 Temperature）容易引发整个设置抽屉乃至聊天界面的无差别重渲染。**原子化状态库（如 Jotai）将每个参数解耦为独立的 Atom 原语**；仅有真正引用了 `temperatureAtom` 的滑块和展示组件会触发微更新，实现了与输入流渲染彻底隔离的极致渲染性能。

---

### 详细回答

#### 1. 集中式 Store vs 原子化 Atom
- **集中式（Redux/Zustand）**：所有参数存在单一全局对象中，虽然能靠选择器优化，但配置项多达数十个时心智负担重；
- **原子化（Jotai）**：自底向上的设计模式，状态以原子（Atom）为最小单位，天然具备响应式依赖追踪。

#### 2. 派生原子（Derived Atoms）实现参数组合与校验
- Jotai 允许定义只读或读写派生原子：
  ```javascript
  // 基础原子
  export const tempAtom = atom(0.7);
  export const topPAtom = atom(0.9);

  // 派生只读原子：组装最终的大模型请求配置
  export const modelConfigAtom = atom((get) => ({
    temperature: get(tempAtom),
    top_p: get(topPAtom),
    isCreative: get(tempAtom) > 1.0 // 动态衍生计算
  }));
  ```

---

### 核心代码片段（极简记法）

```javascript
import { atom, useAtom } from 'jotai';

// 1. 独立原子定义
export const temperatureAtom = atom(0.7);

// 2. 仅订阅该组件，调节时聊天界面其他组件绝不重渲染！
function TemperatureSlider() {
  const [temp, setTemp] = useAtom(temperatureAtom);
  return <input type="range" min="0" max="2" step="0.1" value={temp} onChange={e => setTemp(+e.target.value)} />;
}
```

---

### 面试加分项

- **Atom-with-Storage 自动持久化**：Jotai 提供 `atomWithStorage` 工具，只需一行代码即可将该原子自动与 `localStorage` 同步，用户重新打开页面自动还原模型调参记录。""",
        "followups": """## 追问 1：在 Jotai 中，如果需要重置所有调参原子为默认值，如何优雅设计？

**回答要点**：
使用 `atom(null, (get, set) => ...)` 创建一个只写（Write-only）原子，在其更新函数内部集中调用 `set(tempAtom, 0.7)`、`set(topPAtom, 0.9)`，外部一键调用即可全量重置。

---

## 追问 2：Jotai 与 React 18 并发特性的兼容性如何？

**回答要点**：
Jotai v2 深度基于 React 原生的 `useSyncExternalStore` 构建，完全原生兼容 React 18 并发模式与时间切片，杜绝任何 Tear（UI 撕裂）现象。"""
    },
    {
        "id": "fe-ai-030",
        "title": "设计状态持久化方案自动保存至IndexedDB并支持跨标签页同步",
        "difficulty": "medium",
        "question": "设计一个“状态持久化”方案，将AI应用的关键状态自动保存至IndexedDB，并支持跨标签页同步。",
        "answer": """### 一句话总结

该方案采用**“IndexedDB 异步存储 + BroadcastChannel API 跨标签页总线 + 内存状态响应式同步”**。本标签页内状态变动经防抖后写入 IndexedDB；同时向 `BroadcastChannel` 广播事件（如 `SESSION_UPDATED`）；其他打开的标签页监听到广播后增量拉取最新数据同步到自身内存 Store，实现多 Tab 瞬间一致。

---

### 详细回答

#### 1. 跨标签页通信选型：为什么是 BroadcastChannel？
- **`window.addEventListener('storage')`**：只能监听 `localStorage`，但无法监听 IndexedDB 的写入；
- **SharedWorker**：兼容性稍复杂且调试成本高；
- **`BroadcastChannel`**：现代浏览器原生支持的同源跨 Tab 通信协议，API 极简，吞吐性能极佳。

#### 2. 防抖持久化与广播流程
1. 用户在 Tab A 收到流式 Token；
2. 节流写入 IndexedDB；
3. 完成时，Tab A 发送广播：`channel.postMessage({ type: 'SYNC_MSG', sessionId, newContent })`；
4. Tab B 监听收到消息，局部更新当前页面的 Store，无需重新刷新页面。

---

### 核心代码片段（极简记法）

```javascript
const channel = new BroadcastChannel('ai_tab_sync');

// 1. 发起更新端（Tab A）
function notifyOtherTabs(sessionId, updateData) {
  channel.postMessage({ type: 'UPDATE', sessionId, updateData });
}

// 2. 接收同步端（Tab B）
channel.onmessage = (event) => {
  const { type, sessionId, updateData } = event.data;
  if (type === 'UPDATE') {
    useChatStore.getState().applyRemoteUpdate(sessionId, updateData);
  }
};
```

---

### 面试加分项

- **Web Locks 互斥锁（避免写入冲突）**：当两个标签页同时在同一个会话中提问时，使用 `navigator.locks.request('session_lock_' + id, async () => { ... })` 确保对 IndexedDB 写入操作的互斥排他性，防止脏数据覆盖。""",
        "followups": """## 追问 1：如果某个标签页处于后台冻结（Frozen）状态，能收到 BroadcastChannel 消息吗？

**回答要点**：
处于冻结状态的页面会暂停 JS 执行，无法即时响应事件。但一旦用户点击激活该标签页，事件会被立即清空回放；且最佳实践是在页面触发 `visibilitychange` 变为 `visible` 时，主动从 IndexedDB 进行一次兜底增量查询。

---

## 追问 2：用户在无痕模式（Incognito）下，IndexedDB 怎么表现？

**回答要点**：
无痕模式下 IndexedDB 完全可用，但它只保存在临时内存会话中；当用户关闭无痕窗口时，所有数据会被系统物理清除。"""
    },
    {
        "id": "fe-ai-031",
        "title": "在万条级别的AI对话历史中，如何实现毫秒级搜索与过滤？",
        "difficulty": "hard",
        "question": "在万条级别的AI对话历史中，如何实现毫秒级搜索与过滤（关键词、时间范围、模型类型）？",
        "answer": """### 一句话总结

万条级前端搜索的核心是**“前端轻量倒排索引（Inverted Index，如 FlexSearch / MiniSearch） + Web Worker 离线建立 + 虚拟滚动展示”**。利用分词算法在后台线程预先构建倒排索引字典，关键词检索由 $O(N)$ 遍历降至 $O(1)$ 查找，结合位运算复合过滤，在 10 毫秒内完成万级文本匹配。

---

### 详细回答

#### 1. 为什么原生的 `array.filter(m => m.includes(kw))` 会卡死？
- 10,000 条长文本对话包含数百万字符；
- 用户在搜索框每敲一个字都执行一次全量字符串正则匹配，主线程瞬间卡死几百毫秒，输入严重掉帧。

#### 2. 倒排索引构建架构
- **分词（Tokenization）**：对消息正文分词（英文分词空格，中文结合 N-gram 算法切分为二字词元）；
- **字典构建**：建立 `Map<Term, Set<MessageId>>`；
- **交集计算**：当搜索“React 性能优化”时，分别查出 `React` 和 `性能优化` 的 ID 集合，执行 Set 交集操作即可毫秒级锁定目标。

---

### 核心代码片段（极简记法）

```javascript
import MiniSearch from 'minisearch';

// 1. 初始化全文索引
const miniSearch = new MiniSearch({
  fields: ['content'], // 检索字段
  storeFields: ['id', 'role', 'timestamp']
});

// 2. 批量建索引（移入 Web Worker 执行更佳）
miniSearch.addAll(allMessages);

// 3. 毫秒级搜索
const results = miniSearch.search('流式渲染', {
  filter: (item) => item.timestamp >= startTime // 支持复合过滤
});
```

---

### 面试加分项

- **搜索高亮零回流实现**：匹配到关键词后，使用浏览器原生的 **CSS Custom Highlight API**（`CSS.highlights.set()`）进行高亮，完全无需改动任何 DOM 节点结构，彻底消除因内嵌 `<mark>` 标签导致的频繁重排。""",
        "followups": """## 追问 1：新生成的流式消息，如何实时动态同步加入索引？

**回答要点**：
在流式生成期间不触发索引构建；等收到 `[DONE]` 结束标记后，调用 `miniSearch.add(finishedMessage)` 将该条完整消息单条追加到索引树中，增量开销几乎为 0。

---

## 追问 2：中文分词在前端纯 JS 环境下怎么轻量化解决？

**回答要点**：
无需引入几十 MB 的结巴分词字典。前端可采用轻量高效的 **2-Gram（双字滑动切分）** 或浏览器原生的 `Intl.Segmenter` API（现代浏览器原生支持多语言精准分词），零体积且极快。"""
    },
    {
        "id": "fe-ai-032",
        "title": "请设计一个用于超长AI生成内容的虚拟化渲染方案",
        "difficulty": "hard",
        "question": "请设计一个“虚拟化渲染”方案，用于超长AI生成内容（如数万Token的文档）的平滑滚动与快速定位。",
        "answer": """### 一句话总结

超长 AI 内容渲染的核心是**“动态高度虚拟列表（Dynamic Height Virtualization） + Markdown 块级预估缓存”**。将大文档按段落、代码块拆分为独立 Block，仅渲染可视视口及上下缓冲区内的 DOM 节点；利用 **`ResizeObserver` 动态测量真实高度更新索引偏移树**，并在流式追加时实时维持滚动锚定。

---

### 详细回答

#### 1. 为什么不能用固定高度虚拟列表？
- AI 生成的 Markdown 段落高度完全未知（短则一行标题，长则几百行代码块）；
- 必须支持**动态高度测量与预估（Estimated Height）**。

#### 2. 核心算法机制
1. **预估占位（Spacer）**：初始化时赋予每个块默认高度（如 60px），计算总容器虚拟高度；
2. **可视窗口计算**：根据滚动条的 `scrollTop`，通过二分查找计算出当前视口应该展示的起始索引 `startIndex` 和结束索引 `endIndex`；
3. **真实测量（Measure）**：节点渲染后，通过 `ResizeObserver` 采集实际 DOM 高度，修正高度字典并累加更新后续节点的位移 `offset`。

---

### 核心代码片段（极简记法）

```javascript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualAIDocument({ blocks, parentRef }) {
  const virtualizer = useVirtualizer({
    count: blocks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // 初始预估高度
    overscan: 3 // 上下多预加载 3 个块防白屏
  });

  return (
    <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
      {virtualizer.getVirtualItems().map((item) => (
        <div key={item.key} style={{ position: 'absolute', top: 0, transform: `translateY(${item.start}px)` }}>
          <MarkdownBlock content={blocks[item.index]} />
        </div>
      ))}
    </div>
  );
}
```

---

### 面试加分项

- **流式追加时的滚动锚定（Scroll Anchoring）**：在文档末尾持续吐字时，高度不断剧烈变化。必须在每次高度变动时配合 `scrollBy` 或 CSS `overflow-anchor: auto`，防止视口被新增内容顶飞。""",
        "followups": """## 追问 1：超长内容快速拖拽滚动条到底部时出现短暂白屏，如何缓解？

**回答要点**：
1. **适当调大预渲染缓冲区（overscan: 5~10）**；
2. **轻量骨架占位**：当检测到滚动速度超过阈值（快速飞滑）时，视口内新节点直接渲染灰度骨架矩形，停止昂贵的 Markdown/代码高亮解析，滑动停下后再执行真实解析。

---

## 追问 2：虚拟列表中如何实现全文查找（Ctrl + F）？

**回答要点**：
浏览器原生 Ctrl+F 无法检索视口外未挂载的 DOM。
必须自研页面内搜索框：检索内存中的完整数据，匹配到结果后调用虚拟列表的 `virtualizer.scrollToIndex(targetIndex)` 强制将该节点滚入视口渲染。"""
    },
    {
        "id": "fe-ai-033",
        "title": "如何用WebGL或Canvas实现AI生成图像的高性能实时预览？",
        "difficulty": "medium",
        "question": "如何用WebGL或Canvas实现AI生成图像的高性能实时预览（如缩放、拖拽、滤镜）？",
        "answer": """### 一句话总结

采用 **WebGL 着色器管线（Shader Pipeline）或双缓冲 Canvas 渲染**。将 AI 生成的大分辨率图像上传为 GPU 纹理（Texture）；缩放、平移与色彩滤镜（如色温、降噪、增强）完全由 **GPU 片元着色器（Fragment Shader）并发计算**，避免 CPU 逐像素循环修改像素点造成的卡死，稳定保持 60fps。

---

### 详细回答

#### 1. 为什么不用普通 DOM 变换（`<img>` + CSS transform）？
- CSS transform 仅能支持基础平移缩放；
- 当需要对 AI 图像做局部修复擦除（Inpainting）、涂抹蒙版（Mask）、直方图调整或流式生成过程的扩散步数（Diffusion Steps）过渡动画时，DOM 无能为力。

#### 2. Canvas 2D 逐像素计算的死穴
- 使用 `ctx.getImageData()` 修改像素阵列，对 4K 图像需要操作数千万个数组元素，纯 CPU 运算单帧耗时几百毫秒。

#### 3. WebGL 架构解法
- **GPU 纹理绑定**：单次将图像像素上传到 GPU 显存；
- **片元着色器处理滤镜**：在 GPU 中并发运行 GLSL 代码；
- **矩阵变换（Matrix Transform）**：平移和缩放只计算 3x3 矩阵相乘，单帧仅需 1~2 毫秒。

---

### 核心代码片段（极简记法）

```javascript
// WebGL 片元着色器调整对比度与曝光（GPU 并行计算）
const fragmentShaderSource = `
  precision mediump float;
  uniform sampler2D u_image;
  uniform float u_brightness;
  varying vec2 v_texCoord;

  void main() {
    vec4 color = texture2D(u_image, v_texCoord);
    gl_FragColor = vec4(color.rgb * u_brightness, color.a);
  }
`;
```

---

### 面试加分项

- **OffscreenCanvas（离屏渲染与 Worker）**：将 Canvas 控制权通过 `canvas.transferControlToOffscreen()` 转移给 Web Worker，在独立线程中执行图像加载与渲染，彻底消除主线程阻塞。""",
        "followups": """## 追问 1：用户频繁快速拖拽缩放时，如何避免创建大量临时对象导致 GC 卡顿？

**回答要点**：
对象复用与TypedArray内存池：变换矩阵始终复用同一个 `Float32Array(9)` 实例，仅就地（In-place）修改其数值，绝不每帧 `new` 数组或对象。

---

## 追问 2：对于超大分辨率（如 8K 扩散模型原图），手机端 WebGL 纹理超限怎么办？

**回答要点**：
检查 `gl.getParameter(gl.MAX_TEXTURE_SIZE)`（通常为 4096 或 8192）。超出上限时，采用类似地图瓦片（Tiles）技术，将大图切为多个子块纹理分别加载与局部拼贴渲染。"""
    },
    {
        "id": "fe-ai-034",
        "title": "在AI代码编辑器中，如何优化语法高亮与错误波浪线的渲染性能？",
        "difficulty": "hard",
        "question": "在AI代码编辑器中，如何优化语法高亮、代码折叠、错误波浪线的渲染性能，避免输入卡顿？",
        "answer": """### 一句话总结

优化代码编辑器的核心是**“分层渲染（Layered Architecture） + AST 解析移入 Web Worker + 视口行级虚拟化”**。语法解析与 Linter 检查在后台 Worker 中异步执行，主线程仅按当前视口视行范围更新 DOM；将光标、文本、背景高亮和错误下划线分层独立渲染，避免单字输入引发全量重绘。

---

### 详细回答

#### 1. 痛点：Monaco / CodeMirror 为何会卡？
- 代码编辑器若每敲一个字都同步触发一次完整词法分析（Lexer）和语法树重构，当文件超过几千行时耗时达几十毫秒，导致输入延迟。

#### 2. 三大核心优化手段
1. **后台 Worker 异步高亮（Tree-sitter / TextMate）**：
   词法解析全部在子线程跑完，将结果简化为 Token 数组：`[{ line: 12, start: 4, end: 10, class: 'keyword' }]`，主线程仅做样式类名套用；
2. **行级虚拟渲染（Line Virtualization）**：
   即使文件有一万行，当前屏幕也仅渲染可视的 40~50 个 `div.line` 节点；
3. **分层绘制（Layered Canvas/DOM）**：
   - 文本层、语法高亮层、波浪线下划线层分离；
   - 错误波浪线利用纯 CSS `text-decoration` 配合 SVG 纹理绘制，杜绝手动计算绝对定位小图片。

---

### 核心代码片段（极简记法）

```javascript
// 错误波浪线纯 CSS 高性能绘制
const wavyUnderlineStyle = `
  text-decoration: underline wavy #ff4d4f;
  text-decoration-skip-ink: none; /* 避免文字字切断波浪线 */
`;
```

---

### 面试加分项

- **增量词法分析（Incremental Parsing）**：使用 Tree-sitter 等支持增量更新的解析器。用户在第 50 行输入一个字符，只重新解析受影响的局部 AST 节点，复用其余 99% 的旧语法树。""",
        "followups": """## 追问 1：AI 流式生成代码时，代码块如果一直动态增加行数，代码折叠（Code Folding）状态怎么维持？

**回答要点**：
生成期间禁用昂贵的折叠状态计算；或者仅在检测到大括号闭合 `}` 时，增量计算该折叠区间的起始行。生成结束后统一触发一次完整的折叠索引更新。

---

## 追问 2：VS Code Web版底层针对大文件输入性能是怎么优化的？

**回答要点**：
底层使用 **Piece Table（分块表）** 数据结构存储文本缓冲区。插入和删除只需修改指针节点，时间复杂度为 $O(1)$，无需对整个大字符串进行任何内存拼接移动。"""
    },
    {
        "id": "fe-ai-035",
        "title": "设计按需加载策略仅渲染AI消息可视区域，其余保留为纯文本",
        "difficulty": "medium",
        "question": "设计一个“按需加载”策略，仅渲染AI对话列表中可视区域及附近的消息，其余部分保留为纯文本。",
        "answer": """### 一句话总结

该策略属于**“富渲染与轻渲染按需降级（Content Degradation）”**。处于视口内的消息挂载完整的 React 富组件（富文本 Markdown、可编辑代码块、Mermaid 架构图、KaTeX 数学公式）；一旦滚动离开视口，自动卸载重组件并降级为**带有固定高度骨架的轻量纯文本（Plain Text）**，释放 80% 的内存与 DOM 节点。

---

### 详细回答

#### 1. 为什么全量渲染富组件会导致页面崩溃？
- Mermaid.js 图表、ECharts 实例、KaTeX 渲染树会生成成千上万个嵌套 SVG 和 DOM 节点；
- 对话进行到 50 轮时，页面 DOM 节点数突破数万个，滚动极度卡顿，内存占用达数 GB。

#### 2. IntersectionObserver 动态降级设计
- 每个消息卡片外层包裹探测器：
  ```javascript
  const { ref, inView } = useInView({ rootMargin: '200px 0px' });
  ```
- **在视口内（`inView: true`）**：渲染 `<FullRichMarkdown message={msg} />`；
- **离开视口（`inView: false`）**：
  - 记录脱离前的真实 DOM 高度（防止高度塌陷导致滚动条跳动）；
  - 替换渲染为 `<div style={{ height: recordedHeight }}>{msg.plainTextSummary}</div>`。

---

### 核心代码片段（极简记法）

```javascript
function AdaptiveMessageItem({ message }) {
  const [isInView, setIsInView] = useState(false);
  const [cachedHeight, setCachedHeight] = useState(null);
  const domRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIsInView(entry.isIntersecting);
      if (entry.isIntersecting) {
        setCachedHeight(domRef.current.offsetHeight); // 记录真实高度
      }
    }, { rootMargin: '300px' });

    observer.observe(domRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={domRef} style={{ minHeight: cachedHeight ? `${cachedHeight}px` : 'auto' }}>
      {isInView ? <HeavyMarkdownAST content={message.text} /> : <div className="plain-preview">{message.text.slice(0, 100)}...</div>}
    </div>
  );
}
```

---

### 面试加分项

- **结合 `content-visibility: auto`**：现代 Chrome 原生支持的单行 CSS 魔法：
  `content-visibility: auto; contain-intrinsic-size: 0 120px;`
  浏览器会在屏幕外自动跳过该元素的渲染与样式计算，效果与 JS 降级类似且性能更高。""",
        "followups": """## 追问 1：降级为纯文本后，如果用户在这个时候用浏览器的 Ctrl+F 搜索，还能搜到吗？

**回答要点**：
能搜到！因为轻量纯文本依然在 DOM 树中保留了可读字符；而如果完全用 `display: none` 抹除，则无法被原生搜索匹配。

---

## 追问 2：重新滚入视口时，复杂的图表组件重新初始化会不会有瞬间闪烁？

**回答要点**：
通过预先将图表转换为静态 WebP / SVG 图片快照进行占位；滚入视口先展示图片快照，当用户鼠标 hover 或点击时再激活为可交互的活组件。"""
    },
    {
        "id": "fe-ai-036",
        "title": "如何用WASM加速前端本地AI推理并与JavaScript无缝交互？",
        "difficulty": "hard",
        "question": "如何用WASM加速前端本地的AI推理（如句子嵌入、相似度计算），并实现与JavaScript的无缝交互？",
        "answer": """### 一句话总结

利用 **WebAssembly（WASM，结合 SIMD 多指令与多线程支持）** 将 C++/Rust 编译的推理引擎（如 ONNX Runtime Web / Transformers.js）运行在浏览器端。通过 **`WebAssembly.Memory` 共享线性内存**，避免在 JS 与 WASM 边界频繁深拷贝庞大的浮点数 Embedding 向量，实现单次向量余弦相似度计算仅耗时微秒级。

---

### 详细回答

#### 1. 为什么纯 JavaScript 做向量计算不够快？
- 向量通常是 512 或 1536 维度的 `Float32Array`；
- 纯 JS 执行向量点积和范数计算无法有效利用 CPU 的 SIMD 硬件级并行指令集，单次匹配几千个向量需耗时上百毫秒。

#### 2. WASM SIMD 硬件加速
- WebAssembly SIMD（单指令多数据流）允许**单条 CPU 指令并行处理 4 个 32 位浮点数**运算，吞吐量理论提升 4 倍以上。

#### 3. 规避 JS/WASM 跨语言通信开销（零拷贝）
- 严禁在调用 WASM 函数时传递普通 JS 对象；
- **正确做法**：JS 直接向 WASM 的共享线性内存地址空间（Linear Memory）中写入向量二进制内存切片，传递内存指针和长度，WASM 计算完就地写回，彻底杜绝数据序列化损耗。

---

### 核心代码片段（极简记法）

```javascript
// 零拷贝传入 Embedding 向量
const memory = wasmInstance.exports.memory;
const wasmBuffer = new Float32Array(memory.buffer, pointer, vectorLength);
wasmBuffer.set(jsFloat32Embedding); // 内存直接拷贝

// 调用 WASM 导出函数执行 SIMD 快速余弦计算
const similarityScore = wasmInstance.exports.cosineSimilarity(pointerA, pointerB, vectorLength);
```

---

### 面试加分项

- **WebGPU 演进路线**：指出对于超大矩阵乘法（LLM 逐 Token 解码），WebGPU 比 WASM 还要快 10~50 倍；当前端硬件支持 WebGPU 时优先走 GPU 着色器，不支持时降级走 WASM + SIMD。""",
        "followups": """## 追问 1：前端如何判断当前浏览器是否支持 WASM SIMD？

**回答要点**：
基于特性探测：尝试编译一段最小的包含 SIMD 字节码的操作片段 `WebAssembly.validate(simdBytes)`；若返回 `true` 则动态加载 SIMD 优化包，否则加载纯通用回退 WASM 包。

---

## 追问 2：WASM 模块体积通常较大（几 MB），如何优化加载白屏？

**回答要点**：
1. 开启 Brotli / Gzip 压缩；
2. 利用 `WebAssembly.instantiateStreaming` 边下载边编译，跳过等待完整下载后再编译的串行延迟；
3. 将 WASM 模块编译产物缓存至 IndexedDB 中。"""
    },
    {
        "id": "fe-ai-037",
        "title": "在AI实时语音场景中，如何用Web Audio API优化音频流处理？",
        "difficulty": "hard",
        "question": "在AI实时语音转文字场景中，如何用Web Audio API优化音频流处理，降低内存与CPU占用？",
        "answer": """### 一句话总结

实时语音采样的核心是**“用 `AudioWorklet` 取代已废弃的 `ScriptProcessorNode`”**。在独立的音频渲染线程中采集麦克风 PCM 原始流，完成**降采样（如 48kHz 转 16kHz）、单声道转换与 VAD 静音切除**；仅在检测到有效人声时通过二进制 WebSocket 发往后端模型，大幅节省网络与前端 CPU 占用。

---

### 详细回答

#### 1. 为什么严禁使用 ScriptProcessorNode？
- `ScriptProcessorNode` 在主线程执行音频回调，若主线程有复杂 DOM 重绘或 JS 计算，音频回调会被阻塞导致**破音、音频数据丢帧（Audio Glitch）**；
- 现代 W3C 标准已强制由 `AudioWorklet` 替代。

#### 2. AudioWorklet 独立音频线程优势
- 运行在与 UI 完全隔离的高优先级音频线程中，延迟低至几毫秒，不受主线程渲染和卡顿影响；
- 内部处理 128 采样点帧切片。

#### 3. 前端 VAD（语音活动检测，Voice Activity Detection）
- 若麦克风一直开启，无声环境也会持续产生大量的音频数据包发往服务端计费；
- 前端计算短时能量和零交叉率，未说话期间不发包，检测到人声瞬间启动推流。

---

### 核心代码片段（极简记法）

```javascript
// 注册并连接 AudioWorklet
const audioContext = new AudioContext({ sampleRate: 16000 });
await audioContext.audioWorklet.addModule('pcm-processor.js');

const source = audioContext.createMediaStreamSource(micStream);
const workletNode = new AudioWorkletNode(audioContext, 'pcm-processor');

// 接收来自独立音频线程转换好的 16kHz PCM 数据
workletNode.port.onmessage = (e) => {
  const pcmChunk = e.data; // ArrayBuffer
  websocket.send(pcmChunk);
};

source.connect(workletNode);
```

---

### 面试加分项

- **移动端用户手势激活限制**：指出 `AudioContext` 必须在用户直接触发的事件（如 `onClick`）中调用 `audioContext.resume()` 解冻，否则在 iOS Safari 上会被浏览器直接挂起处于 `suspended` 状态无法录音。""",
        "followups": """## 追问 1：前端如何实现麦克风回声消除（AEC）与降噪？

**回答要点**：
无需在 JS 手写算法！
在调用 `navigator.mediaDevices.getUserMedia()` 时，直接传入底层浏览器硬件级约束：
`{ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } }` 即可开启内置硬件回声抑制。

---

## 追问 2：AudioWorklet 线程与主线程之间如何高效传输音频二进制数据？

**回答要点**：
使用 `port.postMessage(pcmBuffer, [pcmBuffer.buffer])`，利用 **Transferable Objects** 将底层的 ArrayBuffer 所有权直接转移给主线程，实现真正的零拷贝内存交换。"""
    },
    {
        "id": "fe-ai-038",
        "title": "请设计一个渲染优先级调度器，确保AI生成中关键UI响应迅速",
        "difficulty": "hard",
        "question": "请设计一个“渲染优先级”调度器，确保AI生成中的关键UI（如输入框、发送按钮）始终响应迅速？",
        "answer": """### 一句话总结

调度器核心基于 **“浏览器原生 `scheduler.postTask` API 或宏微任务切片分级队列”**。将 UI 任务划分为 **`user-blocking`（最高优：点击打字即时响应）**、**`user-visible`（次高优：输入框光标）** 与 **`background`（最低优：大段流式 Markdown 格式化）**；利用时间切片在每帧空闲时执行低优先级任务，一旦有用户交互到达立即让出主线程。

---

### 详细回答

#### 1. 优先级三级划分模型
- **Immediate（不可中断）**：输入框 onChange、点击“停止生成”按钮、弹窗关闭；
- **Normal（平滑渲染）**：当前正在输入的纯字符渲染；
- **Background（延后计算）**：代码语法高亮计算、KaTeX 数学公式渲染、历史消息自动持久化存储。

#### 2. 原生 Scheduler API 驱动
```javascript
// 最高优先级（立即抢占执行）
scheduler.postTask(urgentTask, { priority: 'user-blocking' });

// 最低优先级（闲时执行）
scheduler.postTask(heavyHighlightTask, { priority: 'background' });
```

#### 3. 降级兼容机制：MessageChannel + requestIdleCallback
- 不支持原生 scheduler 的浏览器，使用 `MessageChannel` 模拟宏任务调度，结合 `performance.now()` 计算单帧已用时间，若耗时超过 5ms 主动 `yield` 让出控制权。

---

### 核心代码片段（极简记法）

```javascript
class RenderScheduler {
  scheduleHeavyTask(taskFn) {
    if ('scheduler' in window) {
      return window.scheduler.postTask(taskFn, { priority: 'background' });
    }
    // 降级使用 requestIdleCallback
    return new Promise(resolve => {
      requestIdleCallback(deadline => {
        resolve(taskFn());
      });
    });
  }
}
```

---

### 面试加分项

- **`scheduler.yield()` 现代时间切片 API**：Chrome 129+ 推出的全新标准，允许长任务内部像写普通代码一样 `await scheduler.yield()`，优雅暂停并让出主线程给点击事件插队，之后再自动恢复执行。""",
        "followups": """## 追问 1：为什么用 MessageChannel 实现宏任务切片，而不是 setTimeout(fn, 0)？

**回答要点**：
因为浏览器对 `setTimeout` 在嵌套超过 5 层时会强制施加 **4ms 的最小延迟限制**；而 `MessageChannel` 没有任何人造延迟，紧随当前事件循环微任务之后立即触发，执行效率高出数倍。

---

## 追问 2：如果 background 队列积压了太多的流式任务，会不会造成饥饿（Starvation）永远得不到执行？

**回答要点**：
必须配置**老化提升（Aging）与超时强制执行时间戳（Expiration Time）**。当一个任务在后台队列等待超过阈值（如 500ms），将其优先级自动提升为最高，强制在本帧执行，防止数据永久陈旧。"""
    },
    {
        "id": "fe-ai-039",
        "title": "如何用React.memo与useCallback避免AI消息列表全量重渲染？",
        "difficulty": "medium",
        "question": "如何用React.memo、useMemo、useCallback避免AI消息列表因无关状态变更导致的全量重渲染？",
        "answer": """### 一句话总结

核心在于**“稳定引用传参 + 细粒度更新隔离 + 自定义 memo 比对器”**。将消息项提取为独立子组件并用 `React.memo` 包裹，自定义对比仅当自身 `content` 或 `status` 变更时才重刷；所有透传给子组件的事件回调（如“重新生成”、“复制”）必须通过 `useCallback` 稳定函数引用，避免父组件每收到一个 Token 都让全量历史卡片做无谓的虚拟 DOM Diff。

---

### 详细回答

#### 1. 为什么普通的 React.memo 经常失效？
- **内联匿名函数破坏引用**：父组件写了 `<MessageItem onCopy={() => copy(m.id)} />`，父组件每渲染一次都会创建一个新函数对象，`React.memo` 浅比较判定 props 发生变化，全量重刷！
- **传递了冗余的父组件状态**：把整个大对象甚至 `streamingId` 传下去。

#### 2. 标准规范写法
1. **稳定事件回调**：使用 `useCallback` 包裹，配合参数传递或者将状态移入状态库；
2. **精准对比（arePropsEqual）**：
   ```javascript
   const MessageItem = React.memo(MessageItemComponent, (prev, next) => {
     return prev.message.id === next.message.id &&
            prev.message.content === next.message.content &&
            prev.message.status === next.message.status;
   });
   ```

---

### 核心代码片段（极简记法）

```javascript
// 1. 纯净子组件并锁定比对
const MessageItem = React.memo(({ id, content, onRegenerate }) => {
  return (
    <div>
      <Markdown>{content}</Markdown>
      <button onClick={() => onRegenerate(id)}>重试</button>
    </div>
  );
});

// 2. 父组件保证回调不变
function ChatList({ messages }) {
  const handleRegenerate = useCallback((id) => {
    retryMessage(id);
  }, []); // 依赖项为空，引用永久稳定

  return messages.map(msg => (
    <MessageItem key={msg.id} id={msg.id} content={msg.content} onRegenerate={handleRegenerate} />
  ));
}
```

---

### 面试加分项

- **useEvent 提案模式**：对于回调内部需要读取动态状态又想保持函数引用不变的场景，使用 `useEvent`（或通过 `useRef` 保存回调本体），彻底解除 useCallback 必须配置一堆依赖项的烦恼。""",
        "followups": """## 追问 1：React.memo 的自定义比较函数如果写得特别深、特别复杂，会不会反而降低性能？

**回答要点**：
会！
如果比较函数内部做了耗时的多层深度递归对比，比对的时间甚至可能超过 React 直接重新渲染虚拟 DOM 的开销。因此比较逻辑必须是 $O(1)$ 的简单关键字段浅比较。

---

## 追问 2：为什么列表的 key 一定不能传数组的 index？

**回答要点**：
如果用 index 作为 key，当新消息被插入或者历史消息被删除时，所有后续组件的 index 都会错位，导致 React 误以为节点没变而复用错误的内部状态（如输入框未保存的草稿），且无法命中 `React.memo` 优化。"""
    },
    {
        "id": "fe-ai-040",
        "title": "在AI多模态输出（文本+图像+表格）场景中，如何分阶段渲染提升首屏速度？",
        "difficulty": "medium",
        "question": "在AI多模态输出（文本+图像+表格）场景中，如何分阶段渲染以提升首屏速度？",
        "answer": """### 一句话总结

多模态分阶段渲染采用**“渐进式流水线（Progressive Pipeline）”**。第一阶段（0ms）立即吐出**流式纯文本骨架**满足用户即时可读；第二阶段渲染**轻量表格与数据预览**；第三阶段（延迟异步加载）以**低分辨率占位图（LQIP）+ 异步 Web Worker 解析重图表**，避免资源集中竞争阻塞首屏呈现。

---

### 详细回答

#### 1. 核心瓶颈：为什么多模态会拖垮首屏？
- 生成的图片动辄数 MB，表格和复杂渲染引擎（如 ECharts）脚本体积庞大；
- 若必须等所有模态就绪后一次性全量挂载，用户会面对长达 5~8 秒的白屏或卡顿。

#### 2. 三阶段渲染流水线
- **阶段 1：首字文本秒出（TTFT）**：
  纯文本渲染成本极低，优先通过流式展示结论摘要；
- **阶段 2：交互结构化数据（表格与代码）**：
  收到数据先用极简原生 HTML `<table>` 快速呈现，后续空闲时再注水（Hydrate）为支持排序过滤的高级表格组件；
- **阶段 3：重资源异步加载（图片与图表）**：
  - 图片先渲染带模糊滤镜的 Low-Quality 占位图或骨架图；
  - 图表采用动态 `import()` 懒加载核心图表库，首屏不打包多余第三方重体积脚本。

---

### 核心代码片段（极简记法）

```javascript
function MultiModalResponse({ data }) {
  return (
    <>
      {/* 阶段 1：纯文本即时渲染 */}
      <p>{data.summaryText}</p>

      {/* 阶段 2：表格按需挂载 */}
      {data.tableData && <SimpleTable data={data.tableData} />}

      {/* 阶段 3：图片懒加载 + 占位 */}
      {data.imageUrl && (
        <img 
          src={data.imageUrl} 
          loading="lazy" 
          placeholder="blur" 
          alt="AI Generated" 
        />
      )}
    </>
  );
}
```

---

### 面试加分项

- **预知宽高占位防 CLS（Cumulative Layout Shift）**：大模型生成图片时，在元数据中提前下发图片原始宽高比（如 `aspect_ratio: "16:9"`）。前端在图片未加载完成前通过 CSS `aspect-ratio` 预留出精准空白高度，彻底杜绝图片加载完毕时页面突然跳动的恶劣视觉抖动。""",
        "followups": """## 追问 1：表格包含数十万行数据时，分阶段渲染怎么处理？

**回答要点**：
首屏仅以纯文本形式渲染前 20 条预览行，并在下方展示“已截取前 20 条，点击下载完整 CSV”；若用户需要在前端浏览全量数据，再动态激活虚拟滚动表格组件。

---

## 追问 2：多个模态数据在同一个 SSE 流里推送，如何分优先级推送到前端？

**回答要点**：
服务端大模型编排层进行通道优先级分发：文本摘要走高优先级通道优先推完；图片生成耗时较长，由异步任务生成完成后通过二次事件（`event: image_ready`）补发给前端就地替换占位符。"""
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

print(f"Generated {len(DATA)} questions successfully (fe-ai-021 ~ fe-ai-040)!")
