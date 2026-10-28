## 追问 1：在 Jotai 中，如果需要重置所有调参原子为默认值，如何优雅设计？

**回答要点**：
使用 `atom(null, (get, set) => ...)` 创建一个只写（Write-only）原子，在其更新函数内部集中调用 `set(tempAtom, 0.7)`、`set(topPAtom, 0.9)`，外部一键调用即可全量重置。

---

## 追问 2：Jotai 与 React 18 并发特性的兼容性如何？

**回答要点**：
Jotai v2 深度基于 React 原生的 `useSyncExternalStore` 构建，完全原生兼容 React 18 并发模式与时间切片，杜绝任何 Tear（UI 撕裂）现象。
