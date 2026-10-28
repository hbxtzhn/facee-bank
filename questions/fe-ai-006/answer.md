### 一句话总结

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
  将公共元数据与专属联合属性进行组合，是架构设计的最佳实践。
