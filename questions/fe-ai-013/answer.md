### 一句话总结

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

- **部分 JSON 容错解析（Partial JSON）**：针对表格或工具调用的 JSON 片段，流式传输未完成时格式是不合法的。使用 `partial-json` 或轻量堆栈状态机，能在 JSON 仅传输了一半时就能渲染出部分表格行，实现渐进式呈现。
