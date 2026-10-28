### 一句话总结

利用 **WebAssembly（WASM，结合 SIMD 多指令与多线程支持）** 将 C++/Rust 编译的推理引擎（如 ONNX Runtime Web / Transformers.js）运行在浏览器端。通过 **`WebAssembly.Memory` 共享线性内存**，避免在 JS 与 WASM 边界频繁深拷贝庞大的浮点数 Embedding 向量，实现单次向量余弦相似度计算仅耗时微秒级。

---

### 详细回答

#### 1. 为什么纯 JavaScript 做向量计算不够快？
- 向量通常是 512 或 1536 维度的 `Float32Array`；
- 纯 JS 执行向量点积和范数计算无法有效利用 CPU 的 SIMD 硬件级并行指令集，单次匹配几千个向量需耗时上百毫秒。

#### 2. WASM SIMD 硬件加速
- WebAssembly SIMD（单指令多数据流）允许**单条 CPU 指令并行处理 4 个 32 位浮点数**运算，吞吐量理论提升 4 倍以上。

#### 3. 规避 JS/WASM 跨语言通信开销（零拷贝）
- 严禁在调用 WASM 函数时传递普通 JS 对象；
- **正确做法**：JS 直接向 WASM 的共享线性内存地址空间（Linear Memory）中写入向量二进制内存切片，传递内存指针和长度，WASM 计算完就地写回，彻底杜绝数据序列化损耗。

---

### 核心代码片段（极简记法）

```javascript
// 零拷贝传入 Embedding 向量
const memory = wasmInstance.exports.memory;
const wasmBuffer = new Float32Array(memory.buffer, pointer, vectorLength);
wasmBuffer.set(jsFloat32Embedding); // 内存直接拷贝

// 调用 WASM 导出函数执行 SIMD 快速余弦计算
const similarityScore = wasmInstance.exports.cosineSimilarity(pointerA, pointerB, vectorLength);
```

---

### 面试加分项

- **WebGPU 演进路线**：指出对于超大矩阵乘法（LLM 逐 Token 解码），WebGPU 比 WASM 还要快 10~50 倍；当前端硬件支持 WebGPU 时优先走 GPU 着色器，不支持时降级走 WASM + SIMD。
