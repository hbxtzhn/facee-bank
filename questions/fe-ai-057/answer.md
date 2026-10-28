### 一句话总结

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

- **白名单强制调试模式（QA Override）**：在 URL 参数中支持 `?_exp_override=ai_temp_test:B`，方便测试和产品人员一键强行指定实验分支验证效果，无需反复切换账号。
