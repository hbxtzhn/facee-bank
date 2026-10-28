## 追问 1：前端如何判断当前浏览器是否支持 WASM SIMD？

**回答要点**：
基于特性探测：尝试编译一段最小的包含 SIMD 字节码的操作片段 `WebAssembly.validate(simdBytes)`；若返回 `true` 则动态加载 SIMD 优化包，否则加载纯通用回退 WASM 包。

---

## 追问 2：WASM 模块体积通常较大（几 MB），如何优化加载白屏？

**回答要点**：
1. 开启 Brotli / Gzip 压缩；
2. 利用 `WebAssembly.instantiateStreaming` 边下载边编译，跳过等待完整下载后再编译的串行延迟；
3. 将 WASM 模块编译产物缓存至 IndexedDB 中。
