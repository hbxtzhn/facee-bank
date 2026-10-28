## 追问 1：为什么 Vite 在开发环境不直接让浏览器加载裸模块（如 import React from 'react'）？

**回答要点**：
因为浏览器原生 ESM 不支持裸模块导入路径（Bare Module Imports），直接写 `import React from 'react'` 会报错；
Vite 在预构建阶段会重写路径为带有具体相对路径的 `/node_modules/.vite/deps/react.js`。

---

## 追问 2：热模块替换（HMR）在 Vite 中为什么能做到恒定毫秒级更新？

**回答要点**：
在 Webpack 中热更新需要重新计算整个关联的 Chunk 链；
而在 Vite 中，由于模块天然解耦，当修改一个文件时，Vite 只需要精确使当前这一个模块的原生浏览器缓存失效，并通知浏览器重新发起该单文件的 HTTP 请求，复杂度恒定为 $O(1)$。
