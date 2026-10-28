### 一句话总结

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

- **定时器与全局事件监听器的沙箱拦截（Patch System）**：指出仅仅代理属性是不够的！若子应用调用了 `window.setInterval` 或 `window.addEventListener('scroll')`，在卸载时必须自动销毁。Qiankun 重写了全局的定时器和事件监听 API，记录所有由子应用发起的监听器引用，在子应用卸载时自动全量批量解除（Unbind），防止内存泄漏。
