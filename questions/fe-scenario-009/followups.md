## 追问 1：在 Chrome 中，多个独立的系统窗口并排展示时，visibilityState 会是 hidden 吗？

**回答要点**：
不会。
只要当前页签在物理显示器上有哪怕 1 像素露出，它的 `visibilityState` 都是 `'visible'`，只有当它被完全盖住、折叠最小化或切换 Tab 时才会变成 `'hidden'`。

---

## 追问 2：页面切后台时，如何修改标题吸引用户切回（如展示「您有一条新消息」）？

**回答要点**：
在 `visibilitychange` 为 `hidden` 且有新消息时，启动轻量定时器交替修改 `document.title`（如 `document.title = '【新消息】您收到一条回复'`）；切回 `visible` 时立即还原原始标题。
