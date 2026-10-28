## 追问 1：子应用如果是通过 eval 执行的，如何让它执行时的 window 指向 proxy 而不是原生 window？

**回答要点**：
采用“带参数的即时执行函数（IIFE）包裹”：
在执行子应用代码前，包裹一行：
`;(function(window, self, globalThis){ ...子应用源码... })(proxyWindow, proxyWindow, proxyWindow);`，强行将作用域内的 `window` 重定向至代理沙箱对象。

---

## 追问 2：如果子应用代码里写了 const a = window; top.window.b = 1，会逃逸沙箱吗？

**回答要点**：
直接访问 `top` 或 `parent` 可能会导致逃逸。
因此工业级沙箱会对 `top`、`parent`、`window` 等特殊保留关键字在 Proxy 的 `get` 拦截器中做特殊防逃逸处理，强制将其映射返回为沙箱实例本身。
