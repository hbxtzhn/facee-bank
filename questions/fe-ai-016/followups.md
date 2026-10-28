## 追问 1：如果用户多标签页打开同一个会话同时生成，IndexedDB 怎么防止数据覆盖混乱？

**回答要点**：
基于乐观锁或 BroadcastChannel 状态广播。在会话元数据中保存 `version` 字段，写入时校验版本号；或通过 Web Locks API（`navigator.locks.request`）获取会话排他锁，确保只有一个标签页能进行流式写入。

---

## 追问 2：IndexedDB 中的数据如何进行全文快速搜索？

**回答要点**：
可以在前端引入微型倒排索引库（如 `FlexSearch` 或 `MiniSearch`），在写入 IndexedDB 的同时更新内存索引字典，实现万条历史对话毫秒级关键词检索。
