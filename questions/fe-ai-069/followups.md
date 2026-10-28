## 追问 1：为什么有的库（比如某些 CommonJS 模块）无法被 Vite / Rollup 有效 Tree Shaking？

**回答要点**：
Tree Shaking 强依赖于 **ES6 静态模块结构（ESM，`import` / `export`）**。CommonJS 的 `require()` 是动态求值的，编译器无法在静态分析期安全判断哪些属性未被使用；必须引入 `@rollup/plugin-commonjs` 或优先选用官方提供 ESM 构建版本的库。

---

## 追问 2：Vite 在开发环境秒级启动的底层原理是什么？

**回答要点**：
基于 **浏览器原生 ESM + esbuild 预构建**。开发模式下 Vite 根本不对业务源码进行打包混淆，而是让浏览器直接请求原生 ES 模块，由 Vite 服务端拦截按需转译单文件，时间复杂度从 $O(N)$ 下降为 $O(1)$。
