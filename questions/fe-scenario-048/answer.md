### 一句话总结

微前端 JS 隔离历经三代演进：**“第一代：快照恢复（Snapshot Diff，卸载时还原现场，性能差且只支持单实例） $	o$ 第二代：Proxy 代理沙箱（FakeWindow 拦截隔离读写，支持多实例并发） $	o$ 第三代：Web Worker / 无头 iframe 原生硬件沙箱（代码运行在物理隔离的全新全局上下文中，杜绝任何逃逸）”**。

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

- **对 Web Components 原生特性的界定**：必须注意，浏览器的 **Web Components（Shadow DOM）只负责 DOM 结构与 CSS 样式的强隔离**，它在 JavaScript 层面**完全没有任何隔离能力**（Shadow DOM 内部的 JS 依然共享最外层的全局 `window`）。千万不要在面试时误将 Shadow DOM 当成 JS 隔离手段。
