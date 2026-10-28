## 追问 1：监控 SDK 自身如果写出 Bug 报错了，会不会把宿主主业务搞死？

**回答要点**：
必须设计“看门狗保护”：
1. SDK 内部所有代码必须严密包裹在 `try...catch` 中；
2. 严禁在 SDK 的报错处理逻辑内部再次触发上报报错（防止死循环发包导致浏览器崩溃）。

---

## 追问 2：Script error（跨域脚本错误）拿不到具体的错误堆栈，只显示 Script error. 怎么解？

**回答要点**：
1. 在引入该跨域 JS 的 `<script>` 标签上添加 `crossorigin="anonymous"` 属性；
2. 静态资源 CDN 响应头必须返回 `Access-Control-Allow-Origin: *`，两项齐备浏览器才会向 JS 暴露详细堆栈。
