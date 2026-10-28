### 一句话总结

设计 Agent 状态机类型时，采用**“带载荷的可辨识联合（Discriminated Union with Payloads）”**绑定每个状态特有的上下文数据，确保不存在的字段在编译期报错；并通过**“状态转移映射表（Transition Matrix）”结合泛型函数**，在类型系统层面强制拦截非法的状态跳跃。

---

### 详细回答

#### 1. 为什么不用传统单一 Object 声明状态？
- **传统劣势**：如果写 `interface AgentState { status: string; thought?: string; toolResult?: any; }`，所有字段全变成可选 `?`，组件渲染时处处需要判断 `toolResult !== undefined`，且无法从语法层面阻止 `idle` 状态携带 `toolResult` 的脏数据。
- **正解**：为每个生命周期阶段定义专属类型，各阶段只暴露该阶段合法的字段：
  ```typescript
  type AgentState =
    | { status: 'idle' }
    | { status: 'thinking'; thought: string }
    | { status: 'acting'; thought: string; toolName: string; toolArgs: Record<string, unknown> }
    | { status: 'observing'; observation: unknown }
    | { status: 'finished'; output: string }
    | { status: 'error'; error: Error };
  ```

#### 2. 类型级状态转移约束（Transition Map）
定义一个对象映射表，明确指定每个状态允许跃迁的目标状态：
```typescript
interface Transitions {
  idle: 'thinking';
  thinking: 'acting' | 'finished' | 'error';
  acting: 'observing' | 'error';
  observing: 'thinking' | 'finished' | 'error';
  finished: 'idle';
  error: 'idle';
}
```

#### 3. 泛型函数实现编译期转移校验
编写状态切换函数 `transition`，若传入的目标状态不在该状态的合法映射集合内，TypeScript 直接红线报错，杜绝业务代码中的非法跃迁。

---

### 核心代码片段（极简记法）

```typescript
// 1. 状态转移规则表
type ValidNextState<Current extends AgentState['status']> = {
  idle: 'thinking';
  thinking: 'acting' | 'finished' | 'error';
  acting: 'observing' | 'error';
  observing: 'thinking' | 'finished' | 'error';
  finished: 'idle';
  error: 'idle';
}[Current];

// 2. 类型安全的状态切换函数
function transition<
  Current extends AgentState, 
  NextStatus extends ValidNextState<Current['status']>
>(
  currentState: Current,
  nextState: Extract<AgentState, { status: NextStatus }>
): Extract<AgentState, { status: NextStatus }> {
  return nextState;
}
```

---

### 面试加分项

- **UI 穷尽性检查（Exhaustive Check）**：在组件内使用 switch-case 渲染不同状态卡片时，使用 `assertNever(state)` 确保后续新增状态（如 `awaiting_user_confirmation` 人机回环交互）时，编译器能立刻提示遗漏的 UI 分支。
