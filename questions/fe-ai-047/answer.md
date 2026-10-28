### 一句话总结

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

- **感知系统（Awareness System）**：Yjs 不仅同步文档，还内置 Awareness 协议。可以同步展示正在协同的其他用户的光标位置、头像名称，以及 AI 正在生成中的虚拟高亮光标。
