## 追问 1：Prettier 的 standalone 打包体积较大（包含各种语言解析器约几 MB），怎么避免拖慢主页面？

**回答要点**：
采用动态 `import()` 按需加载！
用户不点击“代码格式化”按钮，绝不下发 Prettier 资源；并且将格式化计算任务放到 Web Worker 中执行，防止几十万行超长代码格式化时冻结 UI。

---

## 追问 2：在非 HTTPS 环境或者旧浏览器下，Clipboard API 报错怎么办？

**回答要点**：
必须编写降级容灾逻辑：动态创建一个隐藏的 `textarea`，设值后调用旧版 `document.execCommand('copy')` 并捕获异常，确保在任何极端环境下复制功能不崩溃。
