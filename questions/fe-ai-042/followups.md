## 追问 1：前端代码如果误引入了 Node.js 中间层的后端私密依赖（如包含数据库密码的模块），如何检测？

**回答要点**：
通过 ESLint 配置规则（如 `import/no-restricted-paths`）或 TS Project References 进行依赖层级隔离，严禁 `apps/web` 跨目录导入任何属于 `apps/gateway` 内部的源码。

---

## 追问 2：团队规模变大后，Monorepo 安装依赖或 CI 速度变慢怎么优化？

**回答要点**：
1. 开启 **Turborepo 远程缓存（Remote Cache）**；
2. 开启 pnpm 的 content-addressable store 硬链接机制；
3. CI 中配置针对受影响文件（`turbo run test --filter=...[origin/main]`）的增量测试与构建。
