import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-ai-001",
        "title": "在定义AI接口返回的嵌套数据结构时，如何用TypeScript的泛型与条件类型实现灵活的类型推导？",
        "difficulty": "medium",
        "question": "在定义AI接口返回的嵌套数据结构（如多轮对话、工具调用结果）时，如何用TypeScript的泛型与条件类型实现灵活的类型推导？",
        "answer": """### 一句话总结

定义复杂动态的 AI 接口时，核心是采用**“可辨识联合类型（Discriminated Union）”作为基石**，通过固定的标识符（如 `type: 'text' | 'tool_call'`）让 TypeScript 实现自动类型收窄；结合**泛型映射表与条件类型**，根据具体的工具名（`tool_name`）动态推导对应的参数类型，避免使用任何 `any` 或宽泛的 `object`。

---

### 详细回答

#### 1. 为什么不能用可选字段（`?`）堆砌单个接口？
- **反例**：若定义 `interface Message { content?: string; tool_calls?: any[]; }`，在消费时 `msg.content` 永远是 `string | undefined`，必须处处写非空断言 `!` 或额外判空，且无法约束“文本消息绝不能有 tool_calls”这一互斥业务规则。
- **正解（可辨识联合）**：通过具有唯一标识字段（如 `type`）的独立接口联合：
  ```typescript
  type TextMessage = { type: 'text'; content: string };
  type ToolCallMessage<T extends string = string> = { type: 'tool_call'; tool: T; args: ToolArgs<T> };
  type AIMessage = TextMessage | ToolCallMessage;
  ```
  在 `if (msg.type === 'text')` 分支下，TS 会自动将 `msg` 收窄为 `TextMessage`，安全访问 `msg.content`。

#### 2. 工具调用的泛型映射与条件类型推导
- **建立工具注册表（Tool Registry）**：集中声明每个工具的入参 Schema：
  ```typescript
  interface ToolSchemaMap {
    search: { query: string; limit?: number };
    calculator: { expression: string };
  }
  ```
- **使用条件类型提取入参**：
  ```typescript
  type ToolArgs<T extends string> = T extends keyof ToolSchemaMap 
    ? ToolSchemaMap[T] 
    : Record<string, unknown>; // 兜底未知工具
  ```

#### 3. 流式 Chunk 增量类型的动态推导
- 流式返回的 delta 往往是完整结构的浅层可选子集，使用条件类型和映射修饰符实现：
  ```typescript
  type StreamDelta<T> = T extends object ? { [K in keyof T]?: StreamDelta<T[K]> } : T;
  ```

---

### 核心代码片段（极简记法）

```typescript
// 1. 工具类型字典
interface ToolRegistry {
  web_search: { query: string };
  code_runner: { code: string; language: 'js' | 'python' };
}

// 2. 可辨识联合类型（Discriminated Union）
type AIMessage = 
  | { type: 'text'; content: string }
  | { [K in keyof ToolRegistry]: { type: 'tool'; name: K; args: ToolRegistry[K] } }[keyof ToolRegistry];

// 3. 消费时自动精准类型收窄
function handleMessage(msg: AIMessage) {
  if (msg.type === 'text') {
    console.log(msg.content.toUpperCase()); // 安全推导为 string
  } else if (msg.name === 'web_search') {
    console.log(msg.args.query); // 自动推导出 { query: string }
  }
}
```

---

### 面试加分项

- **Zod 运行时校验与类型同步**：在真实项目中，大模型返回的 JSON 参数是不可信的字符串。通常用 `zod` 定义工具入参 Schema，利用 `z.infer<typeof schema>` 自动生成 TS 类型，兼顾**静态类型安全**与**运行时异常拦截**。
- **模板字面量约束**：可用模板字面量类型约束模型标识符（如 `type ModelName = \`gpt-${'4o' | '4-turbo'}\` | \`claude-3-5-${'sonnet' | 'haiku'}\``），提高静态拼写防护。""",
        "followups": """## 追问 1：大模型生成的工具参数经常是序列化的 JSON 字符串，TS 如何优雅地保证解析后类型安全？

**回答要点**：
大模型输出的 `args` 往往是字符串。不要直接 `JSON.parse(rawArgs) as ExpectedType`（类型断言容易掩盖运行时解析崩溃）。
标准做法是结合运行时验证库（如 `Zod` 或 `Valibot`），通过 `schema.safeParse(JSON.parse(rawArgs))` 进行校验，失败时捕获详细报错并作为错误反馈重新喂给大模型重试。

---

## 追问 2：如果模型版本动态更新，新增了前端未知的工具类型，如何保证类型系统不直接崩溃？

**回答要点**：
在可辨识联合类型中保留一个兜底分支（Fallback Branch）：
`| { type: 'unknown_tool'; name: string; args: unknown }`，并在 switch-case 语句中使用 `default` 分支进行兜底渲染（如显示“暂不支持该组件渲染，请更新客户端”），确保向前兼容。"""
    },
    {
        "id": "fe-ai-002",
        "title": "当AI接口返回字段因模型版本不同动态变化时，如何设计类型守卫与类型收缩？",
        "difficulty": "medium",
        "question": "当AI接口返回的字段可能因模型版本不同而动态变化时，如何设计类型守卫（type guard）与类型收缩策略？",
        "answer": """### 一句话总结

应对模型版本差异带来的字段动态变化，核心采用**“自定义谓词守卫（is 语法）+ in 关键字特征探测”**收缩静态类型，结合 **Zod / Valibot 运行时 Schema 校验与适配器（Adapter）模式**，将异构响应在数据入口层标准化转换为前端统一的领域实体。

---

### 详细回答

#### 1. 为什么不能只用简单的 `as` 类型断言？
- **痛点**：若写 `res as GPT4Response`，TS 编译器会直接放行，但若运行时接口切换为 Claude 或返回了新字段，读取未定义属性会导致线上页面直接抛出 `TypeError: Cannot read properties of undefined`。
- **正解**：通过自定义类型守卫函数（Type Guard）在运行时进行字段特征探测，同时让 TS 编译器收窄类型。

#### 2. 自定义类型守卫实现（is 语法）
- 使用 `val is Type` 谓词函数：
  ```typescript
  function isToolCallResponse(res: unknown): res is ToolCallResponse {
    return typeof res === 'object' && res !== null && 'tool_calls' in res;
  }
  ```
- 在业务代码中通过 `if (isToolCallResponse(data))` 即可自动收缩，安全访问 `data.tool_calls`。

#### 3. 适配器模式（Adapter Pattern）统一模型差异
- 对外统一输出 `StandardMessage` 格式；
- 编写适配层：
  ```typescript
  function normalizeAIResponse(raw: unknown): StandardMessage {
    if (isClaudeResponse(raw)) return { text: raw.content[0].text, tokens: raw.usage.output_tokens };
    if (isOpenAIResponse(raw)) return { text: raw.choices[0].message.content, tokens: raw.usage.completion_tokens };
    throw new Error('Unsupported AI model response format');
  }
  ```

---

### 核心代码片段（极简记法）

```typescript
// 1. 特征守卫函数
function hasDeltaContent(chunk: any): chunk is { delta: { content: string } } {
  return typeof chunk?.delta?.content === 'string';
}

// 2. 安全收窄与消费
if (hasDeltaContent(chunk)) {
  console.log(chunk.delta.content); // 安全访问，无编译与运行时错误
}
```

---

### 面试加分项

- **断言函数（Assertion Functions）**：除 `is` 之外，使用 `asserts condition` 关键字（如 `asserts res is ValidPayload`），验证失败直接抛错，验证通过则后续代码作用域全部自动收缩为目标类型，代码更扁平。""",
        "followups": """## 追问 1：类型守卫函数本身如果写错了（比如判断条件与真实类型不符），TypeScript 能检查出来吗？

**回答要点**：
检查不出来！
`value is Type` 是开发者向编译器作出的“绝对承诺”。如果守卫函数内部返回了 `true` 但实际对象缺少该字段，编译器依然会信任开发者。因此守卫逻辑必须覆盖完备，或者使用 Zod 自动生成类型守卫。

---

## 追问 2：在处理大规模流式 Chunk 时，高频调用复杂的类型守卫会不会带来性能损耗？

**回答要点**：
会有轻微开销。优化方案是**仅在首个 Chunk 进行协议特征握手校验**，确定流式协议类型后缓存解析策略函数；后续的高频 Chunk 直接复用轻量解析路径，避免对每一帧数据重复做深层反射检查。"""
    },
    {
        "id": "fe-ai-003",
        "title": "请用TypeScript实现一个类型安全的Prompt模板解析器",
        "difficulty": "hard",
        "question": "请用TypeScript实现一个“类型安全的Prompt模板解析器”，要求支持变量插值、类型校验与默认值。",
        "answer": """### 一句话总结

利用 TypeScript 4.1+ 的**模板字面量类型（Template Literal Types）结合条件类型递归推导**，从模板字符串中静态提取 `{variable}` 占位符联合类型；配合高阶函数与 Proxy，在编译期强制要求必须传入所有匹配的插值参数，漏传或错传时直接静态报错。

---

### 详细回答

#### 1. 静态提取占位符：模板字面量递归
- 定义泛型类型 `ExtractParams<T>`：
  - 模式匹配 `${string}{${infer Param}}${infer Rest}`；
  - 递归提取所有 `{param}` 并组成联合类型，例如模板 `"Hello {name}, your role is {role}"` 静态推导出 `'name' | 'role'`。

#### 2. 参数类型绑定与必填校验
- 将推导出的联合类型转化为 Record 对象：`Record<ExtractParams<T>, string | number>`；
- 在函数签名中强约束入参，漏填任何一个参数在 VS Code 中立刻红线报错。

#### 3. 运行时正则替换与默认值处理
- 运行时通过正则 `/\\{(\\w+)\\}/g` 遍历匹配，若传入参数中包含该 key 则替换，若未传入则尝试使用预置默认值字典，否则抛出运行时异常。

---

### 核心代码片段（极简记法）

```typescript
// 1. 静态递归提取 {variable}
type ExtractParams<T extends string> = 
  T extends `${string}{${infer Param}}${infer Rest}` 
    ? Param | ExtractParams<Rest> 
    : never;

// 2. 类型安全的渲染函数
function renderPrompt<T extends string>(
  template: T,
  vars: Record<ExtractParams<T>, string | number>
): string {
  return template.replace(/\{(\\w+)\}/g, (_, key) => String((vars as any)[key]));
}

// ✅ 编译通过
renderPrompt("我是{role}，帮我分析{topic}", { role: "前端架构师", topic: "性能优化" });

// ❌ 编译报错：缺少属性 'topic'
// renderPrompt("我是{role}，帮我分析{topic}", { role: "前端架构师" });
```

---

### 面试加分项

- **支持默认值语法推导**：可扩展类型支持 `{name=默认值}` 语法，通过条件类型解析提取出可选参数类型 `Partial<ExtractDefaultParams<T>>`，实现更强大的工业级模板引擎。""",
        "followups": """## 追问 1：如果模板字符串非常长（几千字 Prompt），递归类型推导会不会触发 TS 的“类型实例化深度超限”（Type instantiation is excessively deep）？

**回答要点**：
会！TS 默认递归深度限制为 1000 左右。
应对策略：
1. 对于超长 Prompt，仅对变量字典做泛型约束，而非全文递归；
2. 或者拆分为段落式子模板进行组合推导；
3. 将模板声明放在独立的 `as const` 常量中。

---

## 追问 2：如何在类型系统中支持带类型的变量声明（如 {age:number}）？

**回答要点**：
在模板占位符中约定格式 `{varName:type}`，在 `infer Param` 中进一步用模板字面量切分为 `${infer Key}:${infer Type}`，并映射到对应原生类型（`'number' -> number`、`'boolean' -> boolean`）。"""
    },
    {
        "id": "fe-ai-004",
        "title": "如何用TypeScript模板字面量类型约束AI返回的特定格式字符串？",
        "difficulty": "medium",
        "question": "如何用TypeScript的模板字面量类型（Template Literal Types）约束AI返回的特定格式字符串（如日期、ID）？",
        "answer": """### 一句话总结

模板字面量类型允许使用类似 ES6 模板字符串的语法，在类型层面定义精确的**字符串模式（Pattern Matching）**。例如将日期约束为 `` `${number}-${number}-${number}` ``，或将 AI 产出的状态 ID 约束为 `` `session_${string}_v${number}` ``，实现编译期的结构合规强校验。

---

### 详细回答

#### 1. 常见约束场景
- **日期时间格式**：``type ISODate = `${number}-${number}-${number}`;``
- **实体 ID 规范**：``type MessageId = `msg_${string}`;``，约束必须以 `msg_` 为前缀；
- **颜色十六进制**：``type HexColor = `#${string}`;``
- **模型版本号**：``type ModelTag = `gpt-${'4o' | '4-turbo'}-${number}`;``

#### 2. 结合模式匹配进行条件收缩
通过 `extends` 检查传入的字符串是否符合该模板字面量模式：
```typescript
function validateMsgId<T extends string>(id: T extends `msg_${string}` ? T : never) {
  // 必须传入 msg_ 开头的字符串
}
```

---

### 核心代码片段（极简记法）

```typescript
// 1. 约束 AI 生成的日期与会话 ID 格式
type ISODate = `${number}-${number}-${number}`;
type SessionId = `sess_${string}_v${1 | 2}`;

// 2. 消费测试
const validDate: ISODate = "2026-05-20"; // ✅ 合法
// const invalidDate: ISODate = "2026/05/20"; // ❌ 报错：Type '"2026/05/20"' is not assignable to type '`${number}-${number}-${number}`'
```

---

### 面试加分项

- **静态 vs 运行时双重防线**：模板字面量类型只在**编译期**生效，而 AI 返回的内容是运行时到达的。必须指明在工程中结合 **Zod 字符串正则**（`z.string().regex(/^msg_/)`）作为运行时守卫，两者互补。""",
        "followups": """## 追问 1：能不能用模板字面量类型完全校验合法的月份（01~12）和日期（01~31）？

**回答要点**：
可以利用联合类型组合实现穷举：
``type Month = `0${1|2|3|4|5|6|7|8|9}` | '10' | '11' | '12';``
但对于复杂的闰年 2 月 29 天等业务逻辑，类型系统表达成本过高且会导致联合类型展开爆炸，应在运行时函数或 Zod 中校验。

---

## 追问 2：模板字面量类型在重构大模型版本号时有哪些实际工程价值？

**回答要点**：
当模型提供商升级版本（如 `gpt-4o-2024-05-13` 到 `gpt-4o-2026-08-01`）时，只需修改一处类型声明，全工程所有引用了该模型标识符的组件、请求头、埋点上报代码全部会自动提示报错，杜绝拼写手误。"""
    },
    {
        "id": "fe-ai-005",
        "title": "设计一个类型系统描述AI Agent执行过程的状态流转",
        "difficulty": "medium",
        "question": "设计一个类型系统，用于描述AI Agent执行过程中的状态流转（如思考→执行→观察→完成），并实现类型安全的状态切换。",
        "answer": """### 一句话总结

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

- **UI 穷尽性检查（Exhaustive Check）**：在组件内使用 switch-case 渲染不同状态卡片时，使用 `assertNever(state)` 确保后续新增状态（如 `awaiting_user_confirmation` 人机回环交互）时，编译器能立刻提示遗漏的 UI 分支。""",
        "followups": """## 追问 1：如果 Agent 执行过程中遇到需要“用户人工确认”（Human-in-the-loop）的场景，类型系统怎么扩展？

**回答要点**：
扩展一个新状态：
`| { status: 'awaiting_confirmation'; action: string; confirm: () => void; reject: (reason: string) => void }`。
在转移规则中约束其必须从 `acting`（准备调用敏感工具如支付、删除文件时）转移进入，只有用户触发 `confirm` 后才流转到实际执行，保证高风险操作的可控性。

---

## 追问 2：在复杂的生产级 Agent 工作流中，纯手写类型和使用 XState 状态机库怎么选？

**回答要点**：
轻量线性工作流手写类型即可，零依赖体积小；涉及并行分支、嵌套子状态、超时自动重试的复杂场景，选用 XState v5 状态机库，兼具类型安全与可视化排查。"""
    },
    {
        "id": "fe-ai-006",
        "title": "联合类型与交叉类型中，哪种更适合定义多模态AI输出？为什么？",
        "difficulty": "easy",
        "question": "在联合类型（Union Types）与交叉类型（Intersection Types）中，哪种更适合定义多模态AI输出（文本、图像、音频）？为什么？",
        "answer": """### 一句话总结

**联合类型（Union Types，`|`）更适合**。因为多模态 AI 输出的各片段在结构上是**互斥且异构的**（一段输出要么是纯文本、要么是图片、要么是音频），联合类型天然表达“多选一”语义；而交叉类型（`&`）表达的是字段合并，会导致属性冲突并迫使单个实体必须同时包含所有模态字段。

---

### 详细回答

#### 1. 为什么交叉类型（`&`）不适用？
- 交叉类型 `TypeA & TypeB` 要求对象同时拥有两者的所有属性；
- 如果多模态中各自分别有互斥字段（例如文本有 `content: string`，图像有 `imageUrl: string; width: number`，音频有 `duration: number; sampleRate: number`）；
- 若用交叉类型，会创造出一个“既有文本、又有宽高、又有音频采样率”的畸形对象，无法映射真实的单条多模态输出片段。

#### 2. 联合类型（`|`）结合 Tag 实现可辨识联合
- 通过统一的 `type` 或 `modality` 字段作为判别标签：
  ```typescript
  type TextBlock = { type: 'text'; text: string };
  type ImageBlock = { type: 'image'; url: string; mimeType: 'image/png' | 'image/jpeg' };
  type AudioBlock = { type: 'audio'; pcmData: ArrayBuffer; duration: number };

  type MultiModalBlock = TextBlock | ImageBlock | AudioBlock;
  ```
- 在渲染循环中，通过 `block.type` 即可实现完美的 TypeScript 自动类型收窄。

---

### 核心代码片段（极简记法）

```typescript
type ContentBlock =
  | { type: 'text'; text: string }
  | { type: 'image'; url: string; width: number }
  | { type: 'audio'; audioUrl: string; duration: number };

// 安全渲染多模态输出
function renderBlock(block: ContentBlock) {
  switch (block.type) {
    case 'text': return `<p>${block.text}</p>`;
    case 'image': return `<img src="${block.url}" width="${block.width}" />`;
    case 'audio': return `<audio src="${block.audioUrl}" controls />`;
  }
}
```

---

### 面试加分项

- **交叉类型在多模态中的正确用法**：交叉类型适合用于**公共基础属性的混入（Mixin）**，例如：
  `type BaseBlock = { id: string; timestamp: number };`
  `type TextBlock = BaseBlock & { type: 'text'; text: string };`
  将公共元数据与专属联合属性进行组合，是架构设计的最佳实践。""",
        "followups": """## 追问 1：如果一个大模型在单个输出中同时包含文本和图片（图文混排），联合类型怎么表示？

**回答要点**：
大模型的最终输出通常是“多模态片段数组”：
`type MultiModalResponse = ContentBlock[];`
每个独立的 Block 依然使用联合类型互斥表示，整个回答通过数组按先后顺序组合展示，实现灵活的图文混排。

---

## 追问 2：联合类型过多（比如支持 20 种不同的工具或模态）会导致什么性能问题？

**回答要点**：
大型联合类型会导致 TypeScript 编译器的类型检查耗时显著上升（Union Expansion 计算复杂度激增）。建议对相似类型按子系统分组，或采用泛型注册表模式分散推导。"""
    },
    {
        "id": "fe-ai-007",
        "title": "如何用TypeScript声明支持流式Chunk与错误处理的通用传输接口？",
        "difficulty": "medium",
        "question": "如何用TypeScript声明一个支持流式Chunk数据与错误处理的泛型接口，并兼容SSE、WebSocket等多种传输方式？",
        "answer": """### 一句话总结

声明兼容 SSE、WebSocket 和 Fetch Stream 的通用流式接口，核心是利用 **`AsyncIterable<T>`（异步可迭代对象）** 屏蔽底层通信协议差异，配合**事件回调泛型接口（OnChunk / OnError / OnComplete）**与 **`AbortSignal`** 实现统一的流式生命周期抽象。

---

### 详细回答

#### 1. 为什么首选 AsyncIterable 作为通用抽象？
- 现代 JavaScript/TypeScript 原生支持异步生成器与 `for await...of` 语法；
- 无论是 SSE 的 `ReadableStream`、WebSocket 的 `message` 事件，还是 Node.js Stream，均能轻量包装为 `AsyncIterable<Chunk>`；
- 业务消费层无需关心底层是长轮询、SSE 还是 WS，只需统一 `for await (const chunk of stream)`。

#### 2. 通用流式控制器接口设计
```typescript
interface StreamClientConfig {
  url: string;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

interface StreamResponse<TData, TError = Error> {
  // 1. 异步迭代器语法糖
  [Symbol.asyncIterator](): AsyncIterator<TData>;
  // 2. 事件监听式回调
  on(event: 'chunk', listener: (data: TData) => void): this;
  on(event: 'error', listener: (err: TError) => void): this;
  on(event: 'end', listener: () => void): this;
  // 3. 主动中断能力
  cancel(): void;
}
```

---

### 核心代码片段（极简记法）

```typescript
// 通用传输适配层签名
type TransportType = 'sse' | 'websocket' | 'fetch-stream';

interface UniversalStreamRequest<TPayload, TChunk> {
  transport: TransportType;
  endpoint: string;
  payload: TPayload;
  onChunk: (chunk: TChunk) => void;
  onError: (error: Error) => void;
  signal?: AbortSignal;
}

// 统一消费示例
function createStream<P, C>(req: UniversalStreamRequest<P, C>): () => void {
  // 内部根据 transport 分流为 SSE 或 WS 实现，外部 API 保持一致
  return () => { /* 取消订阅 */ };
}
```

---

### 面试加分项

- **泛型约束错误结构**：很多团队把错误类型写成 `any`。应该泛型约束 `TError = { code: string; message: string; retryable: boolean }`，在类型层面指导前端决定是否发起自动重试。""",
        "followups": """## 追问 1：AsyncIterable 和 RxJS Observable 在流式前端场景怎么选？

**回答要点**：
普通 AI 对话展示使用 `AsyncIterable` 最自然，零依赖原生支持；若应用包含高并发流式合并、动态多通道过滤、音视频复杂流编排，选用 RxJS 配合强大的操作符（`switchMap`、`mergeMap`）更合适。

---

## 追问 2：如果在流式传输过程中连接意外中断，AsyncIterable 如何触发终止清理？

**回答要点**：
在异步生成器内部实现 `return()` 和 `finally` 块。当外部调用 `break` 或 `AbortController.abort()` 时，运行时会自动触发生成器的 `finally`，在其中关闭 WebSocket 连接或释放 Reader 锁。"""
    },
    {
        "id": "fe-ai-008",
        "title": "当AI服务返回数据包含递归引用时，TS如何定义并避免类型爆炸？",
        "difficulty": "hard",
        "question": "当AI服务返回的数据结构包含递归引用（如对话树）时，如何用TypeScript定义并避免循环引用导致的类型爆炸？",
        "answer": """### 一句话总结

定义递归数据结构（如分支对话树、思维链树状节点）时，采用 **`interface` 延迟解析特性结合显式子节点数组 `children: TreeNode[]`**；避免在映射类型或复杂条件类型中直接进行无基线终止的无界递归，或引入深度计数器泛型做递归深度截断，防止触发 TS2589 编译器崩溃。

---

### 详细回答

#### 1. 为什么 type 会报错而 interface 不会？
- **类型别名自引用**：若写 `type TreeNode = { id: string } & { children: TreeNode[] };` 或直接自引用泛型，在复杂计算时编译器会尝试深度展开，极易引发 `Type instantiation is excessively deep and possibly infinite (TS2589)`。
- **Interface 延迟求值**：TS 对 `interface` 采用懒求值（Lazy Evaluation）机制，自引用时不会立即展开内部属性，是声明递归类型的首选。

#### 2. 正确定义多分支对话树（Conversation Tree）
```typescript
export interface ConversationNode {
  id: string;
  parentId: string | null;
  message: { role: 'user' | 'assistant'; content: string };
  // 递归引用自身数组
  children: ConversationNode[];
}
```

#### 3. 递归类型的深度限制器（Depth Counter 技巧）
在编写需要递归修改属性的工具泛型（如 DeepReadonly 或 DeepPartial）时，通过元组长度作为计数器防止无限递归：
```typescript
type Prev = [never, 0, 1, 2, 3]; // 限制最大深度为 4
type DeepPartial<T, D extends number = 3> = [D] extends [never] ? T : {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K], Prev[D]> : T[K];
};
```

---

### 核心代码片段（极简记法）

```typescript
// 标准树状对话节点（利用 interface 避免展开爆炸）
interface ChatTreeNode {
  nodeId: string;
  content: string;
  children: ChatTreeNode[]; // 安全递归
}

// 拍平引用的字典结构（工程最佳实践）
interface FlatChatTree {
  rootId: string;
  nodes: Record<string, { id: string; content: string; childIds: string[] }>;
}
```

---

### 面试加分项

- **状态管理反范式化（Normalized State）**：指出“在 Redux/Zustand 状态管理中，尽量避免直接存储深层嵌套的树状对象”。应将其拍平为范式化结构（`Record<id, Node>`），通过 ID 关联。不仅类型推导极其简单、彻底消除递归类型隐患，还能避免单节点更新触发整棵树深拷贝。""",
        "followups": """## 追问 1：前端如何将拍平的 FlatChatTree 高效还原为树状结构供 UI 递归组件渲染？

**回答要点**：
基于 Map 的一次性遍历：遍历字典创建所有节点对象并放入 Map；再次遍历根据 `parentId` 直接把子节点 `push` 到父节点的 `children` 数组中，时间复杂度为 $O(N)$，比递归深搜快得多。

---

## 追问 2：React 递归渲染对话树组件时，如何防止调用栈溢出？

**回答要点**：
当对话分支层级过深时，改用“扁平列表虚拟滚动”：通过深度优先遍历预先计算好每个节点的缩进深度（Indent Level），将树转换为一维线性数组，交由虚拟列表渲染。"""
    },
    {
        "id": "fe-ai-009",
        "title": "请设计一个类型系统用于AI模型元数据的静态校验",
        "difficulty": "medium",
        "question": "请设计一个类型系统，用于前端对AI模型元数据（版本、输入输出格式、最大Token数）的静态校验。",
        "answer": """### 一句话总结

通过**“字面量类型字典（Const Configuration Map）+ 泛型索引访问”**定义不可变元数据字典；当切换选择模型时，自动关联推导出该模型合法的 **上下文窗口上限、支持的模态（文本/图片/音频）、Temperature 允许区间**，在编译期杜绝将多模态图片传给纯文本模型等低级配置错误。

---

### 详细回答

#### 1. 模型元数据配置表建模
通过 `as const` 锁定不可变字面量，保留最精确的字面量类型：
```typescript
const MODEL_REGISTRY = {
  'gpt-4o': {
    maxTokens: 128000,
    supportsVision: true,
    supportsTools: true,
    costPer1kTokens: 0.005
  },
  'text-embedding-3-small': {
    maxTokens: 8191,
    supportsVision: false,
    supportsTools: false,
    costPer1kTokens: 0.00002
  }
} as const;

type ModelName = keyof typeof MODEL_REGISTRY;
type ModelMeta<T extends ModelName> = typeof MODEL_REGISTRY[T];
```

#### 2. 根据模型类型动态约束请求入参
当入参选择了模型后，其他参数自动联动推导：
```typescript
type ChatRequest<M extends ModelName> = {
  model: M;
  prompt: string;
  // 若模型不支持视觉，images 字段直接为 never，禁止传入
  images?: ModelMeta<M>['supportsVision'] extends true ? string[] : never;
};
```

---

### 核心代码片段（极简记法）

```typescript
const MODELS = {
  'gpt-4o': { vision: true, maxTokens: 128000 },
  'deepseek-chat': { vision: false, maxTokens: 64000 }
} as const;

type ModelKey = keyof typeof MODELS;

// 根据模型静态推导入参约束
type GenerateParams<M extends ModelKey> = {
  model: M;
  images?: typeof MODELS[M]['vision'] extends true ? string[] : never;
};

// ✅ 合法
const req1: GenerateParams<'gpt-4o'> = { model: 'gpt-4o', images: ['http://...'] };

// ❌ 编译报错：Type 'string[]' is not assignable to type 'undefined'
// const req2: GenerateParams<'deepseek-chat'> = { model: 'deepseek-chat', images: ['http://...'] };
```

---

### 面试加分项

- **跨项目共享元数据包**：在 Monorepo 架构中，将模型元数据提取为 `@org/model-types` 共享包，Node.js 网关层与 Web 前端共用同一份配置，模型参数升级只需发布一个单包即可全局同步。""",
        "followups": """## 追问 1：前端如何防止用户手动在本地修改 LocalStorage 中的模型配置绕过静态类型校验？

**回答要点**：
前端类型系统只防手误与编译期 Bug。任何从本地存储、用户输入或外部 URL Query 读出的配置，必须使用 Zod 在运行时重新进行一次 Schema 校验与上限截断，绝不盲目信任客户端本地数据。

---

## 追问 2：如何用 TS 校验用户设置的上下文长度没有超出该模型的 maxTokens？

**回答要点**：
TS 无法直接做数值大小不等式比较（如 `Value <= 128000`）。数值范围校验必须借助运行时函数或 Zod 的 `.max(MODELS[model].maxTokens)` 完成。"""
    },
    {
        "id": "fe-ai-010",
        "title": "如何用TypeScript的infer关键字提取AI流式响应嵌套字段？",
        "difficulty": "hard",
        "question": "如何用TypeScript的infer关键字提取AI流式响应中的嵌套数据字段（如choices[0].delta.content）？",
        "answer": """### 一句话总结

**`infer` 关键字用于在条件类型的模式匹配中“声明待推导的类型变量”**。通过递归或深层结构解构，可精准穿透嵌套的数组与对象，自动提取诸如 `Response['choices'][number]['delta']['content']` 等深层叶子节点类型，即便服务端接口定义包裹多层也能零冗余提取纯文本类型。

---

### 详细回答

#### 1. infer 的核心工作机制
`T extends Pattern<infer P> ? P : Fallback`：
- `extends` 左边是传入的具体类型；
- 右边是包含 `infer X` 的占位模板；
- 编译器会反向推导匹配占位符的真实类型并将其绑定到 `X` 上。

#### 2. 提取 choices[0].delta.content 案例
```typescript
type OpenAIChatChunk = {
  id: string;
  choices: Array<{
    index: number;
    delta: { content?: string; role?: string };
  }>;
};

// 利用 infer 提取数组元素与嵌套 delta
type ExtractContent<T> = T extends {
  choices: Array<{
    delta: { content?: infer C };
  }>;
} ? C : never;

type Result = ExtractContent<OpenAIChatChunk>; // 推导为 string | undefined
```

---

### 核心代码片段（极简记法）

```typescript
// 通用路径提取工具类型
type ExtractDeltaContent<T> = T extends { choices: [{ delta: { content: infer Text } }] }
  ? Text
  : T extends { choices: Array<{ delta: { content?: infer Text } }> }
  ? Text
  : never;

// 测试推导
type MyChunk = { choices: [{ delta: { content: string } }] };
type ContentType = ExtractDeltaContent<MyChunk>; // 结果是 string
```

---

### 面试加分项

- **穿透 Promise 与 AsyncIterable**：在流式客户端中，接口往往返回 `Promise<AsyncIterable<Chunk>>`。可结合 `Awaited<T>` 与 `infer` 编写 `UnwrapStream<T>` 工具类型，一步到位提取出最终消费的 Chunk 类型。""",
        "followups": """## 追问 1：infer 和直接索引访问 T['choices'][0]['delta']['content'] 相比，优势在哪？

**回答要点**：
直接索引访问要求结构完全已知且中间每一层都必须非空，如果 `choices` 为空数组或者格式可能是其他分支，索引访问直接报错；而 `infer` 配合条件类型具有**模式匹配容错性**，匹配失败会优雅走 `never` 兜底，不会导致编译崩溃。

---

## 追问 2：infer 在提取函数返回值的 Promise 泛型时怎么用？

**回答要点**：
编写 `type UnpackPromise<T> = T extends Promise<infer U> ? U : T`，或者直接使用内置的 `Awaited<T>`，底层原理完全相同。"""
    },
    {
        "id": "fe-ai-011",
        "title": "请设计一个支持断线重连+消息去重的SSE客户端",
        "difficulty": "medium",
        "question": "请设计一个支持“断线重连+消息去重”的SSE客户端，并处理AI长文本生成中的网络抖动问题。",
        "answer": """### 一句话总结

AI 场景下的 SSE 本质是**带状态的流式断点续传**。由于原生 `EventSource` 只支持 GET 且无法自定义请求头，生产中必须使用 `fetch` + `ReadableStream`。通过**服务端返回递增序列号（`id`）**实现断点续推与本地滑动窗口去重，配合**带 Jitter 的指数退避**防雪崩，并利用 `TextDecoder` 的 `stream: true` 解决弱网下的中文截断乱码。

---

### 详细回答

#### 1. 为什么不用原生 EventSource？
- **只支持 GET 请求**：AI 对话需要传递多轮上下文（几千字 Prompt），极易超出 URL 长度限制（414 URI Too Long）。
- **无法自定义 Header**：无法携带 `Authorization: Bearer <token>` 等鉴权头。
- **推荐方案**：采用 `fetch` + `ReadableStream`，配合 `AbortController` 实现自主可控的流式监听与中断。

#### 2. 断点续接与消息去重
- **递增 Sequence ID**：服务端推流的每个 chunk 带递增 `id`（如 `id: 42`），前端维护 `lastEventId`。
- **断线续推**：重连时通过请求头或 Payload 带上 `last_event_id: 42`，服务端直接从 43 接着推，避免大模型重新推理浪费 Token。
- **滑动窗口去重**：前端用定长 `Set` 记录最近接收的 ID，若因网络重传收到重复包直接静默丢弃。

#### 3. 指数退避重连（防雪崩）
- **重试间隔退避**：重试时间按 $1s \to 2s \to 4s \to 8s$ 递增，并附加随机扰动（Jitter），防止成千上万个客户端同时重试冲垮后端。
- **错误类型熔断**：遇到 `401`、`400` 等不可恢复的客户端错误立即终止重试；仅对网络掉线或 `502/503/504` 等网关错误发起重试。

#### 4. 弱网长文本抖动优化
- **中文截断乱码**：UTF-8 汉字占 3 字节，TCP 分包可能将字符切在两半。**必须开启 `{ stream: true }`**，让解码器自动缓冲未完成的字节：
  ```javascript
  const decoder = new TextDecoder('utf-8');
  const text = decoder.decode(chunk, { stream: true });
  ```
- **打字机平滑队列（Jitter Buffer）**：把收到的字符放入 FIFO 队列，由 `requestAnimationFrame` 匀速吐出，抹平视觉颠簸。

---

### 核心代码片段（极简记法）

```javascript
// 核心：fetch 接收 ReadableStream + 断点续接
const res = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt, lastEventId })
});

const reader = res.body.getReader();
const decoder = new TextDecoder('utf-8');

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  const chunkText = decoder.decode(value, { stream: true }); // stream: true 必填防乱码
  processSSE(chunkText);
}
```

---

### 面试加分项

- **服务端协同认知**：断点重连不是前端单方面的事，必须服务端配合在 Redis 缓存生成中的流式队列；若服务端不支持，重连只能重新生成。
- **主动取消（Abort）**：用户离开或点击停止时，必须用 `AbortController.abort()` 掐断连接，并通知后端停止模型推理，避免持续计费。""",
        "followups": """## 追问 1：大模型生成途中用户关闭页面或点击“停止”，后端会继续扣费吗？前端怎么做？

**回答要点**：
若前端只在客户端直接销毁组件，HTTP 层的 TCP 连接不一定立即断开，或代理网关未向源站转发客户端断开信号。
前端应使用 `AbortController.abort()` 显式中断连接，并向后端发送一条轻量终止通知（如 `POST /api/chat/stop`），服务端主动调用大模型 cancel 接口终止推理。

---

## 追问 2：为什么不用 WebSocket 而选择 SSE 来做 AI 对话流式推送？

**回答要点**：
AI 对话是典型的一问一答单向推流，SSE 基于标准 HTTP，天然契合单向文本流；能无缝复用现有鉴权、CDN 和负载均衡器，在 HTTP/2 下还能复用 TCP 连接；而 WebSocket 双向协议在代理和保活心跳上复杂度更高。"""
    },
    {
        "id": "fe-ai-012",
        "title": "如何在前端实现一个流式Markdown解析器并避免标签截断？",
        "difficulty": "hard",
        "question": "如何在前端实现一个“流式Markdown解析器”，在AI逐字输出过程中实时渲染标题、列表、代码块，并避免标签截断？",
        "answer": """### 一句话总结

流式 Markdown 的核心矛盾是**未闭合标签导致的渲染破碎**与**高频全量解析导致的 CPU 卡顿**。生产级方案采用**“虚拟闭合修复 + 块级增量渲染 + 帧级节流”**：在解析前通过轻量状态机补齐未闭合的代码块反引号 ```` `，将文本按换行拆分为已稳定块（不可变）与尾部活跃块（仅解析尾部），并通过 `requestAnimationFrame` 批量节流更新。

---

### 详细回答

#### 1. 语法标签截断的痛点与解法（虚拟补全）
- **痛点**：模型生成代码块时，先输出 ````ts`，在闭合的反引号到达前，整个后续内容都会被解析器当成错误语法或未格式化文本，造成界面剧烈跳动或闪烁。
- **解法（补全探测）**：在交给 Markdown 引擎前，用轻量状态机扫描未闭合的标识符并临时补齐：
  - 统计反引号 ```` ` 的奇偶性，若为奇数，在文本末尾虚拟追加 `\\n```` 进行解析；
  - 探测未闭合的加粗 `**`、行内代码 `` ` ``、数学公式 `$`，临时在末尾补全闭合符号，确保 AST 解析结构合法。

#### 2. 避免全量解析：按块（Block）增量切分
- **不可变稳定块**：一段文本只要后面出现了两个换行符 `\\n\\n`，说明该段落、标题或列表项已经完结，其 AST 结构不再发生变化。
- **增量缓存策略**：
  - 前端将流式文本拆分为 `[历史稳定块列表]` 和 `[当前正在生成的尾部块]`；
  - 稳定块直接复用已缓存的虚拟 DOM / 渲染结果（React.memo 缓存）；
  - 每次新 Token 仅对末尾活跃块进行解析，将单次解析耗时从 $O(N)$ 降到 $O(1)$。

#### 3. 渲染性能优化：节流与异步调度
- **避免每字重渲染**：大模型每秒可能推送 20~50 个 Token，若每个 Token 都触发 React `setState`，主线程会彻底被渲染任务占满。
- **RAF 节流缓冲**：将收到的 Token 写入内存 Buffer，利用 `requestAnimationFrame`（约 16ms 一帧）进行合并批量渲染。

---

### 核心代码片段（极简记法）

```javascript
// 尾部标签虚拟补齐（核心逻辑）
function patchIncompleteMarkdown(raw) {
  const codeBlockCount = (raw.match(/```/g) || []).length;
  if (codeBlockCount % 2 !== 0) {
    return raw + '\\n```'; // 虚拟补齐闭合反引号
  }
  return raw;
}
```

---

### 面试加分项

- **代码块高亮性能优化**：代码语法高亮极其消耗 CPU。在流式生成期间只做纯文本展示或轻量高亮，等代码块收到闭合标记 ```` ` 后再异步执行一次完整的高亮 AST 解析。""",
        "followups": """## 追问 1：如果大模型生成的内容非常长（数万字），即使增量解析，DOM 节点过多也会卡顿，怎么办？

**回答要点**：
采用“块级虚拟滚动”（Virtual List）：将解析后的 Markdown 段落作为列表项，仅挂载视口内及上下预加载的段落 DOM，视口外只保留纯高度撑开容器。

---

## 追问 2：流式输出时页面自动向下滚动，如果用户手动向上翻看历史记录，如何处理滚动冲突？

**回答要点**：
监听容器的 `onScroll` 事件，当检测到用户手动向上滚动离开底部一定距离（如 50px）时，立即解开“自动吸底锁定”；界面右下角展示“新内容生成中 ↓”悬浮按钮供随时点击回到底部。"""
    },
    {
        "id": "fe-ai-013",
        "title": "当AI流式数据包含多个独立片段时，如何设计Chunk合并算法？",
        "difficulty": "medium",
        "question": "当AI流式返回的数据包含多个独立片段（如文本、代码、表格）时，如何设计Chunk合并算法以保证片段完整性？",
        "answer": """### 一句话总结

多片段 Chunk 合并的核心是**“基于唯一片段标识符（`part_index` / `block_id`）的分区流累加器”**。前端维护一个有序的片段 Map，流式到达的增量根据片段 ID 追加到对应 Buffer 中，并依据服务端发送的结束标记（如 `finish_part`）冻结该片段并触发类型特定的解析器（文本、表格、代码）。

---

### 详细回答

#### 1. 为什么不能简单做字符串拼接？
- 现代复杂 Agent 可能同时并行输出“思考过程（Thinking Block）”、“正式回答（Text Block）”和“工具调用参数（Tool Call Block）”；
- 这些数据包交错推送到前端，若直接字符串拼接，思考与正文内容会彻底混乱。

#### 2. 分区累加算法设计
- 服务端定义协议格式：
  `{ id: "part_1", type: "text", delta: "正在为您" }`
  `{ id: "part_2", type: "code", language: "python", delta: "print('hello')" }`
- 客户端算法：
  1. 维护 `blocks: Map<string, Block>` 与 `blockOrder: string[]`；
  2. 收到 Chunk，通过 `id` 定位目标 Block；
  3. 若不存在，在末尾插入新 Block；若存在，执行 `block.content += delta`；
  4. 当收到 `is_finished: true` 时，将该 Block 标记为不可变，移出高频渲染池。

---

### 核心代码片段（极简记法）

```javascript
function mergeMultiPartChunk(state, chunk) {
  const { partId, type, delta, isFinished } = chunk;
  const existing = state.parts[partId] || { type, content: '', isFinished: false };

  return {
    ...state,
    parts: {
      ...state.parts,
      [partId]: {
        ...existing,
        content: existing.content + delta,
        isFinished: isFinished || existing.isFinished
      }
    }
  };
}
```

---

### 面试加分项

- **部分 JSON 容错解析（Partial JSON）**：针对表格或工具调用的 JSON 片段，流式传输未完成时格式是不合法的。使用 `partial-json` 或轻量堆栈状态机，能在 JSON 仅传输了一半时就能渲染出部分表格行，实现渐进式呈现。""",
        "followups": """## 追问 1：如果网络丢包导致后发出的 part_2 比 part_1 先到达，前端如何保证界面排序正确？

**回答要点**：
Chunk 数据包中必须包含服务端的绝对序列号 `seq_num` 或 `part_index`。前端维护优先队列（Min-Heap），收到乱序包时不直接渲染，而是暂存入待重排缓冲区，按序列号排齐后再执行消费合并。

---

## 追问 2：思考过程（Thinking 过程）渲染完后，用户希望默认收起，交互上怎么协同？

**回答要点**：
当收到该思考片段的 `isFinished: true` 事件时，触发折叠动画将高度变为 0，并展示“已深度思考（耗时 3 秒）”的折叠卡片，让正式回答瞬间浮现到首屏视野中央。"""
    },
    {
        "id": "fe-ai-014",
        "title": "请实现一个支持优先级调度的流式请求队列",
        "difficulty": "hard",
        "question": "请实现一个支持“优先级调度”的流式请求队列，允许用户中断低优先级生成（如翻译）以优先处理高优先级任务（如代码生成）。",
        "answer": """### 一句话总结

优先级流式队列采用**“有限并发池 + 优先级大顶堆 + 动态抢占式 Abort 机制”**。当高优先级任务入队且并发已满时，通过绑定的 `AbortController` 暂停或中断正在运行的低优先级任务并将其回填回待执行队列，立即将网络与计算资源让位给高优先级任务。

---

### 详细回答

#### 1. 为什么普通 FIFO 队列无法满足需求？
- 普通队列遵循先入先出，若用户先发起了耗时 30 秒的“全文翻译”，紧接着发起了紧急的“修复代码报错”，代码任务只能干等 30 秒；
- 浏览器同域名并发通道有限，多流并行会导致互相抢带宽严重卡顿。

#### 2. 调度器核心要素
- **Priority PriorityQueue**：根据任务权重排序（High = 3, Normal = 2, Low = 1）；
- **抢占模式（Preemption）**：
  - 判定：当前活动任务的优先级若低于新入队任务；
  - 动作：触发当前任务的 `abortController.abort()`，保存其中断状态（以便后续断点恢复），立即调度高优先级任务启动。

---

### 核心代码片段（极简记法）

```javascript
class PriorityStreamScheduler {
  constructor(maxConcurrent = 1) {
    this.maxConcurrent = maxConcurrent;
    this.running = [];
    this.queue = []; // 按 priority 降序
  }

  add(task) {
    this.queue.push(task);
    this.queue.sort((a, b) => b.priority - a.priority);
    this.schedule();
  }

  schedule() {
    // 抢占逻辑：若队列头部任务优先级 > 正在运行任务的最低优先级
    if (this.running.length >= this.maxConcurrent) {
      const lowestRunning = this.running.sort((a, b) => a.priority - b.priority)[0];
      const highestPending = this.queue[0];
      if (highestPending && highestPending.priority > lowestRunning.priority) {
        lowestRunning.abort(); // 掐断低优先级
      }
      return;
    }

    const nextTask = this.queue.shift();
    if (nextTask) {
      this.running.push(nextTask);
      nextTask.run().finally(() => {
        this.running = this.running.filter(t => t !== nextTask);
        this.schedule();
      });
    }
  }
}
```

---

### 面试加分项

- **支持断点暂停而不是废弃**：被抢占的低优先级任务不是直接销毁，而是记录当前的 `lastEventId` 并重新塞入队列头部。当高优先级任务完成后，低优先级任务自动发起断点续传。""",
        "followups": """## 追问 1：前端中断任务后，如果服务端仍然在继续消耗 Token，如何通知服务端停止？

**回答要点**：
前端在调用本地 `controller.abort()` 掐断网络连接的同时，发一条带该任务 ID 的轻量信令（`POST /api/chat/pause`），让服务端工作流感知暂停并释放大模型推理句柄。

---

## 追问 2：如果两个任务优先级完全相同，调度顺序是什么？

**回答要点**：
采用 FIFO 作为第二仲裁维度（记录入队时间戳 `createdAt`），同优先级先进先出，保证调度公平性，防止早期任务饥饿死锁。"""
    },
    {
        "id": "fe-ai-015",
        "title": "在React 18+中如何用useTransition与useDeferredValue优化AI流式渲染？",
        "difficulty": "medium",
        "question": "在React 18+中，如何用useTransition与useDeferredValue优化AI流式输出的渲染性能，避免主线程阻塞？",
        "answer": """### 一句话总结

高频流式输出的核心痛点是**昂贵的文本渲染阻塞了用户的紧急交互**。利用 React 18 并发特性的时间切片机制，通过 **`useTransition`** 或 **`useDeferredValue`** 将大段 Markdown/代码高亮降级为**“低优先级过渡更新”**，优先保障用户输入、页面滚动和按钮点击的 60fps 响应，并在高频打断时丢弃过期帧。

---

### 详细回答

#### 1. React 18 并发渲染与优先级调度
- **紧急更新（Urgent Updates）**：直接影响用户即时交互的动作（如输入框打字、点击“停止生成”、鼠标悬停），要求立即响应（0~16ms）。
- **过渡更新（Transition Updates）**：视图转换、大段富文本重绘等（如 AI 流式文本追加），用户对几毫秒的微延迟不敏感。
- **并发打断机制**：当主线程正在渲染沉重的 Markdown 时，若用户突然在输入框敲入一个字符，React 会立即暂停当前的 Markdown 渲染，优先处理输入框更新，避免界面假死。

#### 2. useTransition：在更新发起端降级
- 适合当你**掌控状态更新动作源头**时使用。
- 将流式消息的 `setStreamingContent` 包裹在 `startTransition` 中：
  ```javascript
  const [isPending, startTransition] = useTransition();

  function onReceiveChunk(newText) {
    startTransition(() => {
      setFullText(prev => prev + newText);
    });
  }
  ```

#### 3. useDeferredValue：在数据消费端延迟
- 传入高频变化的文本，返回延迟更新的值：
  ```javascript
  function MessageItem({ rawContent }) {
    const deferredContent = useDeferredValue(rawContent);
    return <ExpensiveMarkdown content={deferredContent} />;
  }
  ```

---

### 核心代码片段（极简记法）

```javascript
function AIChat() {
  const [streamText, setStreamText] = useState('');
  const [, startTransition] = useTransition();
  const deferredText = useDeferredValue(streamText);

  function handleChunk(chunk) {
    startTransition(() => setStreamText(prev => prev + chunk));
  }

  return (
    <>
      <FastInput /> {/* 用户打字永远流畅 */}
      <ExpensiveMarkdown content={deferredText} />
    </>
  );
}
```

---

### 面试加分项

- **节流与调度双管齐下**：`useTransition` 解决的是**调度优先级**，无法消除实际的 CPU 运算总量。在极高频推送下（如每秒 100+ chunk），仍需在网络接收层配合 `requestAnimationFrame` 做 16ms 批处理节流，双剑合璧效果最好。""",
        "followups": """## 追问 1：useTransition 和普通的 setTimeout 防抖节流相比，本质优势是什么？

**回答要点**：
定时器延迟是写死的死等待，性能好也会慢；而 `useTransition` 属于 React Fiber 内部时间切片，设备越强响应越快，且能随时被高优先级的打字点击事件即时打断。

---

## 追问 2：流式输出完成时，如何确保最后一次完整文本不被延迟渲染？

**回答要点**：
收到 `[DONE]` 结束标记时，跳出 `startTransition` 发起一次普通的同步紧急更新，确保最终代码高亮和复制按钮瞬间完整展示。"""
    },
    {
        "id": "fe-ai-016",
        "title": "设计一个流式数据缓存策略，将AI已生成内容分段存储于IndexedDB",
        "difficulty": "medium",
        "question": "设计一个“流式数据缓存”策略，将AI已生成的内容分段存储于IndexedDB，支持离线续写与历史回放。",
        "answer": """### 一句话总结

流式缓存采用**“内存 Buffer 批量聚合 + IndexedDB 增量 Append + 版本化快照”**。生成过程中按时间窗口（如每 2 秒）或 Token 阈值批量向 IndexedDB 写入增量 Chunk，会话完成写入 Final 完整实体；刷新或断网时从 IndexedDB 瞬间读取断点，实现毫秒级会话复原。

---

### 详细回答

#### 1. 为什么不用 localStorage 而用 IndexedDB？
- **容量上限**：localStorage 只有 5MB，长文本多轮对话几天就占满报错；
- **异步非阻塞**：localStorage 读写是同步阻塞主线程的，高频写入会直接拖慢 UI 帧率；IndexedDB 完全异步运行。

#### 2. 分段存储数据结构设计
- **`sessions` 存储表**：保存会话元数据（ID、标题、状态、最后更新时间）；
- **`chunks` 存储表**：复合索引 `[sessionId + seq]`，每条包含分段内容与时间戳。

#### 3. 性能优化：防抖写盘
- 严禁每个 Token 写一次 IndexedDB（事务创建极其频繁会卡死浏览器）；
- 维护一个内存 Buffer，每累积 50 个字符或每间隔 2 秒触发一次 `transaction.put` 批量写入。

---

### 核心代码片段（极简记法）

```javascript
let pendingBuffer = '';
let flushTimer = null;

function saveChunkToDB(sessionId, seq, delta) {
  pendingBuffer += delta;
  clearTimeout(flushTimer);

  flushTimer = setTimeout(async () => {
    const db = await openDB('AICache', 1);
    const tx = db.transaction('chunks', 'readwrite');
    tx.objectStore('chunks').put({
      id: `${sessionId}_${seq}`,
      sessionId,
      seq,
      text: pendingBuffer,
      time: Date.now()
    });
    pendingBuffer = '';
  }, 1000); // 1秒节流写入
}
```

---

### 面试加分项

- **LRU 淘汰与配额管理**：浏览器存储空间有限。设计冷数据淘汰机制：通过 `navigator.storage.estimate()` 监听配额，超限时清理 30 天以前的非收藏历史会话。""",
        "followups": """## 追问 1：如果用户多标签页打开同一个会话同时生成，IndexedDB 怎么防止数据覆盖混乱？

**回答要点**：
基于乐观锁或 BroadcastChannel 状态广播。在会话元数据中保存 `version` 字段，写入时校验版本号；或通过 Web Locks API（`navigator.locks.request`）获取会话排他锁，确保只有一个标签页能进行流式写入。

---

## 追问 2：IndexedDB 中的数据如何进行全文快速搜索？

**回答要点**：
可以在前端引入微型倒排索引库（如 `FlexSearch` 或 `MiniSearch`），在写入 IndexedDB 的同时更新内存索引字典，实现万条历史对话毫秒级关键词检索。"""
    },
    {
        "id": "fe-ai-017",
        "title": "如何用Web Worker并行处理多个AI流式响应并同步跨线程状态？",
        "difficulty": "hard",
        "question": "如何用Web Worker并行处理多个AI流式响应（如同时生成文本与摘要），并实现跨线程状态同步？",
        "answer": """### 一句话总结

将多路流式 fetch 网络请求与 Markdown/JSON 解析全部**剥离到 Web Worker 独立线程**中执行；主线程仅接收解析好的结构化 UI 数据，通过 **`Transferable Objects`（零拷贝转移）或结构化克隆 + `MessageChannel`** 降低线程通信开销，彻底释放主线程保障 60fps 动画流畅度。

---

### 详细回答

#### 1. 为什么要把流式处理移入 Worker？
- 多路流式并发时（如边生成正文、边生成思维导图、边提取摘要），多个流的数据解码、正则匹配、AST 构建在单主线程会导致严重的丢帧和输入卡顿；
- Web Worker 拥有独立的事件循环和后台线程，计算再繁重也绝不卡死主界面。

#### 2. 通信架构设计
- **请求派发**：主线程发送 `{ type: 'START_STREAM', streamId: 'summary', url, prompt }` 到 Worker；
- **Worker 内部**：Worker 独立调用 `fetch(..., { signal })` 并读取流；
- **流式同步（批量节流 PostMessage）**：Worker 内部按 50ms 节流将解析好的文本差量批量发送给主线程，避免通信通道过度饱和。

---

### 核心代码片段（极简记法）

```javascript
// worker.js (子线程独立拉取流)
self.onmessage = async (e) => {
  const { url, payload } = e.data;
  const res = await fetch(url, { method: 'POST', body: JSON.stringify(payload) });
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    // 解析并回传给主线程
    self.postMessage({ type: 'CHUNK', text: decoder.decode(value, { stream: true }) });
  }
  self.postMessage({ type: 'DONE' });
};
```

---

### 面试加分项

- **SharedArrayBuffer 共享内存（极端高性能）**：对于需要双向高频交互的场景，可通过 `SharedArrayBuffer` 建立环形缓冲区，配合 `Atomics` 原语实现零通信延迟的状态同步。""",
        "followups": """## 追问 1：Web Worker 中可以使用 DOM 解析库吗？

**回答要点**：
Worker 内部没有 `window` 和 `document`，不能直接使用依赖真实 DOM 的操作（如 `document.createElement`）。
但纯 JavaScript 实现的 AST 解析库（如 `marked`、`json5`）完全可以在 Worker 中顺畅运行。

---

## 追问 2：如果主线程组件销毁了，如何销毁 Worker 中的流式请求？

**回答要点**：
主线程向 Worker 发送 `{ type: 'ABORT', streamId }`，Worker 内部触发对应的 `AbortController.abort()`；若该 Worker 是一次性专属 Worker，直接调用 `worker.terminate()` 瞬间强制终结子线程。"""
    },
    {
        "id": "fe-ai-018",
        "title": "当AI流式包含自定义事件如[DONE]、[ERROR]时，前端如何解析并触发回调？",
        "difficulty": "easy",
        "question": "当AI服务端返回的流式数据包含自定义事件（如[DONE]、[ERROR]）时，前端如何解析并触发相应回调？",
        "answer": """### 一句话总结

基于 **SSE 行协议状态机**解析格式块。标准 SSE 协议中通过 `event: <name>` 或在 `data:` 内容中携带自定义标记（如 `[DONE]`）；解析器按 `\\n\\n` 切分块后提取事件名和有效载荷，利用 **发布订阅模式（EventBus）或策略映射表（Strategy Map）** 精确分发到对应事件回调。

---

### 详细回答

#### 1. 常见服务端推流格式规范
- **协议级事件（Event-Type 形式）**：
  ```http
  event: error
  data: {"code": "RATE_LIMIT", "message": "请求过于频繁"}
  ```
- **内容级控制符（OpenAI 规范形式）**：
  ```http
  data: [DONE]
  ```

#### 2. 状态机分词解析
- 每个 SSE Block 以双换行 `\\n\\n` 分隔；
- 逐行扫描：
  - 若以 `event:` 开头，记录事件名 `eventName`；
  - 若以 `data:` 开头，提取内容主体；
  - 遇到 `[DONE]` 触发 `onComplete()` 回调并主动中断流读取；
  - 解析到 `error` 立即触发 `onError(parsedData)`。

---

### 核心代码片段（极简记法）

```javascript
function handleSSELine(line, emitter) {
  if (line.startsWith('data:')) {
    const data = line.slice(5).trim();
    if (data === '[DONE]') {
      emitter.emit('complete');
      return;
    }
    try {
      const json = JSON.parse(data);
      if (json.error) emitter.emit('error', json.error);
      else emitter.emit('message', json.delta);
    } catch {
      emitter.emit('message', data);
    }
  }
}
```

---

### 面试加分项

- **处理心跳注释行（Ping / Keep-alive）**：很多网关每 15 秒推一条 `: ping` 注释防止连接断开。解析器必须能识别并静默忽略以冒号 `:` 开头的 SSE 注释行，防止将其误当成非法数据报错。""",
        "followups": """## 追问 1：如果一个 chunk 中同时收到了多行 data:（多行文本），如何处理？

**回答要点**：
根据 W3C SSE 规范，同一个事件块内的多行 `data:` 字段内容应该以换行符 `\\n` 拼接在一起，直到遇到空行 `\\n\\n` 才代表一个完整事件的结束。

---

## 追问 2：如果服务端因为超时在流中间直接掐断连接且未发送 [DONE]，前端怎么感知？

**回答要点**：
基于“空闲超时定时器（Idle Timeout）”：只要连接未收到新 Chunk 超过阈值（如 15 秒），判定为服务端静默僵死，主动抛出连接超时异常并提示重试。"""
    },
    {
        "id": "fe-ai-019",
        "title": "请设计一个流式进度估算组件动态预测AI生成剩余时间",
        "difficulty": "medium",
        "question": "请设计一个“流式进度估算”组件，根据已接收的Token数与模型速率，动态预测AI生成剩余时间。",
        "answer": """### 一句话总结

流式进度预测采用**“滑动窗口计算实时速率（Tokens/s） + 任务总预期长度预测 + 阻尼平滑算法”**。根据前序接收的 Token 计算瞬时生成速度，结合用户 Prompt 意图对总 Token 数进行经验预估，并通过平滑移动平均（EMA）消除时间预测突变跳动，给用户稳定的心理预期。

---

### 详细回答

#### 1. 为什么不能用固定倒计时？
- AI 推理受服务器负载、网络抖动、模型思考（CoT）等因素影响，速度是波动的；
- 必须基于真实网络采样的动态速度进行推算。

#### 2. 三步计算模型
1. **采样窗口与瞬时速率**：
   记录最近 $N$ 秒内接收的 Token 数量差：
   $\text{Speed} = \frac{\Delta \text{Tokens}}{\Delta \text{Time}}$
2. **总 Token 预估（经验模型）**：
   根据任务类型预估基准总长度（例如“生成代码”默认 800 Token，“摘要”默认 200 Token）；
3. **剩余时间与阻尼平滑**：
   $\text{RemainingTime} = \frac{\text{EstimatedTotal} - \text{CurrentTokens}}{\text{Speed}}$
   利用指数移动平均（EMA）过滤速度颠簸，避免倒计时从 5 秒跳到 20 秒又跳回 3 秒。

---

### 核心代码片段（极简记法）

```javascript
class TokenSpeedEstimator {
  constructor() {
    this.history = []; // [{ time, count }]
  }

  record(tokenCount) {
    const now = performance.now();
    this.history.push({ time: now, count: tokenCount });
    // 仅保留最近 3 秒的采样点
    this.history = this.history.filter(item => now - item.time <= 3000);
  }

  getSpeed() { // 计算 token / 秒
    if (this.history.length < 2) return 20; // 默认初始速率
    const first = this.history[0];
    const last = this.history[this.history.length - 1];
    const duration = (last.time - first.time) / 1000;
    return duration > 0 ? (last.count - first.count) / duration : 20;
  }
}
```

---

### 面试加分项

- **终点停滞体验优化（Zeno's Paradox 防御）**：若真实生成长度超过了预估总长度，进度条不能超过 100% 也不能卡死。应采用类似浏览器加载条的对数减速效果（逐渐逼近 99% 但永不走满），直到收到 `[DONE]` 瞬间拉满完成。""",
        "followups": """## 追问 1：大模型在吐出第一个 Token 之前有很长一段首字延迟（TTFT），这期间进度条怎么展示？

**回答要点**：
分阶段状态机：首字到达前展示“思考与检索知识库中...”并配以呼吸骨架屏或脉冲波动画，不进入具体倒计时；首字到达后（TTFT 结算）正式切入 Token 速度估算阶段。

---

## 追问 2：如何在前端快速粗略计算已接收文本的 Token 数量？

**回答要点**：
无需每次调用重量级的分词器。可采用快速经验估算规则：英文通常 4 个字符约 1 Token，中文汉字 1 个字约 1~1.5 Token。"""
    },
    {
        "id": "fe-ai-020",
        "title": "如何实现AI流式输出的语音同步朗读（TTS）与逐句对齐？",
        "difficulty": "hard",
        "question": "如何实现AI流式输出的“语音同步朗读”（TTS），确保语音与文字逐句对应，并支持暂停、跳过？",
        "answer": """### 一句话总结

语音同步朗读采用**“标点断句缓冲区（Sentence Splitter Buffer） + 音频切片队列（Audio Chunk Queue） + Web Audio API 调度”**。流式文本按标点（`。！？\n`）实时切分为完整句子，异步请求 TTS 生成音频并压入播放队列；利用音频时长与高亮索引实现文字光标跟随，配合 `AudioContext` 精准控制暂停、恢复与打断。

---

### 详细回答

#### 1. 核心难点：为什么不能逐字朗读？
- 语音合成（TTS）必须以**完整语义句子**为最小输入单位，单字合成完全没有声调抑扬顿挫，机械感极强；
- 因此必须在前端实现“流式断句缓冲”。

#### 2. 断句与异步流水线设计
1. **分句检测**：当文本流中出现中英文句末标点（`。 ! ? ; \n`）时，将前面的一整句截出作为一个独立语音任务；
2. **并发预加载**：当前句正在播放时，后台并发请求下一句的 TTS 音频流，实现无缝衔接，消除卡顿；
3. **视觉字音对齐**：根据各分句在整段文本中的起止偏移量（`startIndex`, `endIndex`），在播放该句音频时为对应 DOM 节点添加高亮背景或下划线。

---

### 核心代码片段（极简记法）

```javascript
let textBuffer = '';
const audioQueue = [];

function onTokenReceive(token) {
  textBuffer += token;
  // 匹配句子结束标点
  const match = textBuffer.match(/^([\s\S]+?[。！？；\n])([\s\S]*)$/);
  if (match) {
    const sentence = match[1];
    textBuffer = match[2]; // 剩余部分继续累加
    queueTTSPlayback(sentence);
  }
}

async function queueTTSPlayback(sentence) {
  const audioBlob = await fetchTTSAudio(sentence);
  audioQueue.push(audioBlob);
  if (!isPlaying) playNextAudio();
}
```

---

### 面试加分项

- **用户主动跳过与打断（Stop & Flush）**：用户点击“停止朗读”或直接提问新问题时，必须执行三清操作：
  1. 调用 `audioElement.pause()` 停止当前播放；
  2. 清空 `audioQueue` 队列中的所有后续音频；
  3. 通过 `AbortController` 取消正在后台请求的所有未决 TTS 网络接口。""",
        "followups": """## 追问 1：使用浏览器原生的 SpeechSynthesisUtterance（Web Speech API）有什么坑？

**回答要点**：
原生 Web Speech API 在长文本播放超过 15 秒时，Chrome 会出现静默停止播放的底层 Bug；且移动端 iOS Safari 必须由用户手势（Click）同步激活音频上下文才能发声。生产级严肃项目建议使用服务端 TTS（如 Edge-TTS 或 OpenAI TTS）。

---

## 追问 2：句与句衔接播放时有微小的静音断档，怎么消除？

**回答要点**：
利用 `Web Audio API` 的 `AudioBufferSourceNode` 双缓冲机制：在上一段音频即将结束的前 50ms（`audioContext.currentTime + duration`），预先调度启动下一段音频，实现零缝隙交叉淡入淡出（Cross-fade）。"""
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

print(f"Generated {len(DATA)} questions successfully (fe-ai-001 ~ fe-ai-020)!")
