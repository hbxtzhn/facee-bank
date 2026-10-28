## 追问 1：PDF.js 在渲染包含特殊中文字体（如宋体/楷体）的文档时乱码发虚，为什么？

**回答要点**：
中文字体需要庞大的 CMap 映射表（Character Map）。
必须在 PDF.js 配置中正确指向外部 CMap 静态资源路径：
`cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist/cmaps/'` 并且 `cMapPacked: true`。

---

## 追问 2：PDF.js 的 Worker 脚本加载经常报错跨域怎么办？

**回答要点**：
PDF.js Worker 默认要求同源加载。
如果静态资源放在 CDN 上，可以通过将 Worker 脚本以 `Blob URL` 的形式在前端动态包装，绕过跨域限制：
`pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(blob);`。
