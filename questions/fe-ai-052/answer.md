### 一句话总结

该系统采用**“轻量量化小模型（如 all-MiniLM-L6-v2 ONNX 量化版） + ONNX Runtime Web 推理引擎 + 内存余弦相似度（Cosine Similarity）矩阵运算”**。纯前端本地执行文本分词并推理生成 384 维向量；与 IndexedDB 预存的文档向量集进行点积比对，实现**零服务器依赖、零成本、毫秒级且百分之百保护隐私**的本地知识库检索（Client-side RAG）。

---

### 详细回答

#### 1. 为什么要在前端做本地向量化？
- **隐私保护**：用户本地敏感笔记、密码文本完全不出浏览器；
- **零服务端成本**：分担大模型向量化 API 的调用费用；
- **离线可用**：在无网络环境下依然支持本地智能语义搜索。

#### 2. 三步实现流水线
1. **模型加载与缓存**：
   下载量化为 8 位的轻量模型（体积约 20MB），由浏览器 CacheStorage 或 IndexedDB 永久缓存；
2. **文本转向量（Inference）**：
   使用 `@xenova/transformers`（封装了 ONNX Runtime Web）：
   ```javascript
   const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
   const output = await extractor('如何做性能优化', { pooling: 'mean', normalize: true });
   const queryVector = output.data; // Float32Array
   ```
3. **向量检索（余弦相似度）**：
   遍历本地知识库向量，计算向量点积：$\cos(	heta) = \sum A_i B_i$，降序返回 Top K 相关片段。

---

### 核心代码片段（极简记法）

```javascript
// 向量归一化后的点积即为余弦相似度
function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
  }
  return dotProduct;
}

// 快速匹配本地文档 Top K
function searchTopK(queryVec, docVectors, k = 3) {
  return docVectors
    .map(doc => ({ ...doc, score: cosineSimilarity(queryVec, doc.vector) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}
```

---

### 面试加分项

- **WebGPU 加速**：ONNX Runtime Web 支持指定执行提供者为 WebGPU（`executionProviders: ['webgpu']`），在支持的浏览器上向量推理耗时可从 WASM 的 100ms 骤降至 10ms 以内。
