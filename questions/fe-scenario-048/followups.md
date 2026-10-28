## 追问 1：在严格模式（'use strict'）下，函数内部未通过 var/let 声明直接写 a = 1，会报错还是挂在全局？沙箱怎么拦截？

**回答要点**：
严格模式下会直接抛出 `ReferenceError: a is not defined`，根本不会挂到全局；
而在非严格模式下，沙箱在 Proxy 的 `has` 拦截器中返回 `true`，配合 `with` 语法糖能强制将该隐式全局赋值捕获到 `fakeWindow` 中。

---

## 追问 2：无界（Wujie）使用 iframe 做 JS 沙箱，那子应用里的 document.getElementById 查到的是哪个页面？

**回答要点**：
无界在 iframe 沙箱中重写了 `document` 的查询方法！
将其所有 DOM 查询重定向代理到宿主应用中对应的 Web Component 容器节点上，实现了“JS 运行在 iframe，DOM 渲染并操作宿主容器”的绝妙分离。
