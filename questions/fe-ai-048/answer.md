### 一句话总结

配置驱动工作流引擎采用**“有向无环图（DAG）JSON Schema 规范 + 节点驱动型可视化运行时（如 React Flow） + 拓扑排序执行引擎”**。前端通过 JSON 描述 `nodes`（输入、模型、分支、代码执行）与 `edges`（数据流动连线）；通过拓扑排序（Topological Sort）确定无环依赖序列，结合异步依赖注入引擎依次驱动节点求值。

---

### 详细回答

#### 1. 工作流 DAG 数据规范设计
```json
{
  "nodes": [
    { "id": "input_1", "type": "userInput" },
    { "id": "llm_1", "type": "llmNode", "config": { "model": "gpt-4o", "prompt": "{{input_1.text}}" } },
    { "id": "branch_1", "type": "conditionNode", "config": { "rules": [{ "expr": "len > 50", "target": "node_A" }] } }
  ],
  "edges": [
    { "source": "input_1", "target": "llm_1" },
    { "source": "llm_1", "target": "branch_1" }
  ]
}
```

#### 2. 前端画布可视化（React Flow）
- 将 JSON 中的 `nodes` 映射为自定义 React 组件（`LLMNodeComponent`、`CodeNodeComponent`）；
- 节点通过 Handle 锚点定义输入插槽与输出插槽；
- 画布拖拽、缩放、连线即时更新 JSON 树。

#### 3. 执行引擎：拓扑排序（Topological Sorting）与条件分支
- 检查入度为 0 的起始节点；
- 依次推进执行；遇到分支节点时，根据上一节点输出的变量值求值表达式，动态激活下游的边，未激活分支直接标记为跳过（Skipped）。

---

### 核心代码片段（极简记法）

```javascript
// 简单拓扑执行调度
async function executeDAG(nodes, edges, initialInput) {
  const context = { input: initialInput };
  // 简化的线性顺序执行（实际需根据 edge 拓扑排序）
  for (const node of nodes) {
    if (node.type === 'llm') {
      context[node.id] = await callLLM(node.config.prompt, context);
    } else if (node.type === 'condition') {
      const match = evaluateRule(node.config.rule, context);
      if (!match) break; // 中断或选择分支
    }
  }
  return context;
}
```

---

### 面试加分项

- **循环依赖环路检测（Cycle Detection）**：在用户连线建立 Edge 时，前端立即执行一次深度优先遍历（DFS）进行环路检查。若发现用户试图形成回路，禁止连接并弹出 Toast“工作流不允许形成死循环依赖”。
