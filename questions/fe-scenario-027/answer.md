### 一句话总结

前端预览 PDF 最主流的三种方案：**“浏览器原生容器嵌入（`<iframe / embed>`，零代码成本但无法深度定制样式）”**、**“PDF.js Canvas 渲染引擎（业界标准，高度可定制批注水印但首屏包体积大）”**、以及**“服务端转切片图片/SVG（前端纯图片展示，秒开体验最好且天然具备最强防下载防盗能力）”**。

---

### 详细回答

#### 1. 方案一：原生标签嵌入（Iframe / Embed / Object）
- `src="blob:http://.../file.pdf"` 或直接设为 PDF 地址；
- **优点**：无需加载任何第三方 JS 脚本，直接复用 Chrome/Safari 自带的 PDF 阅读器（自带打印、缩放）；
- **缺点**：样式完全无法控制、移动端 iOS Safari 经常只渲染第一页无法向下滚动、无法禁止用户右键下载。

#### 2. 方案二：Mozilla 官方 PDF.js（最强大的定制方案）
- 引入 `pdfjs-dist`；
- 在 Web Worker 中解析 PDF 二进制数据，将其每一页逐个渲染到 `<canvas>` 节点上；
- **优点**：支持在 Canvas 上方覆盖一层文字层（TextLayer）支持用户鼠标划词复制、完美支持加暗水印、签名盖章。

#### 3. 方案三：服务端转切片图片（政企/防作弊首选）
- 后端或云服务将 PDF 每一页异步转为 WebP 高清图；
- 前端只负责用虚拟列表渲染图片流；
- **优点**：首屏秒开无压力、完全防爬虫直接扒走原始 PDF 矢量文件。

---

### 核心代码片段（极简记法）

```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function renderPDFPage(pdfUrl, canvas) {
  const loadingTask = pdfjsLib.getDocument(pdfUrl);
  const pdf = await loadingTask.promise;
  const page = await pdf.getPage(1); // 提取第 1 页

  const viewport = page.getViewport({ scale: 1.5 });
  canvas.width = viewport.width;
  canvas.height = viewport.height;

  // 将 PDF 绘制至 Canvas
  await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
}
```

---

### 面试加分项

- **超大几千页 PDF 渲染不卡顿的秘诀**：在 PDF.js 方案中必须配合**“页面级虚拟列表（Virtual List）”**：只渲染当前视口可见的 2~3 页 Canvas，离开视口的页面必须调用 `page.cleanup()` 显式释放显存内存，杜绝万页文档爆掉浏览器内存。
