## 追问 1：在 beforeunload 回调函数中执行一个耗时 2 秒的 while 同步死循环能阻止页面关闭吗？

**回答要点**：
不能！
现代浏览器引擎内置了强制杀死超时进程的看门狗机制（Watchdog）。若在卸载钩子中卡住，浏览器会直接强行杀掉该 Render 进程并关闭窗口。

---

## 追问 2：pagehide 和 unload 有什么细微差别？

**回答要点**：
`pagehide` 事件在页面进入浏览器的往返缓存（BFCache / Back-Forward Cache）时也会触发，且其事件对象包含 `e.persisted` 属性标识页面是否被缓存以便后续秒开。
