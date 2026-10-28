## 追问 1：@babel/runtime 和 @babel/plugin-transform-runtime 应该分别安装在 dependencies 还是 devDependencies？

**回答要点**：
- `@babel/plugin-transform-runtime` 是编译期执行转译的插件，安装在 **`devDependencies`**；
- `@babel/runtime` 包含转译后代码在浏览器运行时真正需要调用的辅助函数模块，必须安装在 **`dependencies`**（生产依赖）。

---

## 追问 2：为什么现在的 Vite / esbuild 项目里很少见到 babel-runtime 了？

**回答要点**：
现代浏览器已原生全面支持 ES2020+ 特性；Vite / Rollup 内部的打包器对现代语法能原生支持降级，且社区普遍采用轻量高标准的 `core-js` 直接按需注入，大幅减少了对重量级 Babel 工具链的依赖。
