### 一句话总结

该流水线采用 **“交互式引导提交（Commitizen `git cz`） + Git 生命周期拦截（Husky） + 增量自动化修复（lint-staged）”**。开发者敲击 `cz` 通过方向键选择改动类型并填写工单号；提交触发 `pre-commit` 钩子自动格式化并修复语法隐患；`commit-msg` 钩子校验日志合法性，实现从写码到入仓全流程工业化标准化。

---

### 详细回答

#### 1. 三剑客各司其职
- **Commitizen（前端交互层）**：替代枯燥的 `git commit -m "..."`，提供友好命令行表单交互，引导输入标准 message；
- **Husky（钩子驱动层）**：在 `npm install` 时自动安装 Git 钩子脚本到 `.husky/`；
- **lint-staged（执行引擎）**：仅抓取本次提交的差异文件，自动执行 ESLint、Prettier 与单元测试。

#### 2. 标准搭建三步法
1. 安装依赖：`pnpm add -D husky lint-staged commitizen cz-conventional-changelog @commitlint/cli`；
2. 激活 Husky：`pnpm dlx husky-init`；
3. 挂载钩子：
   - `.husky/pre-commit` 写入 `npx lint-staged`；
   - `.husky/commit-msg` 写入 `npx --no -- commitlint --edit ${1}`。

---

### 核心代码片段（极简记法）

```bash
# .husky/pre-commit 钩子内容
npx lint-staged

# .husky/commit-msg 钩子内容
npx --no -- commitlint --edit "$1"
```

---

### 面试加分项

- **提交前同步执行类型检查（tsc）**：很多人忽略了 ESLint 默认不会检查静态类型错误。在 `lint-staged` 或 pre-commit 中加上 `tsc --noEmit`，坚决把任何类型不匹配的危险代码拦截在本地。
