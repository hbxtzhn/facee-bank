## 追问 1：大模型生成的工具参数经常是序列化的 JSON 字符串，TS 如何优雅地保证解析后类型安全？

**回答要点**：
大模型输出的 `args` 往往是字符串。不要直接 `JSON.parse(rawArgs) as ExpectedType`（类型断言容易掩盖运行时解析崩溃）。
标准做法是结合运行时验证库（如 `Zod` 或 `Valibot`），通过 `schema.safeParse(JSON.parse(rawArgs))` 进行校验，失败时捕获详细报错并作为错误反馈重新喂给大模型重试。

---

## 追问 2：如果模型版本动态更新，新增了前端未知的工具类型，如何保证类型系统不直接崩溃？

**回答要点**：
在可辨识联合类型中保留一个兜底分支（Fallback Branch）：
`| { type: 'unknown_tool'; name: string; args: unknown }`，并在 switch-case 语句中使用 `default` 分支进行兜底渲染（如显示“暂不支持该组件渲染，请更新客户端”），确保向前兼容。
