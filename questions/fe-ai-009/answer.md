### 一句话总结

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

- **跨项目共享元数据包**：在 Monorepo 架构中，将模型元数据提取为 `@org/model-types` 共享包，Node.js 网关层与 Web 前端共用同一份配置，模型参数升级只需发布一个单包即可全局同步。
