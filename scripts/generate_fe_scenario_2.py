import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-scenario-026",
        "title": "babel-runtime作用是啥？",
        "difficulty": "medium",
        "question": "babel-runtime的作用是什么？它与@babel/polyfill有什么区别？为什么在库开发中推荐使用？",
        "answer": """### 一句话总结

`@babel/plugin-transform-runtime` 配合 `@babel/runtime` 核心解决两大痛点：**“公共辅助函数抽离复用以缩小体积”**与**“无全局变量污染的沙箱 Polyfill”**。它将每个文件里重复生成的 `_extend`、`_classCallCheck` 等内联助手函数提取为模块导入，并使用局部重命名的别名引入 Promise/Symbol，避免污染全局命名空间，是开发通用 NPM 库的行业标配。

---

### 详细回答

#### 1. 痛点一：辅助函数重复注入（包体积膨胀）
- 默认情况下，Babel 在转译 ES6 `class` 时，会在每个打包文件中都硬编码一份几十行的辅助代码 `function _classCallCheck(...)`；
- 如果项目有 200 个文件，就会被重复拷贝 200 次；
- **解决**：transform-runtime 将其替换为统一从 `@babel/runtime/helpers/classCallCheck` 导入，全包只保留一份单例。

#### 2. 痛点二：全局 Polyfill 污染（库开发的大忌）
- `@babel/polyfill`（已废弃）采用的是在全局 `window` 上直接无脑挂载 `window.Promise = ...`；
- 如果你在开发一个工具库（SDK）给别人用，你的 SDK 偷偷篡改了用户的全局 Promise，极易导致宿主应用出现不可预知的冲突 Bug；
- **解决**：runtime 插件采用沙箱化局部替换：`import _Promise from '@babel/runtime-corejs3/core-js-stable/promise'`，在局部作用域内安全运行，完全不碰全局变量。

---

### 核心代码片段（极简记法）

```json
// .babelrc 配置生产级 transform-runtime
{
  "plugins": [
    [
      "@babel/plugin-transform-runtime",
      {
        "corejs": 3,       // 提供不污染全局的 API Polyfill
        "helpers": true,     // 抽离重复的 helper 辅助函数
        "regenerator": true // 抽离 async/await 运行时生成器
      }
    ]
  ]
}
```

---

### 面试加分项

- **应用开发 vs 库开发的 Polyfill 选型**：指出在业务应用（Application）开发中，通常推荐 `@babel/preset-env` 搭配 `useBuiltIns: 'usage'`，直接按需按浏览器目标兼容性全局填充；而在基础库/组件库（Library）开发中，坚决强制使用 `transform-runtime` 保持纯洁无污染。""",
        "followups": """## 追问 1：@babel/runtime 和 @babel/plugin-transform-runtime 应该分别安装在 dependencies 还是 devDependencies？

**回答要点**：
- `@babel/plugin-transform-runtime` 是编译期执行转译的插件，安装在 **`devDependencies`**；
- `@babel/runtime` 包含转译后代码在浏览器运行时真正需要调用的辅助函数模块，必须安装在 **`dependencies`**（生产依赖）。

---

## 追问 2：为什么现在的 Vite / esbuild 项目里很少见到 babel-runtime 了？

**回答要点**：
现代浏览器已原生全面支持 ES2020+ 特性；Vite / Rollup 内部的打包器对现代语法能原生支持降级，且社区普遍采用轻量高标准的 `core-js` 直接按需注入，大幅减少了对重量级 Babel 工具链的依赖。"""
    },
    {
        "id": "fe-scenario-027",
        "title": "如何实现预览PDF文件？",
        "difficulty": "medium",
        "question": "在前端如何实现 PDF 文件的高性能在线预览？有哪些方案及各自的优缺点？",
        "answer": """### 一句话总结

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

- **超大几千页 PDF 渲染不卡顿的秘诀**：在 PDF.js 方案中必须配合**“页面级虚拟列表（Virtual List）”**：只渲染当前视口可见的 2~3 页 Canvas，离开视口的页面必须调用 `page.cleanup()` 显式释放显存内存，杜绝万页文档爆掉浏览器内存。""",
        "followups": """## 追问 1：PDF.js 在渲染包含特殊中文字体（如宋体/楷体）的文档时乱码发虚，为什么？

**回答要点**：
中文字体需要庞大的 CMap 映射表（Character Map）。
必须在 PDF.js 配置中正确指向外部 CMap 静态资源路径：
`cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist/cmaps/'` 并且 `cMapPacked: true`。

---

## 追问 2：PDF.js 的 Worker 脚本加载经常报错跨域怎么办？

**回答要点**：
PDF.js Worker 默认要求同源加载。
如果静态资源放在 CDN 上，可以通过将 Worker 脚本以 `Blob URL` 的形式在前端动态包装，绕过跨域限制：
`pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(blob);`。"""
    },
    {
        "id": "fe-scenario-028",
        "title": "如何在划词选择的文本上添加右键菜单？",
        "difficulty": "medium",
        "question": "如何在划词选择的文本上添加右键菜单（鼠标滑动选择一组字符后，点击右键或弹出悬浮操作条）？",
        "answer": """### 一句话总结

划词菜单的核心是**“利用 `window.getSelection()` 获取当前选区对象与坐标范围，并在 `contextmenu`（右键）或 `mouseup`（划选完毕）事件中弹出绝对定位操作框”**。通过 `selection.getRangeAt(0).getBoundingClientRect()` 获取选中文字在视口中的精确位置，结合 `e.preventDefault()` 阻止浏览器默认右键菜单，实现高仿 Medium / 飞书的划词悬浮菜单。

---

### 详细回答

#### 1. 核心 API 链路
1. **`window.getSelection()`**：获取浏览器全局的 Selection 选区对象；
2. **`selection.toString().trim()`**：判定用户是否真正选中了有效文字（若为空字符串说明用户只是普通点击，不弹菜单）；
3. **`range.getBoundingClientRect()`**：提取选中文字矩形区域的 `top`, `bottom`, `left`, `width` 物理视口像素坐标；
4. **阻止原生右键**：在 `contextmenu` 事件中调用 `e.preventDefault()`。

#### 2. 定位计算逻辑
- 弹窗菜单通常居中展示在选中文字的上方：
  - `menuTop = rect.top + window.scrollY - menuHeight - 8;`
  - `menuLeft = rect.left + window.scrollX + (rect.width / 2) - (menuWidth / 2);`

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('contextmenu', (e) => {
  const selection = window.getSelection();
  const selectedText = selection.toString().trim();

  if (selectedText) {
    e.preventDefault(); // 阻止浏览器原生右键菜单
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // 绝对定位弹出自定义划词菜单
    showCustomMenu({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
      text: selectedText
    });
  }
});
```

---

### 面试加分项

- **边界碰撞保护（Viewport Collision）**：如果用户划选的是屏幕最顶部或最左侧的文字，菜单如果继续往上弹会被浏览器窗口截断隐藏。必须编写边界碰撞检测：若 `rect.top < menuHeight`，自动反转菜单弹出方向（翻转显示在选中文字的下方）。""",
        "followups": """## 追问 1：用户点击页面其他空白区域时，如何让划词菜单自动消失？

**回答要点**：
在全局 `document` 监听 `mousedown` 事件，通过 `menuRef.contains(e.target)` 判断点击是否落在菜单外部；若在外部，立即销毁或隐藏菜单，恢复纯净状态。

---

## 追问 2：如果用户划词跨越了多个不同的段落（包含多个 <p> 和 <div>），坐标怎么算？

**回答要点**：
`range.getBoundingClientRect()` 会返回包裹所有跨行跨段落文字的**“外接最大凸多边形矩形”**；
如果需要对每一行分别高亮，可调用 `range.getClientRects()`，它会返回每一行文字独立的精确小矩形数组。"""
    },
    {
        "id": "fe-scenario-029",
        "title": "富文本里面，是如何做到划词的？",
        "difficulty": "hard",
        "question": "富文本编辑器里面，是如何做到划词的？底层数据结构（Range / Selection）与选区映射原理是什么？",
        "answer": """### 一句话总结

富文本划词底层的物理层依赖浏览器原生的 **`Selection`（选区集合）与 `Range`（连续文本范围）对象**，其在逻辑层抽象为**“基于虚拟文档模型（如 Slate / ProseMirror 的绝对字符偏移量）的精准路径定位”**。通过获取起止文本节点的 `(anchorNode, anchorOffset)` 到 `(focusNode, focusOffset)`，将物理 DOM 节点映射为富文本 AST 树上的数据范围，实现精准划词高亮与样式包裹。

---

### 详细回答

#### 1. 浏览器原生选区三剑客
- **`Selection`**：用户选中的整体表示（`window.getSelection()`）；
- **`Anchor（锚点）`**：鼠标按下的起始位置（包含对应 DOM 文本节点与字符偏移量）；
- **`Focus（焦点）`**：鼠标释放或拖拽移动的终点（支持从右往左反向划选）；
- **`Range`**：一个规范化的、始终由左向右包含 `startContainer` 到 `endContainer` 的文本片段。

#### 2. 原生 DOM 划词修改样式的传统做法（DOM 操作）
- 获取 `range = selection.getRangeAt(0)`；
- 创建包裹元素：`const span = document.createElement('span'); span.className = 'highlight';`；
- 执行环绕：`range.surroundContents(span)`。
- **致命缺陷**：若用户划选跨越了标签边界（比如选了半个加粗段落和半个普通段落），`surroundContents` 会直接抛出 DOMException 异常崩溃！

#### 3. 现代富文本引擎（ProseMirror / Slate）的抽象映射
- **绝不直接操作不可靠的 DOM Range！**
- 内部建立严格的线性坐标系：文档中每一个字符对应一个单调递增的绝对位置索引（Position）；
- 划选时将 DOM Range 转换为内部状态 `{ from: 42, to: 88 }`；
- 在纯数据层面生成一条不可变的 `Transaction`，重新渲染出合法的虚拟 DOM 树，彻底消除跨标签撕裂问题。

---

### 核心代码片段（极简记法）

```javascript
// 获取划词选区与位置
const selection = window.getSelection();
if (selection.rangeCount > 0) {
  const range = selection.getRangeAt(0);
  console.log('起始节点:', range.startContainer, '起始偏移:', range.startOffset);
  console.log('结束节点:', range.endContainer, '结束偏移:', range.endOffset);
}
```

---

### 面试加分项

- **划词状态的持久化与恢复（Highlight Persistence）**：如果需要将用户的划词高亮保存到后端并在下次打开时还原，绝不能存易变的 DOM XPath。应结合字符绝对偏移（Character Offsets）或使用 DOM 序列化开源标准库（如 `web-highlighter`），记录前缀锚文本（Contextual Anchor）做容错模糊对齐。""",
        "followups": """## 追问 1：如果划选时从右向左划，Selection 和 Range 的表现有何不同？

**回答要点**：
`Selection` 能够区分划选方向：反向划选时 `anchorOffset > focusOffset`，`selection.isCollapsed` 为 false；
而 `Range` 永远会被浏览器自动归一化为正向：`range.startOffset` 永远处于左侧较小值，`endOffset` 处于右侧较大值。

---

## 追问 2：如何在输入框（<input> 或 <textarea>）中实现代码选区或光标位置读取？

**回答要点**：
表单输入元素不产生标准 DOM Range。
必须直接通过表单专有原生属性：`input.selectionStart` 与 `input.selectionEnd` 获取光标字符下标，并通过 `input.setSelectionRange(start, end)` 进行程序化选区控制。"""
    },
    {
        "id": "fe-scenario-030",
        "title": "如何做好前端监控方案？",
        "difficulty": "hard",
        "question": "如何设计并落地一套工业级的前端全方位监控方案？包含哪些维度？",
        "answer": """### 一句话总结

一套完备的前端监控体系必须覆盖四大核心支柱：**“错误监控（JS 运行时报错、Promise 未捕获、静态资源加载失败、接口 4xx/5xx） + 性能监控（Web Vitals 核心指标、长任务） + 用户行为监控（PV/UV、点击漏斗、停留时长、录屏回放） + 业务监控（支付转化率、白屏探测）”**。配合客户端 SDK 自动捕获、采样上报以及后端的异常聚类报警，形成闭环保障体系。

---

### 详细回答

#### 1. 支柱一：全方位异常捕获网
- **同步与异步代码报错**：`window.onerror`；
- **未捕获的 Promise 报错**：`window.addEventListener('unhandledrejection')`；
- **资源加载 404 捕获**：`window.addEventListener('error', fn, true)`（注意：必须在捕获阶段监听，因为资源错误不冒泡）；
- **React 组件树级崩溃**：`componentDidCatch`（ErrorBoundary）；
- **接口异常**：Axios / Fetch 全局拦截器采集 HTTP 状态码与耗时。

#### 2. 支柱二：白屏自动探测（极关键指标）
- 页面加载完成后，利用 `document.elementsFromPoint(x, y)` 采样屏幕关键 9 个十字点；
- 若采出来的节点全都是 `html`、`body` 或 `#app:empty` 容器，判定为白屏故障，立即触发紧急告警。

#### 3. 支柱三：上报机制与数据治理
- **通道选型**：优先使用 `navigator.sendBeacon` 或 `fetch keepalive`；
- **频次治理**：合并批处理（每 5 秒发送一次）、抽样率控制（错误 100% 上报，PV 5% 采样）；
- **数据关联**：全链路统一注入 `trace_id`、`session_id`、`app_version` 与用户信息。

---

### 核心代码片段（极简记法）

```javascript
// 全局异常捕获核心防线
window.addEventListener('error', (event) => {
  // 区分资源加载错误与普通 JS 报错
  const isResource = event.target && (event.target.src || event.target.href);
  reportError({
    type: isResource ? 'RESOURCE_ERROR' : 'JS_ERROR',
    message: event.message || '资源加载失败',
    target: isResource ? (event.target.src || event.target.href) : null,
    stack: event.error?.stack
  });
}, true); // 捕获阶段必填！

window.addEventListener('unhandledrejection', (e) => {
  reportError({ type: 'PROMISE_ERROR', reason: e.reason });
});
```

---

### 面试加分项

- **SourceMap 生产安全治理**：指出生产环境打包生成的 `.map` 文件**绝对禁止上传到公开 CDN**（防止竞品和黑客直接逆向阅读完整源代码）。应在 CI 构建时将 SourceMap 私密上传至企业内网自建的 Sentry / 监控服务器，在内网服务端后台完成代码行号还原后，本地立即彻底删除 map 文件。""",
        "followups": """## 追问 1：监控 SDK 自身如果写出 Bug 报错了，会不会把宿主主业务搞死？

**回答要点**：
必须设计“看门狗保护”：
1. SDK 内部所有代码必须严密包裹在 `try...catch` 中；
2. 严禁在 SDK 的报错处理逻辑内部再次触发上报报错（防止死循环发包导致浏览器崩溃）。

---

## 追问 2：Script error（跨域脚本错误）拿不到具体的错误堆栈，只显示 Script error. 怎么解？

**回答要点**：
1. 在引入该跨域 JS 的 `<script>` 标签上添加 `crossorigin="anonymous"` 属性；
2. 静态资源 CDN 响应头必须返回 `Access-Control-Allow-Origin: *`，两项齐备浏览器才会向 JS 暴露详细堆栈。"""
    },
    {
        "id": "fe-scenario-031",
        "title": "如何标准化处理线上用户反馈的问题？",
        "difficulty": "medium",
        "question": "当线上收到用户反馈“点按钮没反应”等模糊客诉时，前端团队如何标准化排查、复现与闭环处理？",
        "answer": """### 一句话总结

标准化客诉处理遵循**“现场精准复原（TraceID / 用户 ID 联动日志捞取） $\to$ 最小用例复现 $\to$ 热修发版灰度 $\to$ 复盘建立防线”**的闭环机制。通过用户提供的账号或报错提示中的关联码，在监控后台拉取该用户发生操作时的**设备环境、接口状态码与行为轨迹（Breadcrumbs / 录屏）**，杜绝无头苍蝇式盲猜，将偶发客诉转化为确定性技术 Bug。

---

### 详细回答

#### 1. 第一步：信息采集与一键排障入口
- 在产品帮助中心设计“一键上传诊断日志”按钮；
- 界面报错弹窗展示短关联码（如 `错误代码: #ERR_9527`，底层映射为该条请求的 `traceId`）；
- 收集元数据：User ID、设备型号、OS 版本、App 内置浏览器版本、网络运营商（4G/Wi-Fi）。

#### 2. 第二步：日志与现场秒级检索
- 根据 TraceID 在日志中枢（Kibana / SLS / Sentry）过滤：
  1. 查看当时是否有 4xx/5xx 网络接口挂起超时；
  2. 查看控制台是否有 JS 未捕获崩溃异常；
  3. 查看前序是否有 LocalStorage 满载配额报错。

#### 3. 第三步：灰度验证与热修复
- 修复代码后先在灰度通道验证，确认客诉用户反馈正常后全量发版；
- 补充对应的自动化单元测试或 E2E 用例，杜绝同类故障在下个版本死灰复燃。

---

### 核心代码片段（极简记法）

```javascript
// 报错界面向用户展示一键可复制的排障工单号
function renderErrorDialog(errorTraceId) {
  return `
    <div class="error-dialog">
      <p>抱歉，遇到意外故障</p>
      <p>排障代码: <code>${errorTraceId}</code></p>
      <button onclick="copyAndFeedback('${errorTraceId}')">复制并联系客服</button>
    </div>
  `;
}
```

---

### 面试加分项

- **前端健康度自动化大盘（SLA 机制）**：将客诉处理升级为组织机制：制定团队质量红线（如 P0 故障 15 分钟响应、1 小时热修交付；全站 JS 错误率维持在 0.1% 以下），每月定期举行故障复盘会（Post-mortem）。""",
        "followups": """## 追问 1：用户使用的是微信内置浏览器，反馈有 Bug 但开发在手机上无法复现，怎么远程调试？

**回答要点**：
通过微信官方提供的 `debugx5.qq.com` 开启移动端 vConsole 调试面板，让用户点击开启后直接截取控制台面板截图，或者利用工具库（如 `chii` / `spy-debugger`）实现移动端远程无线真机调试。

---

## 追问 2：如果客诉用户是因为使用了过旧的手机浏览器导致语法不兼容白屏，如何处理？

**回答要点**：
在 `index.html` 的 `<head>` 中嵌入一段未经转译的最简原生内联嗅探脚本：检测关键特性（如 `window.Promise`、`window.fetch`）；若不支持，直接展示友好的静态升级提示遮罩：“您的浏览器版本过低，请升级后访问”，阻止加载主 bundle。"""
    },
    {
        "id": "fe-scenario-032",
        "title": "px如何转为rem？",
        "difficulty": "easy",
        "question": "移动端适配中，px是如何转换为rem的？底层计算原理与工程自动化配置（PostCSS）是怎样的？",
        "answer": """### 一句话总结

rem 是相对于**页面根元素（`<html>`）的 `font-size` 的相对单位**。底层原理是**“动态根据屏幕宽度等比例修改根字号，使 1rem 始终代表屏幕宽度的固定百分比”**；在现代前端工程中，严禁人工口算，全部通过 **`postcss-pxtorem` 插件在打包编译期将 CSS 中的 px 自动转换为 rem**，开发者只需按设计稿像素无脑写 px。

---

### 详细回答

#### 1. 底层换算公式
- 假设设计稿宽度为 375px，约定标准根字号为 37.5px（即 $1\text{rem} = 37.5\text{px}$，正好是设计稿宽度的 1/10）；
- 元素在设计稿上量出宽度为 150px，则换算为：$150 / 37.5 = 4\text{rem}$；
- 当页面运行在 414px 宽度的手机上时，通过 JS 将根字号动态更新为 $414 / 10 = 41.4\text{px}$；
- 此时元素在界面上的渲染宽度为：$4\text{rem} \times 41.4\text{px} = 165.6\text{px}$，实现了完美的等比自适应放大！

#### 2. 工程化自动化：postcss-pxtorem
- 开发者在代码里直接写：`width: 150px;`；
- PostCSS 自动转译为：`width: 4rem;`。

---

### 核心代码片段（极简记法）

```javascript
// postcss.config.js 自动化转换配置
module.exports = {
  plugins: {
    'postcss-pxtorem': {
      rootValue: 37.5, // 对应设计稿基准字号 (375宽度的1/10)
      propList: ['*'], // 所有 CSS 属性均转换
      selectorBlackList: ['.ignore'] // 忽略特定类名转换
    }
  }
};
```

---

### 面试加分项

- **纯 CSS 的 vw 方案替代 rem**：指出 rem 依赖 JS 动态修改 DOM 容易引起首屏字体闪烁。现代移动端推荐更直接的 **`postcss-px-to-viewport` 方案**：将 px 直接转为 `vw`，完全不需要执行任何 JS 代码，纯 CSS 实现原生视口等比缩放。""",
        "followups": """## 追问 1：有时候希望某些属性（比如边框 1px border）保持绝对物理 1 像素，不要被转成 rem，怎么配置？

**回答要点**：
1. 在样式属性中书写大写字母单位，如 `border: 1PX solid #ccc;`（PostCSS 默认只匹配小写 px，大写会被智能跳过）；
2. 或者在插件配置的 `propList` 中排除 `border` 相关属性。

---

## 追问 2：用户的安卓系统设置了“超大辅助字体”，导致计算出来的 rem 界面排版全乱挤爆，怎么防守？

**回答要点**：
安卓微信等内置环境会强行放大网页根字号。
防守代码：在设置完 `html.style.fontSize` 后，立即通过 `window.getComputedStyle(document.documentElement).fontSize` 测量实际渲染字号；若发现实际字号 > 设定字号，除以该缩放比例做反向除法抵消。"""
    },
    {
        "id": "fe-scenario-033",
        "title": "浏览器有同源策略，为何CDN请求资源时不会有跨域限制？",
        "difficulty": "medium",
        "question": "浏览器有同源策略，但是为何cdn请求资源（图片、脚本、样式表）的时候不会有跨域限制？",
        "answer": """### 一句话总结

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

- **Canvas 跨域“画布污染”（Tainted Canvas）**：如果用 JS 把跨域 CDN 上的图片画入 Canvas，随后调用 `canvas.toDataURL()` 尝试导出图片，浏览器会立即抛出安全异常报错。必须在 `<img>` 标签加上 `crossOrigin="anonymous"` 且 CDN 配置了 CORS 响应头，消除画布污染。""",
        "followups": """## 追问 1：JSONP 能够实现跨域通信，底层就是利用了这个特性吗？

**回答要点**：
完全正确！
JSONP 本质就是动态创建一个 `<script src="http://api.com?callback=handleData">` 标签利用天然跨域漏洞，服务端返回包裹了数据的 JS 函数调用字符串（`handleData({ ... })`），浏览器下载后立即执行回调传参。

---

## 追问 2：既然 script 标签天然跨域，黑客能否通过 script 标签窃取我的内部私密接口数据？

**回答要点**：
这也是为什么**私密业务 API 绝对不能返回纯合法 JS 语句！**
如果接口返回标准 JSON（如 `{"secret": 123}`），黑客用 `<script src="/api/secret">` 引入时，浏览器会将其当作非法语法直接报错抛出，黑客依然无法提取其中的数据。"""
    },
    {
        "id": "fe-scenario-034",
        "title": "cookie可以实现不同域共享吗？",
        "difficulty": "medium",
        "question": "Cookie可以实现不同域共享吗？二级域名共享与完全跨域共享分别该怎么做？",
        "answer": """### 一句话总结

**同一个父级域名下的不同子域名可以无缝共享（通过指定 `Domain=.example.com`）；而完全不同的顶级域名（如 a.com 与 b.com）由于浏览器沙箱安全隔离，在底层协议上绝对无法直接共享读取 Cookie**。跨完全不同域的会话共享必须借助 **SSO 单点登录（CAS / OAuth 重定向授权并携带 Token）** 或 **中间页借助 `postMessage` + `iframe` 跨源传输**。

---

### 详细回答

#### 1. 场景一：二级子域名共享（同主域）
- 场景：`oa.baidu.com` 和 `tieba.baidu.com`；
- **配置规则**：
  写入 Cookie 时显式设置 `Domain=.baidu.com; Path=/`；
  此时只要是以 `.baidu.com` 结尾的所有二级、三级子域名，在发请求时均会自动携带该 Cookie。

#### 2. 场景二：完全跨域（a.com 与 b.com）
- **协议死限制**：浏览器内核强制禁止 `a.com` 读取属于 `b.com` 的 Cookie（同源策略最核心防线，若能共享则黑客可秒级窃取全网登录态）；
- **成熟工程解法（SSO 单点登录）**：
  1. 访问 `b.com` 时发现未登录，自动 302 重定向到统一认证中心 `sso.com`；
  2. `sso.com` 验证自身 Cookie 发现已登录，签发一个带有一次性票据的授权码（Ticket）；
  3. 重定向回 `b.com?ticket=xyz`；
  4. `b.com` 后端用 ticket 兑换会话，并在 `b.com` 自身的域名下独立种下本站 Cookie。

---

### 核心代码片段（极简记法）

```javascript
// 子域名共享 Cookie 规范设置
document.cookie = "token=xyz123; Domain=.company.com; Path=/; Secure; SameSite=Lax";
```

---

### 面试加分项

- **跨域 iframe 写入 Cookie 的第三方限制（CHIPS / Partitioned Cookies）**：Chrome 正在全面废除传统的第三方跨站 Cookie（Third-Party Cookies）。如果必须在跨域 iframe 中嵌入携带自身 Cookie，必须声明新特性属性 `Partitioned`（独立分区 Cookie），否则会被新版 Chrome 直接丢弃。""",
        "followups": """## 追问 1：前端如果在 a.com 的 JS 里手动写 document.cookie = "token=123; Domain=b.com"，会发生什么？

**回答要点**：
浏览器会直接静默忽略该操作（写入失败）！
浏览器安全机制严格规定：页面只能将 Cookie 的 Domain 设置为当前域名本身或其公共父级域名，禁止向任何无关域名种 Cookie。

---

## 追问 2：SameSite 属性设为 Strict、Lax、None 分别代表什么？

**回答要点**：
- `Strict`：最严格，任何第三方网站发起的请求（包括点击超链接）绝不携带该 Cookie；
- `Lax`（现代默认）：导航类跨站（如直接点击 a 链接跳转）放行携带，跨站 POST/iframe 请求禁止携带；
- `None`：任何跨站请求均可携带，但必须同时开启 `Secure`（必须走 HTTPS）。"""
    },
    {
        "id": "fe-scenario-035",
        "title": "axios是否可以取消请求？",
        "difficulty": "medium",
        "question": "Axios 是否可以取消请求？底层原理是什么？有哪些实战业务应用场景？",
        "answer": """### 一句话总结

Axios **完全支持取消请求**。现代 Axios（v0.22.0+）全面拥抱浏览器原生标准的 **`AbortController` 与 `AbortSignal`**（已废弃旧版自研的 `CancelToken`）；底层通过将信号源传递给底层的 XMLHttpRequest 的 `xhr.abort()` 或 Fetch API，瞬间从浏览器网络层强行切断 TCP 数据流传输，并使对应的 Promise 进入 reject 异常分支。

---

### 详细回答

#### 1. 现代标准方案：AbortController
- 创建控制器：`const controller = new AbortController();`；
- 发起请求时透传信号：`axios.get('/api/search', { signal: controller.signal })`；
- 随时随刻取消：`controller.abort()`；
- 捕获异常：通过 `axios.isCancel(err)` 或 `err.name === 'CanceledError'` 判定该错误由主动取消引起，无需向用户弹出报错。

#### 2. 常见核心业务场景
- **Tab 标签快速切换（防竞态条件）**：用户从 Tab A 点击切换到 Tab B，必须立即取消 Tab A 尚未返回的网络请求，防止 Tab A 的慢数据晚于 Tab B 返回而篡改界面；
- **搜索输入联想框（弃旧迎新）**；
- **页面组件卸载（Unmount）**：在 React `useEffect` 清理函数中取消请求，防止组件销毁后仍在内存中触发 `setState` 内存泄漏警告。

---

### 核心代码片段（极简记法）

```javascript
const controller = new AbortController();

axios.get('/api/large-data', { signal: controller.signal })
  .catch(err => {
    if (axios.isCancel(err)) {
      console.log('请求被成功主动取消:', err.message);
    }
  });

// 用户点击取消按钮或离开页面
controller.abort();
```

---

### 面试加分项

- **服务端是否感知取消？** 必须指出：前端调用 `abort()` 仅代表**“客户端切断了 TCP 连接并不再接收后续 Response”**。如果请求已经到达服务端并开始执行繁重的数据库写事务，服务端若未配置断开监听，依然会默默把操作执行完毕。取消前端请求不能百分百阻止服务端已触发的逻辑。""",
        "followups": """## 追问 1：为什么 Axios 废弃了之前的 CancelToken？

**回答要点**：
`CancelToken` 是早年基于提案（TC39 已废弃提案）的非标准实现；而 `AbortController` 已经成为 W3C / WHATWG 官方认可的标准 Web API（Node.js、Fetch、Web Worker 通用），顺应行业标准统一生态。

---

## 追问 2：一个 AbortController 实例可以同时取消多个并发的请求吗？

**回答要点**：
完全可以！
只需将同一个 `controller.signal` 传递给 10 个不同的 Axios 请求；一旦调用 `controller.abort()`，所有绑定了该信号的请求会瞬间被一次性批量全部掐断。"""
    },
    {
        "id": "fe-scenario-036",
        "title": "前端如何实现折叠面板效果？",
        "difficulty": "medium",
        "question": "前端如何实现折叠面板（Accordion 手风琴）效果？有哪些纯CSS与JS方案？如何实现丝滑的高度动画？",
        "answer": """### 一句话总结

折叠面板的核心难点是**“从 `height: 0` 到自适应内容 `height: auto` 之间无法直接应用 CSS transition 动画”**。最现代的纯 CSS 方案是采用 **CSS Grid 的 `grid-template-rows: 0fr -> 1fr` 魔法过渡**；JS 方案采用获取 `scrollHeight` 动态赋固定像素高；语义化场景亦可直接利用 HTML5 原生 `<details>` 与 `<summary>` 标签零 JS 实现。

---

### 详细回答

#### 1. 传统高度动画的痛点
- 如果写 `transition: height 0.3s; height: 0 -> height: auto;`，浏览器**根本不会产生任何动画**，而是生硬地瞬间闪现；
- 旧解法是设一个很大的 `max-height: 500px`，但会导致展开和收起时动画速度极其不匀速、存在明显滞后卡顿。

#### 2. 现代纯 CSS 最优解：CSS Grid 0fr 转 1fr
- 外层包裹容器设为 Grid 布局：
  ```css
  .accordion-content {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.3s ease-out;
  }
  .accordion-content.expanded {
    grid-template-rows: 1fr; /* 丝滑过渡到内容实际撑开高度！ */
  }
  .accordion-inner {
    overflow: hidden; /* 内部子元素必须 overflow: hidden */
  }
  ```

#### 3. HTML5 原生语义化标签：`<details>`
- 浏览器自带展开收起行为，无需任何 JS 状态维护；
- 现代 Chrome 120+ 原生支持给 `details::details-content` 添加过渡动画。

---

### 核心代码片段（极简记法）

```html
<!-- 原生无需一行 JS 的手风琴折叠卡片 -->
<details>
  <summary>点击展开查看常见问题</summary>
  <p>这里是折叠的详细内容，浏览器原生支持...</p>
</details>
```

---

### 面试加分项

- **手风琴互斥模式（Accordion Mutex）**：若要求“同一时刻最多只能展开一个面板，展开 A 时自动折叠 B”，原生 `<details>` 仅需加上 `name="faq-group"` 属性，同名 details 标签由浏览器内核原生自动互斥互锁，体验绝佳。""",
        "followups": """## 追问 1：JS 方案中，动态把 height 设为 scrollHeight 之后，动画执行完需要把它改回 auto 吗？为什么？

**回答要点**：
必须改回 `auto`！
因为如果一直写死具体像素高度，当用户动态拉伸浏览器窗口或内容因国际化文字变长换行时，写死的固定高度会导致内容文字溢出或高度截断。

---

## 追问 2：折叠面板收起后，里面的组件还会占用内存吗？

**回答要点**：
纯 CSS 隐藏只是样式的隐藏，内部的 DOM 节点与 React 状态依然常驻内存。如果内容极重（如包含大图、表格），应结合条件渲染在收起时彻底销毁卸载该子组件以节约内存。"""
    },
    {
        "id": "fe-scenario-037",
        "title": "DOM里面如何判定a元素是否是b元素的子元素？",
        "difficulty": "easy",
        "question": "在原生 DOM 编程中，如何判断 a 元素是否是 b 元素的子元素（或后代节点）？有哪些 API 和遍历方案？",
        "answer": """### 一句话总结

最优雅标准的原生 API 是 **`b.contains(a)`**（若 a 是 b 的后代或 a 就是 b 本身则返回 `true`）；反向查找可以使用 **`a.closest(selector)`** 向上溯源祖先；亦可利用底层高阶位运算符 **`b.compareDocumentPosition(a)`** 进行精确的节点拓扑位置判定。

---

### 详细回答

#### 1. 方案一：Node.contains()（最常用，推荐）
- `b.contains(a)`；
- 返回值：布尔值；
- **注意点**：如果 `a === b`，`contains` 也会返回 `true`。若业务要求必须是“纯子孙后代（排除自身）”，需要补一行判定：`b !== a && b.contains(a)`。

#### 2. 方案二：Element.closest()（反向查询）
- 从自身开始逐级向上查找匹配指定 CSS 选择器的最近祖先：
  ```javascript
  const isDescendant = !!a.closest('#parent-b-id');
  ```

#### 3. 方案三：compareDocumentPosition（位掩码高精判断）
- 返回两个节点相对位置的二进制位掩码：
  - `DOCUMENT_POSITION_CONTAINED_BY (16)`：代表被包含；
  ```javascript
  const isChild = !!(b.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_CONTAINED_BY);
  ```

---

### 核心代码片段（极简记法）

```javascript
// 判定 a 是否为 b 的真后代节点
function isStrictChild(a, b) {
  return a !== b && b.contains(a);
}
```

---

### 面试加分项

- **手写向上递归遍历（Polyfill 思想）**：如果面试官追问“禁止用自带 API 手写实现”，可基于 `parentNode` 编写极简的 `while` 循环向上回溯：
  ```javascript
  function isChildManual(a, b) {
    let node = a.parentNode;
    while (node) {
      if (node === b) return true;
      node = node.parentNode;
    }
    return false;
  }
  ```""",
        "followups": """## 追问 1：如果 a 元素处于 Shadow DOM 内部，外部的 b.contains(a) 能生效吗？

**回答要点**：
失效！
Shadow DOM 构建了独立的封装边界。若 a 处于 shadowRoot 内部，外部祖先的 `contains` 会直接返回 `false`。必须通过 `event.composedPath()` 获取真实的冒泡物理路径。

---

## 追问 2：如果 a 节点是一个文本节点（TextNode），contains API 依然有效吗？

**回答要点**：
依然有效！
`contains` 挂载在 `Node.prototype` 上，对元素节点（Element）、文本节点（Text）和注释节点（Comment）均完全通用。"""
    },
    {
        "id": "fe-scenario-038",
        "title": "判断对象是否为空，包含其原型链上是否有自定义数据或方法，该如何判定？",
        "difficulty": "medium",
        "question": "判断一个对象是否为空，包含了其原型链上是否有自定义数据或者方法，该如何判定？",
        "answer": """### 一句话总结

判定包含原型链的自定义数据判空，**核心是使用 `for...in` 循环扫描对象及其原型链上的所有可枚举属性，并借助 `Object.prototype` 过滤掉 ECMAScript 语言内置的标准原生原型属性（如 `toString`、`valueOf`）**；若扫描到任何非内置的自定义属性或方法，立即判定为“非空”。

---

### 详细回答

#### 1. 为什么 `Object.keys()` 与 `Reflect.ownKeys()` 都不行？
- `Object.keys(obj)` 只能获取对象**自身拥有的（Own Properties）**可枚举属性，完全忽略原型链上的继承数据；
- 无法满足“包含原型链自定义数据”的题目要求。

#### 2. 原型链过滤的核心策略
- 原生内置的顶级原型 `Object.prototype` 默认带有很多系统内置属性（`isPrototypeOf`, `propertyIsEnumerable` 等），但它们都是不可枚举的；
- 若开发者或第三方库手动修改了原型（例如 `obj.__proto__.myCustomProp = 123`），这个属性是可枚举的，能被 `for...in` 抓取；
- **排查逻辑**：
  遍历原型链直到 `proto === null` 或 `proto === Object.prototype`，收集所有自定义属性。

---

### 核心代码片段（极简记法）

```javascript
function isDeepEmpty(obj) {
  if (obj === null || typeof obj !== 'object') return false;

  // for...in 会遍历自身及整条原型链上的可枚举属性
  for (const key in obj) {
    // 排除内置 Object.prototype 原生属性干扰
    if (!(key in Object.prototype)) {
      return false; // 存在自定义原型属性或自身属性，非空！
    }
  }

  // 进一步检查不可枚举但用户自定义的非原生方法
  let curr = obj;
  while (curr && curr !== Object.prototype) {
    const ownProps = Object.getOwnPropertyNames(curr);
    const hasCustom = ownProps.some(k => k !== 'constructor');
    if (hasCustom) return false;
    curr = Object.getPrototypeOf(curr);
  }

  return true;
}
```

---

### 面试加分项

- **对不可枚举属性与 Symbol 的考量**：指出如果原型链上的方法是通过 `Object.defineProperty(proto, 'customFn', { enumerable: false })` 定义的，`for...in` 会漏掉。必须配合 `Object.getPrototypeOf()` 向上递归，用 `Object.getOwnPropertyNames()` 与 `Object.getOwnPropertySymbols()` 综合扫描才算 100% 严谨。""",
        "followups": """## 追问 1：Object.create(null) 创建的对象在判空时有何特殊之处？

**回答要点**：
`Object.create(null)` 没有原型链（`__proto__ === undefined`），没有诸如 `toString` 等任何内置方法，遍历时不会受到任何原生原型的干扰，结构极其纯净。

---

## 追问 2：直接修改 Object.prototype 对整个项目有何致命危害？

**回答要点**：
会导致原型污染（Prototype Pollution）！
全工程所有普通对象都会意外多出这个属性，不仅导致第三方库的遍历逻辑全部崩溃，还会引入严重的远程代码执行（RCE）安全漏洞。"""
    },
    {
        "id": "fe-scenario-039",
        "title": "JS如何综合判空？空数组、空对象、空字符串、0等边界如何统一处理？",
        "difficulty": "medium",
        "question": "JS如何判空？若业务约定「空」包含：空数组、空对象、空字符串、0、undefined、null、空Map、空Set，都属于为空的数据，该如何封装？",
        "answer": """### 一句话总结

综合判空采用**“基础假值快速短路 + 精准类型分流分支校验”**。首先过滤 `null` 与 `undefined`；数值 `0` 与布尔 `false` 按题意归入空；对复合引用类型分别校验：字符串与数组取 `.length === 0`，Map 与 Set 校验 `.size === 0`，普通对象校验 `Reflect.ownKeys(val).length === 0`。

---

### 详细回答

#### 1. 业务定义中的各种“空”分类
- **原生假值类**：`null`, `undefined`, `NaN`, `0`, `""`；
- **集合容器类**：
  - 数组：`[]`；
  - Map / Set：`new Map()`, `new Set()`；
- **纯对象类**：`{}`。

#### 2. 避免踩坑：为什么不能简单用 `!value`？
- 普通的 `!value` 会把非空对象 `{}` 和非空数组 `[]` 判定为 `true`（它们在布尔转换时是真值）；
- 必须针对引用对象进行内部元素的容量探测。

---

### 核心代码片段（极简记法）

```javascript
function isEmpty(val) {
  // 1. null, undefined, 空字符串, 数字 0, NaN 均为空
  if (val === null || val === undefined || val === '' || val === 0 || Number.isNaN(val)) return true;

  // 2. 数组或字符串
  if (Array.isArray(val) || typeof val === 'string') return val.length === 0;

  // 3. Map 或 Set
  if (val instanceof Map || val instanceof Set) return val.size === 0;

  // 4. 普通对象（包含 Symbol 键）
  if (typeof val === 'object') return Reflect.ownKeys(val).length === 0;

  return false;
}
```

---

### 面试加分项

- **对数字 0 是否为空的业务辩证**：必须主动向面试官指出：在常规通用工具库（如 Lodash `_.isEmpty(0)`）中，数字 `0` 是被当作**非空（有效数值）**看待的。本题之所以将 0 判为空是基于特定的业务表单清空场景，展示自己对通用库规范与业务定制差异的清醒认知。""",
        "followups": """## 追问 1：如果对象中有 Symbol 类型的 key，Object.keys() 能捕获到吗？

**回答要点**：
捕获不到！
`Object.keys()` 只返回字符串类型的自身可枚举 key；若要完全覆盖 Symbol，必须使用 `Reflect.ownKeys(obj)` 或 `Object.getOwnPropertySymbols(obj)`。

---

## 追问 2：如果传入的是一个自定义类实例（如 new Date()），你的判空函数会怎么表现？

**回答要点**：
`new Date()` 自身没有直接属性，但它有内置的时间戳状态（通过 `date.getTime()` 读取）。如果不加拦截，会被普通对象规则误判为空；因此严谨的库会加白名单优先排除 Date 与 RegExp 实例。"""
    },
    {
        "id": "fe-scenario-040",
        "title": "CSS实现翻牌效果",
        "difficulty": "medium",
        "question": "如何用纯CSS实现3D卡片翻牌效果？背靠背正反面切换的核心样式属性有哪些？",
        "answer": """### 一句话总结

CSS 3D 翻牌的核心是**“3D 透视舞台（`perspective`） + 保留 3D 空间（`transform-style: preserve-3d`） + 背面隐藏（`backface-visibility: hidden`）”**。将卡片容器作为 3D 旋转体，正反两面通过绝对定位重叠并让背面预先 `rotateY(180deg)`；当 Hover 或激活时让容器 `rotateY(180deg)`，两面同时翻转，原本隐藏的背面顺理成章转到正面展现。

---

### 详细回答

#### 1. 核心三大 CSS 属性
- **`perspective: 1000px;`**：必须加在**最外层父级舞台**上，给视网膜提供“近大远小”的真实 3D 空间透视深度；
- **`transform-style: preserve-3d;`**：必须加在**旋转卡片容器**上，指示子元素要在 3D 空间中保持立体层级，否则子元素会被强制拍平成 2D 平面；
- **`backface-visibility: hidden;`**：必须加在**正面与反面子元素**上，当元素背面朝向观察者时自动隐形不可见。

#### 2. 结构与旋转逻辑
- 正面（Front）：默认 `transform: rotateY(0deg);`；
- 反面（Back）：默认 `transform: rotateY(180deg);`（背对用户被 hidden 隐藏）；
- 容器触发翻转：`transform: rotateY(180deg);`。

---

### 核心代码片段（极简记法）

```css
.card-wrapper {
  perspective: 1000px; /* 3D 透视 */
}
.card {
  position: relative;
  transition: transform 0.6s;
  transform-style: preserve-3d; /* 维持 3D 空间 */
}
.card:hover {
  transform: rotateY(180deg); /* 翻转触发 */
}
.front, .back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden; /* 核心：背面隐藏 */
}
.back {
  transform: rotateY(180deg); /* 预先背对 */
}
```

---

### 面试加分项

- **旋转轴心与毛刺抗锯齿（Anti-aliasing）**：在翻转动画执行中，文本或边缘容易产生毛刺闪烁。加上 `transform: translateZ(0)` 或 `will-change: transform` 能触发 GPU 硬件合成渲染，保持旋转全程无微小抖动与模糊。""",
        "followups": """## 追问 1：如果不加 perspective 属性，翻转视觉上看起来会变成怎样？

**回答要点**：
若没有透视距离，翻转看起来就像是二维平面上卡片的**左右宽度在机械拉伸缩放**（从 100% 宽压成 0% 再变宽），毫无任何三维空间立体厚度感。

---

## 追问 2：点击卡片翻转后，如何让背面上的输入框或按钮正常响应点击事件？

**回答要点**：
因为翻转后背面已经面向用户，且正面已被 `backface-visibility: hidden` 隐藏，只要层级正确，背面的按钮和输入框天然能够完美接收所有点击与输入交互事件。"""
    },
    {
        "id": "fe-scenario-041",
        "title": "flex:1代表什么？",
        "difficulty": "easy",
        "question": "CSS Flex 布局中，flex: 1 是哪三个属性的简写？各自的默认值和具体作用是什么？",
        "answer": """### 一句话总结

`flex: 1` 是 **`flex-grow: 1`（放大比例）、`flex-shrink: 1`（缩小比例）、`flex-basis: 0%`（基准大小）** 的复合简写。它的核心含义是：**“该项目忽略自身内容原始尺寸（从 0 开始算），与其他同样设为 flex: 1 的兄弟元素绝对等分吸收容器中所有的剩余可用空间”**。

---

### 详细回答

#### 1. 三大属性深度拆解
- **`flex-grow: 1`**：当主轴方向有剩余空间时，该项目参与等比放大；
- **`flex-shrink: 1`**：当主轴空间不足产生溢出时，该项目参与等比收缩；
- **`flex-basis: 0%`（关键！）**：分配空间前，该元素的初始基准大小计算为 0，完全按空间分配权重均分。

#### 2. 对比：flex: 1 与 flex: auto 的本质区别
- **`flex: 1`（即 `1 1 0%`）**：强行无视内容长短，兄弟元素**绝对等宽**；
- **`flex: auto`（即 `1 1 auto`）**：保留元素内容自身的原本尺寸，仅对扣除内容后剩下的空白空间按比例瓜分，文字多的元素最终尺寸会更大。

---

### 核心代码片段（极简记法）

```css
/* 经典圣杯布局中间自适应 */
.main-content {
  flex: 1; /* 等价于 flex: 1 1 0%; 占满剩余所有宽度 */
}
```

---

### 面试加分项

- **文字过长挤破 flex: 1 的神坑与解法**：在 `flex: 1` 的子元素内部，若包含很长一段不换行的英文字符，子元素会被撑破超出父容器宽度！原因是 Flex 元素的默认属性是 `min-width: auto`。必须在 `flex: 1` 的元素上显式声明 **`min-width: 0;`**，才能强制生效省略号截断。""",
        "followups": """## 追问 1：flex 属性的单值写法中，flex: initial 代表什么？

**回答要点**：
`flex: initial` 等价于 `flex: 0 1 auto`（不放大、可缩小、尺寸依内容而定），这也是任何 flex 子项未设置 flex 时的浏览器原生默认值。

---

## 追问 2：flex-basis 的优先级与 width 相比谁更高？

**回答要点**：
在 Flex 布局的主轴方向上，`flex-basis` 的优先级**高于 `width`**。若同时设置了 `width: 200px` 与 `flex-basis: 100px`，浏览器最终以 `flex-basis` 的 100px 作为基准分配尺寸。"""
    },
    {
        "id": "fe-scenario-042",
        "title": "一般是怎么做代码重构的？",
        "difficulty": "medium",
        "question": "在大型前端项目中，一般是怎么开展代码重构的？有哪些系统化的方法论与防风险手段？",
        "answer": """### 一句话总结

安全重构的铁律是**“在不改变外部可见行为的前提下，改善软件的内部架构结构”**。工业级重构三步法：**“补齐单元/端到端自动化测试作为安全气囊 $\to$ 小步快跑、频繁提交且每次改动保持编译与测试全绿 $\to$ 配合特征开关（Feature Flag）渐进式灰度替换”**，坚决杜绝“闭关憋大招两个月全盘推翻重写”。

---

### 详细回答

#### 1. 为什么“推翻重写”90% 会以灾难告终？
- 旧系统哪怕再烂，里面也堆积了过去数年修补的无数边界特殊 Case；
- 一旦盲目全盘重写，必定丢失隐性业务逻辑，引发线上客诉雪崩。

#### 2. 系统化重构实施四部曲
1. **构建安全防护网（Safety Net）**：重构前必须为核心业务链路编写测试用例（哪怕是简单的黑盒快照测试）；
2. **绞杀者模式（Strangler Fig Pattern）**：
   - 新旧代码双轨并行；
   - 逐步将老页面的子模块一个一个替换为新代码，最终彻底绞杀并下线老代码；
3. **小步迭代（Micro-refactoring）**：
   - 提取函数（Extract Function）、重命名变量、消灭深层 if-else、抽离公共 Hook；
   - 每次提交控制在 100 行内，保证随时可发版。

---

### 核心代码片段（极简记法）

```javascript
// 绞杀者模式 + 特征开关灰度平滑替换老模块
function OrderPanel(props) {
  const isNewRefactorEnabled = useFeatureFlag('refactor_order_v2');

  return isNewRefactorEnabled ? (
    <RefactoredNewOrderPanel {...props} />
  ) : (
    <LegacyOldOrderPanel {...props} />
  );
}
```

---

### 面试加分项

- **重构契约：代码只做重构，不同时加新需求**：指出很多开发者的通病是在重构的同时顺手改需求加新特性，一旦报错根本分不清是重构引入还是新需求导致的。严格遵循“要么纯重构、要么加需求”，两项工作严格隔离独立提 PR。""",
        "followups": """## 追问 1：对于没有时间补单元测试的祖传老页面，如何进行防回归验证？

**回答要点**：
采用“流量录制与回放比对”或**“双写影子模式（Shadow Run）”**：同时执行新旧两套重构函数，前端仅展示旧函数结果，但在后台异步比对两者的输出是否 100% 严格一致，不一致时静默上报报警。

---

## 追问 2：如何说服技术领导和产品经理同意给你时间进行代码重构？

**回答要点**：
用业务语言和数据说话，而不是抱怨代码丑陋：
1. 计算研发成本（“该模块目前新增一个小需求需 5 人天，重构后降至 1 人天”）；
2. 摆出生产 Bug 率数据；
3. 顺应新业务大版本迭代的契机“搭车重构”。"""
    },
    {
        "id": "fe-scenario-043",
        "title": "如何清理源码里面没有被应用的代码（JS/TS/CSS）？",
        "difficulty": "medium",
        "question": "如何自动化扫描并清理源码中没有被引用的死代码（Dead Code / Unused Code），主要是 JS、TS 与 CSS？",
        "answer": """### 一句话总结

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

- **动态类名导致 PurgeCSS 误杀的避坑**：若代码中存在拼接类名如 `<div className={\`btn-\${color}\`}>`，静态分析器无法推导，会误以为 `btn-red` 未使用而强行删掉导致生产样式丢失。解决是在 PurgeCSS 配置中配置白名单（`safelist: [/^btn-/]`）。""",
        "followups": """## 追问 1：为什么有的工具把明明有用的代码给误报成无用导出了？

**回答要点**：
因为某些代码是通过动态 `import(variablePath)` 或反射动态调用的，静态语法树分析器无法推断动态运行时路径，因此需要给此类特殊文件配置 `ignore` 规则。

---

## 追问 2：package.json 中的 sideEffects 字段到底起什么作用？

**回答要点**：
它告诉 Webpack / Rollup 该模块内的代码是否包含副作用（如修改全局 window、执行自动打点）。若声明 `false`，当项目中仅 `import { a } from 'lib'` 时，打包器会大胆地把 `lib` 内部未使用的其他几百个函数连同它们的顶层语句全部摇掉。"""
    },
    {
        "id": "fe-scenario-044",
        "title": "前端应用如何做国际化？",
        "difficulty": "medium",
        "question": "前端应用如何做多语言国际化（i18n）？架构设计、文案管理与异步按需加载如何落地？",
        "answer": """### 一句话总结

前端国际化采用**“文案标识解耦（Key 映射） + 核心运行时（如 `react-i18next` / `vue-i18n`） + 语言包动态按需异步加载”**。界面严禁硬编码中文字符，统一使用 `t('login.submit')` 占位；通过 Webpack / Vite 将各语言包切分为独立 JSON 异步分包，切换语言时仅动态拉取对应语种资源，首屏零额外体积负担。

---

### 详细回答

#### 1. 核心架构设计三要素
- **语言检测中枢**：优先级判断：URL 参数（`?lang=en`） $\to$ 本地 LocalStorage 记忆 $\to$ 浏览器系统偏好（`navigator.language`）；
- **动态占位插值与复数处理**：支持变量插值（`t('welcome', { name: 'Jack' })`）以及英语等单复数转换规则；
- **按需加载（Code Splitting）**：用户在中国访问只下载中文包，点击切换“English”时才动态 fetch 英文语言包。

#### 2. 日常开发痛点：文案提取与维护
- 研发手动去文案表格复制 Key 极度低效痛苦；
- 引入自动化 CLI 工具（如 `i18n-ally` VS Code 插件）：在代码中直接写中文，构建时自动扫描提取并生成国际化 JSON 映射表。

---

### 核心代码片段（极简记法）

```javascript
import i18n from 'i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend) // 动态从 CDN 异步按需拉取目标语言包
  .init({
    lng: 'zh-CN',
    fallbackLng: 'en',
    backend: { loadPath: '/locales/{{lng}}/{{ns}}.json' }
  });

// 组件内消费
const { t } = useTranslation();
return <button>{t('common.confirm')}</button>;
```

---

### 面试加分项

- **样式与排版的国际化灾难（排版适配）**：不同语言文案长度差异巨大（德语、俄语文案通常比中文长 2~3 倍）。严禁在按钮上写死固定宽度（`width: 80px`），布局必须采用自适应宽度并留足安全间距；针对阿拉伯语等中东语言，还需在 `<html>` 标签动态切换 `dir="rtl"`（从右往左排版）。""",
        "followups": """## 追问 1：数字、日期、货币的国际化（如人民币 vs 美元格式）怎么处理？

**回答要点**：
无需引入庞大的第三方库，优先使用现代浏览器原生内置的 **`Intl` 对象**！
- 货币与数字：`new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.5)`；
- 日期时间：`new Intl.DateTimeFormat('zh-CN').format(new Date())`。

---

## 追问 2：多语言页面如何做好 SEO 搜索引擎优化？

**回答要点**：
在 HTML `<head>` 中添加包含语言指示的 `<link rel="alternate" hreflang="en" href="https://example.com/en/" />` 标签，并在服务端根据路由直接输出对应语种的纯净 HTML，禁止由纯前端客户端异步渲染导致爬虫抓到空白 Key。"""
    },
    {
        "id": "fe-scenario-045",
        "title": "应用如何做应用灰度发布？",
        "difficulty": "medium",
        "question": "前端应用如何落地灰度发布（渐进式放量）？有哪些架构方案及回滚机制？",
        "answer": """### 一句话总结

前端灰度发布核心有两大路径：**“网关/CDN 路由级灰度（分流静态资源入口 `index.html`）”**与**“代码层特征开关灰度（Feature Flag 动态控制功能组件）”**。网关根据用户 ID、IP 或 Cookie 计算一致性哈希，将 10% 的流量导流至加载了 `index_v2.html` 的灰度版本，一旦发现监控报错激增，秒级调整分流比例归零实现一键无感回滚。

---

### 详细回答

#### 1. 方案一：Nginx / 网关层分流（最彻底的整站灰度）
- 构建时打包出两份产物：`dist_v1`（稳定版）与 `dist_v2`（灰度版）；
- 在 Nginx 或边缘网关（OpenResty / Cloudflare Workers）提取用户 Cookie `uid`：
  - 对 `uid` 做 MurmurHash 取模 100；
  - 若数值小于设定阈值（如 10），Nginx 内部代理转发到 `dist_v2/index.html`；
  - 其余 90% 流量依然加载 `dist_v1/index.html`。

#### 2. 方案二：特征开关（Feature Flags / 业务组件级灰度）
- 代码正常全量发版；
- 页面加载时向配置中心拉取当前用户的 Flag 清单；
- 代码中包裹判断：`if (flags.enableNewCheckout) { ... }`；
- 优势：无需多版本打包部署，颗粒度细化到单个按钮与组件。

---

### 核心代码片段（极简记法）

```nginx
# Nginx 基于 Cookie 的 uid 做 10% 权重灰度路由
split_clients "${cookie_uid}" $app_version {
  10%     "/dist_v2/"; # 灰度版
  *       "/dist_v1/"; # 稳定版
}

location / {
  root /var/www$app_version;
  try_files $uri $uri/ /index.html;
}
```

---

### 面试加分项

- **静态资源版本容错（Version Cascade）**：灰度发布期间，CDN 上**必须同时完整保留 v1 和 v2 的所有带 hash 的 JS/CSS 文件**！若直接覆盖或清理了旧版资源，会导致尚未刷新页面的 90% 旧版用户在懒加载新页面路由时触发致命的 404 ChunkLoadError。""",
        "followups": """## 追问 1：灰度发布时，如果新版本涉及后端数据库字段的破坏性变更，前端怎么配合？

**回答要点**：
遵循“扩展而非修改（Expand and Contract）”原则：
后端先发版支持新老字段双写兼容；前端发布灰度验证无误；最后全量切流后再逐步清理后端老字段，严禁前后端进行硬碰硬的同步一次性割接。

---

## 追问 2：如何让公司内部的测试人员、产品经理强制固定进入灰度版本？

**回答要点**：
白名单覆盖机制：在网关逻辑中优先判断：若 URL Query 携带特定调试参数（如 `?__preview_env=v2`）或请求头包含特定员工 Cookie，无视哈希比例直接强制路由至灰度版本。"""
    },
    {
        "id": "fe-scenario-046",
        "title": "为何通常在微前端应用隔离，不选择iframe方案？",
        "difficulty": "medium",
        "question": "为何通常在微前端应用隔离中，不优先选择原生的 iframe 方案？它有哪些难以逾越的体验硬伤？",
        "answer": """### 一句话总结

iframe 拥有最完美的物理级硬隔离，但它带来了**“无法逾越的体验与交互割裂”**。最核心的五大硬伤是：**URL 路由状态无法与浏览器前进后退无缝同步**、**弹窗无法居中在视口全屏展示（被局限在 iframe 小框内）**、**每次重新加载导致白屏且无法复用公共公共基础依赖（内存消耗巨大）**、以及**跨 iframe 通信（postMessage）繁琐且脆弱**。

---

### 详细回答

#### 1. 硬伤一：UI 视图与全屏弹窗受限
- 子应用如果有 Modal 弹窗或下拉选择菜单，它的绝对定位只能局限在 iframe 自己的内部区域；
- 无法遮罩整个宿主浏览器屏幕，UI 体验极其滑稽与山寨。

#### 2. 硬伤二：路由状态丢失（Deep Linking 灾难）
- 用户在 iframe 内部点击跳转到了 `/page/detail/10`；
- 此时按下浏览器 F5 刷新，整个页面重载，iframe 内部状态瞬间被重置回了默认初始首页；
- 用户无法将带有深层路由的链接直接复制分享给他人。

#### 3. 硬伤三：性能与内存冗余
- 每个 iframe 是一个独立的完整浏览上下文；
- 宿主和 3 个 iframe 子应用必须各自初始化一份完整的 React、ReactDOM、Vue 运行时和 CSS 样式表；
- DOM 树成倍增加，内存消耗极大，切换子应用时伴随明显的空白闪烁。

---

### 核心代码片段（极简记法）

```html
<!-- iframe 弹窗被死死困在局部，无法覆盖全屏 -->
<div class="host-app">
  <iframe src="http://sub-app.com" style="width: 500px; height: 300px;"></iframe>
</div>
```

---

### 面试加分项

- **无界（Wujie）微前端框架对 iframe 的逆向拯救**：指出业界已有优秀的创新方案（如腾讯无界）：将 iframe 仅仅作为**纯 JS 代码的无头执行沙箱**，而将所有的 DOM 元素投影抽取渲染到宿主主应用中，既继承了 iframe 绝对完美的 JS 隔离，又彻底消除了弹窗受限与样式隔离的难题！""",
        "followups": """## 追问 1：iframe 在什么场景下仍然是最佳甚至唯一的选择？

**回答要点**：
当需要嵌入**完全不受信任的第三方外部应用**（如用户自行上传的未审核插件、不可信的第三方支付收银台）时，iframe 依然是无可替代的唯一安全硬防线，能绝对防御跨站脚本盗取主站凭据。

---

## 追问 2：不用 iframe 的微前端框架（如 Qiankun）是如何实现样式隔离的？

**回答要点**：
1. **Shadow DOM（真正严格隔离）**；
2. **动态 Scoped CSS**：在运行时给子应用所有 CSS 选择器自动追加特定的父级属性前缀（如 `div[data-qiankun="app1"]`）。"""
    },
    {
        "id": "fe-scenario-047",
        "title": "Qiankun是如何做JS隔离的？",
        "difficulty": "hard",
        "question": "Qiankun 是如何做 JavaScript 隔离的？SnapshotSandbox、ProxySandbox 与 Singular 模式底层原理是什么？",
        "answer": """### 一句话总结

Qiankun 的 JS 隔离采用**“现代 Proxy 代理沙箱（ProxySandbox / SingularProxySandbox）为主，旧版快照沙箱（SnapshotSandbox）降级兜底”**。现代沙箱基于 ES6 `Proxy` 拦截子应用对 `window` 的读写，将所有全局变量增删改操作收拢在内存的 `fakeWindow` 代理对象中；子应用卸载时直接弃置代理，主应用真实全局环境分毫不受污染。

---

### 详细回答

#### 1. 方案一：SnapshotSandbox（旧版单实例快照沙箱，降级方案）
- **适用场景**：不支持 ES6 Proxy 的低版本浏览器（IE11）；
- **原理**：
  - 子应用激活（`active`）：遍历记录当前 `window` 状态存为快照 `windowSnapshot`，恢复上一次的修改；
  - 子应用卸载（`inactive`）：再次遍历 `window` 与快照比对，记录差异并将 `window` 还原回原始状态；
- **劣势**：遍历 window 极其消耗性能，且同一时刻屏幕上**只允许激活一个子应用**。

#### 2. 方案二：SingularProxySandbox（单实例代理沙箱）
- 基于单个 Proxy 拦截；
- 维护 `addedPropsMap` 与 `modifiedPropsMap`，激活时就地赋值，卸载时根据记录快速撤销改动。

#### 3. 方案三：MultipleProxySandbox（多实例代理沙箱，最先进）
- 允许同一个页面上**同时挂载多个子应用**并排运行；
- 为每个子应用各自创建一个全新的空对象 `fakeWindow`；
- 当子应用读取变量时，优先读自身 `fakeWindow`，没有再逃逸读取真实 `window`；
- 当子应用给 `window.a = 123` 赋值时，**只写入自己的 `fakeWindow`**，各子应用间互不干扰。

---

### 核心代码片段（极简记法）

```javascript
// 多实例 Proxy 沙箱核心微型原理
class MiniProxySandbox {
  constructor() {
    this.fakeWindow = {};
    this.proxy = new Proxy(window, {
      get: (target, p) => this.fakeWindow[p] ?? target[p],
      set: (target, p, val) => {
        this.fakeWindow[p] = val; // 所有的污染仅沉淀在 fakeWindow 中
        return true;
      }
    });
  }
}
```

---

### 面试加分项

- **定时器与全局事件监听器的沙箱拦截（Patch System）**：指出仅仅代理属性是不够的！若子应用调用了 `window.setInterval` 或 `window.addEventListener('scroll')`，在卸载时必须自动销毁。Qiankun 重写了全局的定时器和事件监听 API，记录所有由子应用发起的监听器引用，在子应用卸载时自动全量批量解除（Unbind），防止内存泄漏。""",
        "followups": """## 追问 1：子应用如果是通过 eval 执行的，如何让它执行时的 window 指向 proxy 而不是原生 window？

**回答要点**：
采用“带参数的即时执行函数（IIFE）包裹”：
在执行子应用代码前，包裹一行：
`;(function(window, self, globalThis){ ...子应用源码... })(proxyWindow, proxyWindow, proxyWindow);`，强行将作用域内的 `window` 重定向至代理沙箱对象。

---

## 追问 2：如果子应用代码里写了 const a = window; top.window.b = 1，会逃逸沙箱吗？

**回答要点**：
直接访问 `top` 或 `parent` 可能会导致逃逸。
因此工业级沙箱会对 `top`、`parent`、`window` 等特殊保留关键字在 Proxy 的 `get` 拦截器中做特殊防逃逸处理，强制将其映射返回为沙箱实例本身。"""
    },
    {
        "id": "fe-scenario-048",
        "title": "微前端架构一般是如何做JavaScript隔离的？",
        "difficulty": "hard",
        "question": "微前端架构一般是如何做JavaScript隔离的？业界主流的隔离方案有哪些演进路线？",
        "answer": """### 一句话总结

微前端 JS 隔离历经三代演进：**“第一代：快照恢复（Snapshot Diff，卸载时还原现场，性能差且只支持单实例） $\to$ 第二代：Proxy 代理沙箱（FakeWindow 拦截隔离读写，支持多实例并发） $\to$ 第三代：Web Worker / 无头 iframe 原生硬件沙箱（代码运行在物理隔离的全新全局上下文中，杜绝任何逃逸）”**。

---

### 详细回答

#### 1. 为什么需要 JS 隔离？
- 子应用 A 定义了 `window.user = { role: 'admin' }`；
- 子应用 B 误写了 `window.user = 'Jack'`；
- 两个子应用互相覆盖踩踏全局变量，或者全局事件监听器在子应用卸载后未注销导致严重内存泄漏。

#### 2. 主流隔离方案横向矩阵对比
- **快照沙箱（如 Qiankun Snapshot）**：通过遍历 `window` 的 Diff 记录修改；兼容性好（支持 IE），性能开销大；
- **Proxy 代理沙箱（如 Qiankun / MicroApp）**：拦截属性存取，通过 with 语句或动态作用域传递 `fakeWindow`；主流标准；
- **影子 iframe 沙箱（如 腾讯无界 Wujie）**：开辟一个不可见的无头 `iframe`，直接把子应用 JS 塞进 iframe 内部运行，利用浏览器最原生的 JS 引擎环境实现 100% 隔离且零额外劫持开销。

---

### 核心代码片段（极简记法）

```javascript
// 现代沙箱核心作用域绑定机制
function runInSandbox(code, sandboxProxy) {
  // 利用 with 改变作用域链，使全局寻址优先命中 sandboxProxy
  const fn = new Function('window', `with(window) { ${code} }`);
  fn(sandboxProxy);
}
```

---

### 面试加分项

- **对 Web Components 原生特性的界定**：必须注意，浏览器的 **Web Components（Shadow DOM）只负责 DOM 结构与 CSS 样式的强隔离**，它在 JavaScript 层面**完全没有任何隔离能力**（Shadow DOM 内部的 JS 依然共享最外层的全局 `window`）。千万不要在面试时误将 Shadow DOM 当成 JS 隔离手段。""",
        "followups": """## 追问 1：在严格模式（'use strict'）下，函数内部未通过 var/let 声明直接写 a = 1，会报错还是挂在全局？沙箱怎么拦截？

**回答要点**：
严格模式下会直接抛出 `ReferenceError: a is not defined`，根本不会挂到全局；
而在非严格模式下，沙箱在 Proxy 的 `has` 拦截器中返回 `true`，配合 `with` 语法糖能强制将该隐式全局赋值捕获到 `fakeWindow` 中。

---

## 追问 2：无界（Wujie）使用 iframe 做 JS 沙箱，那子应用里的 document.getElementById 查到的是哪个页面？

**回答要点**：
无界在 iframe 沙箱中重写了 `document` 的查询方法！
将其所有 DOM 查询重定向代理到宿主应用中对应的 Web Component 容器节点上，实现了“JS 运行在 iframe，DOM 渲染并操作宿主容器”的绝妙分离。"""
    },
    {
        "id": "fe-scenario-049",
        "title": "React循环渲染中为什么推荐不用index做key？",
        "difficulty": "medium",
        "question": "React 循环渲染中为什么强烈推荐不用 index 做 key？用 index 会引发什么性能和 UI Bug？什么时候可以破例用 index？",
        "answer": """### 一句话总结

React 的 Diff 算法通过 `key` 识别节点的唯一性。**若用 `index` 作 key，在列表发生插入、删除或反转重排时，节点的 index 会集体发生错位错乱**；导致 React 误以为所有后续节点都发生了变化而**引发无意义的全量 Diff 性能退化**，更严重的是会导致带有非受控状态的子组件（如输入框光标、未保存草稿）**错误复用旧状态，产生恶劣的数据错位 UI Bug**。

---

### 详细回答

#### 1. 经典 UI 错位灾难（案例复现）
- 列表有 3 项：`[A(key=0), B(key=1), C(key=2)]`，每一项内嵌一个输入框；
- 用户在第 1 项输入了“AAA”；
- 此时用户点击“删除第 1 项”；
- 剩下的数组变为：`[B(key=0), C(key=1)]`；
- **React 的 Diff 视角**：
  - “key=0 的节点还在，无需销毁重建，直接更新 props”；
  - 结果：**原来第 1 项输入框里的“AAA”错误地留在了现在的 B 组件上！**；
  - 真正被销毁的反而是原本 key=2 的 C 组件！

#### 2. 为什么唯一稳定 ID（如 item.id）能解决问题？
- 节点绑定 `key={item.id}`；
- 无论列表怎么翻转、排序、删除，每个业务实体的 ID 恒定不变；
- React 能精准判定“哪个实体被移走了、哪个实体位移了”，实现高效复用与正确的组件销毁。

#### 3. 什么时候可以破例用 index？
- 列表仅用于纯静态展示、**绝对不会发生任何插入/删除/排序操作**，且项内无任何内部状态。

---

### 核心代码片段（极简记法）

```javascript
// ❌ 极度危险：易引发数据错位
{list.map((item, index) => <UserCard key={index} data={item} />)}

// ✅ 规范标准：绑定唯一稳定业务标识符
{list.map((item) => <UserCard key={item.id} data={item} />)}
```

---

### 面试加分项

- **避免在 render 循环中动态生成 key**：有人为了图省事写 `key={Math.random()}`。这会导致每一次父组件重刷时所有子组件的 key 都全部变动，React 会判定全部节点死亡并从 DOM 彻底物理销毁重建，造成极其灾难的性能暴跌和输入框聚焦丢失。""",
        "followups": """## 追问 1：如果接口返回的数据确实没有唯一 ID 字段，前端应该怎么生成 key？

**回答要点**：
在数据拉取成功的第一时间（数据入库/Store 时），遍历数组使用 `crypto.randomUUID()` 或自增计数器为每一项附加一个稳定字段 `item._tempId = uuid()`；绝不要在 JSX 渲染模板时动态临时生成。

---

## 追问 2：React 的 Diff 算法比对 key 时，是跨层级比对的吗？

**回答要点**：
不是！
React 的启发式 Diff 算法只在**同级节点（Same Level）**之间进行高效比对，时间复杂度为 $O(N)$；若节点跨越了不同的父层级，React 会直接销毁旧树并重建新树。"""
    },
    {
        "id": "fe-scenario-050",
        "title": "React如何避免Context引起整个挂载节点树重新渲染？",
        "difficulty": "hard",
        "question": "React 中使用 Context 时，如何避免 Provider 根节点的值更新引起整棵挂载节点树的无差别重新渲染？",
        "answer": """### 一句话总结

Context 导致全量重刷的核心根源是**“Context 消费端是基于引用的粗粒度穿透订阅，无法按需订阅局部属性”**。三大防线：**“拆分多个细粒度 Context（按读写频次分离）”**、**“通过 `children` 属性或 `React.memo` 将不需要更新的中间层级隔离开”**、以及在生产级复杂场景中**“改用基于 `useSyncExternalStore` 的外部原子化状态库（如 Zustand / Jotai）”**。

---

### 详细回答

#### 1. 误区剖析：为什么 React.memo 挡不住 Context？
- 如果子组件内部直接调用了 `useContext(MyContext)`；
- 只要 Provider 的 `value` 发生引用变动，**任何 `React.memo` 都会被直接穿透失效！**消费了该 Context 的组件必定强制执行重渲染。

#### 2. 防御策略一：通过 children 传参（组件组合解耦）
- 如果 Provider 内部有状态更新，包裹在其 JSX 标签内的子元素若是作为 `children` 传入的：
  ```javascript
  function MyProvider({ children }) {
    const [theme, setTheme] = useState('dark');
    return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
  }
  ```
- 此时 `children` 是在父级组件创建好的 React Element 引用，只要父级不重刷，`children` 对应的中间层组件直接跳过重绘！

#### 3. 防御策略二：读写分离（Context Splitting）
- 将高频变化的“状态（State）”与低频不变的“修改函数（Dispatch）”拆分为两个独立的 Context：
  `ThemeStateContext` 与 `ThemeDispatchContext`；
  仅需要触发点击操作的按钮只订阅 Dispatch，完全不因 State 的变动而触发重刷。

---

### 核心代码片段（极简记法）

```javascript
// 拆分为只读状态与操作动作两个 Context
const CountStateContext = createContext();
const CountDispatchContext = createContext();

function CounterProvider({ children }) {
  const [count, dispatch] = useReducer(reducer, 0);
  return (
    <CountStateContext.Provider value={count}>
      <CountDispatchContext.Provider value={dispatch}>
        {children} {/* 保持不变，中间层级不重刷 */}
      </CountDispatchContext.Provider>
    </CountStateContext.Provider>
  );
}
```

---

### 面试加分项

- **use-context-selector 提案实现**：原生 Context 不支持选择器（Selector）。可通过社区知名库 `use-context-selector`，让组件仅在 `useContextSelector(Ctx, state => state.user.name)` 关注的单一属性变化时才重刷，实现精准更新。""",
        "followups": """## 追问 1：useMemo 包裹 Provider 的 value 属性，能阻止消费者的重渲染吗？

**回答要点**：
能阻止“因父组件其他无关状态变更导致的消费者误刷”；
但只要 `useMemo` 依赖的某个属性真正发生改变，生成的对象引用发生变化，所有订阅了该 Context 的消费者依然会正常触发重渲染。

---

## 追问 2：为什么大型企业级复杂前端工程普遍不推荐把所有全局状态都塞在 Context 里？

**回答要点**：
因为 Context 本质上是 React 提供的“依赖注入（Dependency Injection）”工具，并非高性能的状态管理器；它缺乏原生的微更新切片、缺乏时间旅行调试工具，且高频更新会导致难以排查的雪崩级渲染卡顿。"""
    }
]

for item in DATA:
    qdir = os.path.join(QUESTIONS_DIR, item['id'])
    os.makedirs(qdir, exist_ok=True)
    with open(os.path.join(qdir, 'question.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {item['title']}\n\n{item['question']}\n")
    with open(os.path.join(qdir, 'answer.md'), 'w', encoding='utf-8') as f:
        f.write(item['answer'].strip() + '\n')
    with open(os.path.join(qdir, 'followups.md'), 'w', encoding='utf-8') as f:
        f.write(item['followups'].strip() + '\n')

print(f"Generated {len(DATA)} questions successfully (fe-scenario-026 ~ fe-scenario-050)!")
