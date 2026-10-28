## 追问 1：离线状态下，大模型推理本身如何进行？

**回答要点**：
若完全离线，可通过 WebAssembly / WebGPU 在前端本地运行轻量蒸馏模型（如 WebLLM 运行 Llama 3-8B 或 ONNX Runtime Web）；若本地硬件无法支撑，则只允许离线浏览历史并排队暂存任务，提示联网后自动推理。

---

## 追问 2：TanStack Query 如何处理长文本流式请求？

**回答要点**：
TanStack Query 擅长传统的 Promise 请求，流式通常配合 `useMutation` 触发：在 mutation 函数中拉取 stream，并在 `onChunk` 回调中通过 `queryClient.setQueryData` 手动更新缓存树。
