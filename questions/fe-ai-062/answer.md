### 一句话总结

现代规范体系采用 **“ESLint Flat Config（语法与逻辑检查） + Prettier（无争议代码排版） + Commitlint（Angular 规范提交信息） + Husky / Simple-git-hooks”**。在 Git 提交（`pre-commit`）时利用 **`lint-staged` 仅对暂存区增量文件执行检查与自动修复**，在 `commit-msg` 阶段拦截不规范提交日志，实现本地秒级拦截并守死提交入口。

---

### 详细回答

#### 1. 工具分工明确（职责不越界）
- **ESLint**：管代码质量（变量未定义、禁用 `any`、React Hook 依赖项缺失、禁止在流式组件中滥用副作用）；
- **Prettier**：管代码格式（换行、单双引号、缩进、尾逗号）；
- **eslint-config-prettier**：关闭所有 ESLint 中与 Prettier 冲突的排版规则。

#### 2. Commitlint 规范（Angular 风格）
- 强制格式：`<type>(<scope>): <subject>`；
- 类型必须在：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`chore` 之中。

#### 3. 为什么必须用 lint-staged？
- 如果每次 `git commit` 都全量扫描几十万行源码，提交一次要等 30 秒；
- `lint-staged` 只针对 `git add` 暂存区里的几十行改动文件执行 Lint，0.5 秒瞬间跑完。

---

### 核心代码片段（极简记法）

```json
// package.json 配置
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "*.{ts,tsx,js}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

---

### 面试加分项

- **ESLint 9 Flat Config 演进**：指出现代项目已全面拥抱 `eslint.config.js`（扁平化配置），基于纯 ES 模块导入，废弃了旧版复杂的 `.eslintrc.js` 及其隐藏的共享插件解析 Bug，配置速度与可读性大幅提升。
