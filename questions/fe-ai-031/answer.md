### 一句话总结

万条级前端搜索的核心是**“前端轻量倒排索引（Inverted Index，如 FlexSearch / MiniSearch） + Web Worker 离线建立 + 虚拟滚动展示”**。利用分词算法在后台线程预先构建倒排索引字典，关键词检索由 $O(N)$ 遍历降至 $O(1)$ 查找，结合位运算复合过滤，在 10 毫秒内完成万级文本匹配。

---

### 详细回答

#### 1. 为什么原生的 `array.filter(m => m.includes(kw))` 会卡死？
- 10,000 条长文本对话包含数百万字符；
- 用户在搜索框每敲一个字都执行一次全量字符串正则匹配，主线程瞬间卡死几百毫秒，输入严重掉帧。

#### 2. 倒排索引构建架构
- **分词（Tokenization）**：对消息正文分词（英文分词空格，中文结合 N-gram 算法切分为二字词元）；
- **字典构建**：建立 `Map<Term, Set<MessageId>>`；
- **交集计算**：当搜索“React 性能优化”时，分别查出 `React` 和 `性能优化` 的 ID 集合，执行 Set 交集操作即可毫秒级锁定目标。

---

### 核心代码片段（极简记法）

```javascript
import MiniSearch from 'minisearch';

// 1. 初始化全文索引
const miniSearch = new MiniSearch({
  fields: ['content'], // 检索字段
  storeFields: ['id', 'role', 'timestamp']
});

// 2. 批量建索引（移入 Web Worker 执行更佳）
miniSearch.addAll(allMessages);

// 3. 毫秒级搜索
const results = miniSearch.search('流式渲染', {
  filter: (item) => item.timestamp >= startTime // 支持复合过滤
});
```

---

### 面试加分项

- **搜索高亮零回流实现**：匹配到关键词后，使用浏览器原生的 **CSS Custom Highlight API**（`CSS.highlights.set()`）进行高亮，完全无需改动任何 DOM 节点结构，彻底消除因内嵌 `<mark>` 标签导致的频繁重排。
