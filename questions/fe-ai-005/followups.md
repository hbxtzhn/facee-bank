## 追问 1：如果 Agent 执行过程中遇到需要“用户人工确认”（Human-in-the-loop）的场景，类型系统怎么扩展？

**回答要点**：
扩展一个新状态：
`| { status: 'awaiting_confirmation'; action: string; confirm: () => void; reject: (reason: string) => void }`。
在转移规则中约束其必须从 `acting`（准备调用敏感工具如支付、删除文件时）转移进入，只有用户触发 `confirm` 后才流转到实际执行，保证高风险操作的可控性。

---

## 追问 2：在复杂的生产级 Agent 工作流中，纯手写类型和使用 XState 状态机库怎么选？

**回答要点**：
轻量线性工作流手写类型即可，零依赖体积小；涉及并行分支、嵌套子状态、超时自动重试的复杂场景，选用 XState v5 状态机库，兼具类型安全与可视化排查。
