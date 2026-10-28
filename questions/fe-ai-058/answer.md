### 一句话总结

前端离线推理采用**“WebLLM / llama.cpp 编译为 WASM + WebGPU 硬件着色器加速 + 流式内存量化加载”**。将 4-bit 量化后的轻量模型（如 Qwen2-0.5B、Phi-3-mini）直接部署在静态 CDN 上；前端借助 WebGPU 并发调度 GPU 计算核心执行矩阵运算，实现**完全断网环境下在浏览器内实时吐字推理**。

---

### 详细回答

#### 1. 为什么纯 WASM CPU 推理大模型不现实？
- 大语言模型单次生成需要不断遍历几十亿个参数矩阵；
- 纯 CPU 算力极为有限，WASM CPU 跑 1B 模型通常只有 1~2 Token/s，卡顿无法使用；
- 必须依赖 **WebGPU API**，直接调用显卡的 Compute Shader 实现硬件并行加速。

#### 2. 模型下载与缓存工程
- 即使是 4-bit 量化模型，体积也有 1~2 GB；
- **分块流式加载**：将大模型权重切分为多个 50MB 的 `.bin` 文件并发下载；
- **进度通知**：向用户展示精确的“模型离线包下载中 45%”进度条；
- **Cache API 永久固化**：存入浏览器 CacheStorage，用户后续打开零耗流量。

---

### 核心代码片段（极简记法）

```javascript
import * as webllm from '@mlc-ai/web-llm';

// 1. 初始化 WebGPU 推理引擎
const engine = new webllm.MLCEngine();
engine.setInitProgressCallback((report) => console.log(report.text)); // 进度更新

// 2. 加载本地/CDN 模型
await engine.reload('Qwen2-0.5B-Instruct-q4f16_1-MLC');

// 3. 纯本地流式推理（断网也能跑！）
const chunks = await engine.chat.completions.create({
  messages: [{ role: 'user', content: '前端怎么做离线化？' }],
  stream: true
});
for await (const chunk of chunks) {
  console.log(chunk.choices[0]?.delta?.content || '');
}
```

---

### 面试加分项

- **设备兼容性降级矩阵**：在加载模型前调用 `navigator.gpu?.requestAdapter()`，若检测到低端集成显卡或内存小于 4GB 的移动设备，友好提示“当前设备硬件算力不足，已自动切换为云端模型”，防止撑爆浏览器内存崩溃。
