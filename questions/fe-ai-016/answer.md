### 一句话总结

流式缓存采用**“内存 Buffer 批量聚合 + IndexedDB 增量 Append + 版本化快照”**。生成过程中按时间窗口（如每 2 秒）或 Token 阈值批量向 IndexedDB 写入增量 Chunk，会话完成写入 Final 完整实体；刷新或断网时从 IndexedDB 瞬间读取断点，实现毫秒级会话复原。

---

### 详细回答

#### 1. 为什么不用 localStorage 而用 IndexedDB？
- **容量上限**：localStorage 只有 5MB，长文本多轮对话几天就占满报错；
- **异步非阻塞**：localStorage 读写是同步阻塞主线程的，高频写入会直接拖慢 UI 帧率；IndexedDB 完全异步运行。

#### 2. 分段存储数据结构设计
- **`sessions` 存储表**：保存会话元数据（ID、标题、状态、最后更新时间）；
- **`chunks` 存储表**：复合索引 `[sessionId + seq]`，每条包含分段内容与时间戳。

#### 3. 性能优化：防抖写盘
- 严禁每个 Token 写一次 IndexedDB（事务创建极其频繁会卡死浏览器）；
- 维护一个内存 Buffer，每累积 50 个字符或每间隔 2 秒触发一次 `transaction.put` 批量写入。

---

### 核心代码片段（极简记法）

```javascript
let pendingBuffer = '';
let flushTimer = null;

function saveChunkToDB(sessionId, seq, delta) {
  pendingBuffer += delta;
  clearTimeout(flushTimer);

  flushTimer = setTimeout(async () => {
    const db = await openDB('AICache', 1);
    const tx = db.transaction('chunks', 'readwrite');
    tx.objectStore('chunks').put({
      id: `${sessionId}_${seq}`,
      sessionId,
      seq,
      text: pendingBuffer,
      time: Date.now()
    });
    pendingBuffer = '';
  }, 1000); // 1秒节流写入
}
```

---

### 面试加分项

- **LRU 淘汰与配额管理**：浏览器存储空间有限。设计冷数据淘汰机制：通过 `navigator.storage.estimate()` 监听配额，超限时清理 30 天以前的非收藏历史会话。
