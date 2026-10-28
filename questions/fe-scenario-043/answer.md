### 一句话总结

清理无用代码采用**“静态依赖图分析工具自动化扫描 + 构建工具 Tree Shaking 生产级剔除 + CSS 纯净提取”**。JS/TS 依赖扫描首推 **`knip` 或 `ts-prune`**，精准找出未使用的导出、依赖和死文件；CSS 清理首选 **PurgeCSS** 扫描匹配类名；结合 ESLint 的 `no-unused-vars` 在写码期即时拦截。

---

### 详细回答

#### 1. JS / TS 死文件与未使用导出识别
- **`knip`（现代全能王，强烈推荐）**：
  - 扫描整个工程的 AST 依赖图谱；
  - 一键列出：从未被引入的孤儿文件、从未被导入的 `export` 函数、`package.json` 中已安装但从未被使用的 npm 包；
- **`ts-prune`**：专门扫描 TypeScript 中无用的导出。

#### 2. CSS 未使用样式清理
- **PurgeCSS / Tailwind CSS JIT**：
  - 分析所有 HTML/JSX 模板中出现的字符串词元；
  - 任何在模板中未被使用的 CSS 类名，在打包构建时物理剔除，CSS 体积直接缩减 80%。

#### 3. 生产打包层：Tree Shaking（最后一道防线）
- 保持所有依赖采用 ESM 标准（`import/export`）；
- 在 `package.json` 中配置 `"sideEffects": false` 告知打包器该模块无副作用，放心剪切。

---

### 核心代码片段（极简记法）

```bash
# 一键全面体检项目无用代码与依赖
npx knip
```

---

### 面试加分项

- **动态类名导致 PurgeCSS 误杀的避坑**：若代码中存在拼接类名如 `<div className={\`btn-\${color}\`}>`，静态分析器无法推导，会误以为 `btn-red` 未使用而强行删掉导致生产样式丢失。解决是在 PurgeCSS 配置中配置白名单（`safelist: [/^btn-/]`）。
