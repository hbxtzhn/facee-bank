## 追问 1：在每秒 50 次 Token 的极高频流式推流下，Immer 本身的 Proxy 开销会不会成为瓶颈？

**回答要点**：
会有轻微开销。在极端追求性能的场景下：
1. 流式生成期间仅在内存中维护纯可变字符串 Buffer；
2. 配合 `requestAnimationFrame` 做帧级节流；
3. 仅在节流刷新 UI 时调用一次 Immer，将 Proxy 创建频次限制在每秒 30~60 次以内，完全无性能压力。

---

## 追问 2：Immer 配合 Redux Toolkit / Zustand 时怎么使用？

**回答要点**：
Redux Toolkit 的 `createSlice` 内部已经默认集成了 Immer，在 reducer 里直接写赋值修改即可；Zustand 则只需添加 `immer` 中间件包裹 store 定义函数即可。
