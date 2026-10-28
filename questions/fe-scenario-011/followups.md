## 追问 1：如何计算超大文件的 MD5 避免前端内存溢出崩溃？

**回答要点**：
不能直接读取整个文件 `readAsArrayBuffer(file)`。
必须使用 `FileReader` 配合 `file.slice()` 分块流式读取，结合 `spark-md5` 的 `spark.append()` 逐块累加计算 Hash，并在 Web Worker 中执行。

---

## 追问 2：抽样 Hash（Sampling Hash）是怎么做到秒算几十 GB 文件指纹的？

**回答要点**：
大文件仅提取特定特征块：文件头部 2MB、尾部 2MB、以及中间均匀抽取 10 个 100KB 切片，将这些特征块拼接计算 Hash，准确率达 99.999% 且能在 1 秒内算完。
