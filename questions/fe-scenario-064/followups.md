## 追问 1：script 标签的 defer 和 async 到底有什么区别？

**回答要点**：
- 两者都是异步并行下载脚本、不阻塞 HTML 解析；
- `defer`：脚本下载完成后**绝不立即执行**，而是静静等待整棵 DOM 树全部解析完毕，且严格按照标签在 HTML 中的书写先后顺序串行执行；
- `async`：只要脚本一旦下载完成，**立即强行中断 HTML 解析并立刻插队执行**，谁先下完谁先执行，顺序完全随机。

---

## 追问 2：什么是关键渲染路径（Critical Rendering Path）？

**回答要点**：
指浏览器从接收 HTML、CSS、JS 字节流到最终在屏幕上绘制出物理像素的完整五步过程：
`构建 DOM 树 -> 构建 CSSOM 树 -> 合并生成 Render Tree -> 布局（Layout/Reflow） -> 绘制（Painting/Composite）`。
