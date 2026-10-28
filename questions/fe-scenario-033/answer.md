### 一句话总结

同源策略（SOP）的核心是**“限制跨源脚本对隐私数据的任意读取，而非限制跨源资源的被动引用与加载”**。HTML 原生标签（`<script src>`、`<link href>`、`<img src>`）在设计之初就天然允许跨域嵌入引用资源；只要当前页面的 JS 无法跨域窥探并读取到该资源内部的明文内存数据，就不会违背安全边界。

---

### 详细回答

#### 1. 跨域嵌入（Embedding） vs 跨域读取（Reading）
- **允许跨域嵌入（Safe）**：
  - `<script src="...">`：浏览器仅负责下载并在当前作用域中执行代码，普通 JS 无法读取脚本文件的文本源码字符串；
  - `<img src="...">`：浏览器仅负责解码并在屏幕上绘制图像，JS 无法直接读取其二进制像素；
  - `<link rel="stylesheet">`：仅应用样式规则。
- **限制跨域读取（Dangerous）**：
  - `fetch` / `XMLHttpRequest` 发起的数据请求；
  - Canvas 通过 `getImageData()` 窃取跨域图片的像素；
  - 读取跨域 `iframe` 内部的 `contentWindow.document`。

#### 2. CDN 静态资源的设计契约
- CDN 承载的 JS、CSS 和图片是面向全网公开的公共资产，不存在针对特定用户的 Cookie 隐私会话；
- 因此通过 `<script>` 引用完全安全。

---

### 核心代码片段（极简记法）

```html
<!-- ✅ 天然放行跨域引用 -->
<script src="https://cdn.bootcdn.net/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<img src="https://third-party-cdn.com/logo.png" />

<!-- ❌ 若直接用 fetch 拉取且 CDN 未配置 CORS，会被同源策略拦截报错 -->
<script>
  fetch('https://third-party-cdn.com/data.json'); // 报错跨域！
</script>
```

---

### 面试加分项

- **Canvas 跨域“画布污染”（Tainted Canvas）**：如果用 JS 把跨域 CDN 上的图片画入 Canvas，随后调用 `canvas.toDataURL()` 尝试导出图片，浏览器会立即抛出安全异常报错。必须在 `<img>` 标签加上 `crossOrigin="anonymous"` 且 CDN 配置了 CORS 响应头，消除画布污染。
