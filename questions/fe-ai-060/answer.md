### 一句话总结

一键格式化采用**“AST 抽象语法树转换流水线 + Prettier 浏览器端运行时 + Clipboard API 多 MIME 类型写入”**。利用 `unified / remark` 将 Markdown 解析为语法树并规范化重排；代码块交给在浏览器中运行的 `prettier/standalone` 自动美化缩进；复制时同时写入 `text/html` 与 `text/plain`，支持一键无损粘贴至飞书、Notion 或 Word。

---

### 详细回答

#### 1. 痛点：为什么普通复制会导致排版全乱？
- 大模型生成的表格往往存在 Markdown 竖线未对齐、代码缺少缩进空格；
- 若只复制纯文本到剪贴板，粘贴到富文本编辑器（如微信公众号、飞书文档）时会退化为原始的 `###` 和一团乱码。

#### 2. 三步格式化技术链路
1. **代码美化（Prettier Standalone）**：
   引入浏览器专用打包的 `prettier/standalone`，对检测出的 JS/Python 代码执行格式化，对齐括号与缩进；
2. **Markdown 树状清洗（Remark Pipeline）**：
   规范列表间距、自动补齐表格缺失的表头单元格；
3. **双通道剪贴板写入（HTML + PlainText）**：
   利用 `navigator.clipboard.write([new ClipboardItem({ 'text/html': htmlBlob, 'text/plain': textBlob })])`。

---

### 核心代码片段（极简记法）

```javascript
// 一键带格式复制到剪贴板
async function copyAsRichText(markdownText, renderedHtml) {
  const textBlob = new Blob([markdownText], { type: 'text/plain' });
  const htmlBlob = new Blob([renderedHtml], { type: 'text/html' });

  // 现代 Clipboard API 同时注入富文本与纯文本
  await navigator.clipboard.write([
    new ClipboardItem({
      'text/plain': textBlob,
      'text/html': htmlBlob
    })
  ]);
}
```

---

### 面试加分项

- **Word / 邮件专用内嵌内联样式转换（Juice）**：Word 和旧版邮件客户端不支持外部 CSS 类名。在转换 HTML 时通过类似 `juice` 的轻量处理将 CSS 样式转换为 `style="..."` 行内内嵌样式，粘贴到 Word 中排版分毫不差。
