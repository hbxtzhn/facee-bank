### 一句话总结

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

- **对流式场景的高频微调（enablePatches）**：Immer 支持生成 JSON Patch。在多人实时协同对话场景中，通过 `produceWithPatches` 可以直接导出最小变更 Diff 操作包通过 WebSocket 广播，带宽占用极小。
