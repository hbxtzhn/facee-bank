### 一句话总结

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

- **充血模型（Rich Domain Model） vs 贫血模型**：指出在前端传统 Redux 中数据只是一堆纯对象（贫血），业务逻辑散落在各组件；DDD 推荐将逻辑封装在实体方法内，使核心业务与具体渲染框架（React/Vue）彻底脱钩，单测覆盖率可达 100%。
