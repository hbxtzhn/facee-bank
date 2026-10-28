### 一句话总结

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

- **人机协同（Human-in-the-Loop）**：在敏感工具调用前插入 `waitingApproval` 状态，强依赖用户手动点击授权后才流转到执行。
