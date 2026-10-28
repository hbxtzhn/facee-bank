### 一句话总结

Function Calling（工具调用）的核心是**“前端向模型声明 JSON Schema 工具契约 + 模型决断调用参数 + 前端执行并将 Observation 结果回填”**。大模型本身不具备联网或运算能力，它仅根据用户意图输出结构化的 `{ name, arguments }`；前端的**工具分发中心（Tool Dispatcher）**匹配并执行本地代码，再发起二次请求将结果回传给模型输出最终结论。

---

### 详细回答

#### 1. 运作完整闭环四步走
1. **声明工具（Tools Definition）**：前端在请求头中传入工具清单及 JSON Schema 入参定义；
2. **模型决断（Decision）**：大模型判断是否需要调用工具，若需要，流式返回 `tool_calls` 片段；
3. **本地执行（Client Execution）**：前端拦截解析参数，调用真实 JS 函数（如获取经纬度、调用后端 API）；
4. **结果回填（Observation Feed）**：前端携带原始工具调用 ID 及返回的 JSON 结果再次请求大模型，由大模型总结润色输出给人看的话。

---

### 核心代码片段（极简记法）

```javascript
// 1. 声明工具定义 Schema
const tools = [{
  type: 'function',
  function: {
    name: 'calculate',
    description: '执行数学计算',
    parameters: {
      type: 'object',
      properties: { expression: { type: 'string' } },
      required: ['expression']
    }
  }
}];

// 2. 本地执行工具与回填
async function runTool(toolCall) {
  const { name, arguments: argsJson } = toolCall.function;
  const args = JSON.parse(argsJson);
  if (name === 'calculate') {
    return eval(args.expression); // 简写示意，生产应使用安全计算引擎
  }
}
```

---

### 面试加分项

- **流式参数拼接（Incremental JSON Parsing）**：大模型返回 `arguments` 是以流式字符串碎片逐步推过来的（如 `{"expr"` -> `": "1+1"` -> `"}"`）。前端在流式生成期间可以通过 `partial-json` 进行容错渐进式解析，提前在 UI 呈现“正在计算 1+1...”加载态。
