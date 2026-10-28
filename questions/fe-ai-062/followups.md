## 追问 1：如果有人在本地用 git commit --no-verify 强行跳过了本地的 Git Hooks 怎么办？

**回答要点**：
本地 Git Hooks 属于“防君子不防小人”。
团队必须在 **CI/CD 流水线（GitHub Actions / GitLab CI）上配置强制 Gatekeeper**：代码推送到远程时必须全量执行 `npm run lint` 和 `npm run type-check`，检查不通过直接锁死合并按钮（Block PR）。

---

## 追问 2：AI 自动生成（如 Copilot 补全）的大段代码经常报错违背 TS 规则，怎么快速规范？

**回答要点**：
在 VS Code 中配置 `"editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }` 与 `"editor.formatOnSave": true`，保存瞬间让工具链自动修复所有 AI 生成的细小格式缺陷。
