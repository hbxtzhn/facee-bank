### 一句话总结

前端降低 Token 成本的核心是**“把关输入入口 + 会话上下文智能裁剪 + 本地结果去重缓存”**。通过 **Prompt 客户端去空格精简**、**滑动窗口截断历史轮次**、**向量相似度命中直接走前端本地缓存**，以及**防抖避免无效提问**，在网络请求发出前拦下 30%~50% 的不必要 Token 消耗。

---

### 详细回答

#### 1. 会话上下文滑动窗口（Sliding Window）
- 多轮对话如果将 50 轮历史无脑发给后端，Token 呈二次方级爆炸；
- 前端维护滑动窗口：只携带**系统 Prompt（System Role） + 最近 4~6 轮对话**；超出的历史消息自动在前端折叠，或前端调用本地小模型做轻量摘要后发送。

#### 2. 本地相似度缓存（Semantic Cache）
- 对用户提问在本地计算 Hash 或向量检索；
- 若用户问了与 5 分钟前完全相同或语义相似度 > 0.98 的问题，直接调取 IndexedDB 缓存的旧回答，提示“已从本地缓存秒级命中”，完全不发接口。

#### 3. 客户端 Prompt 清洗与压缩
- 过滤无效换行、冗余连续空格、剔除长文本中无关的 HTML/Markdown 样式标签；
- 上传代码文件时，前端预先剔除注释行和无意义的空格缩进后再喂给模型。

---

### 核心代码片段（极简记法）

```javascript
// 会话上下文滑动窗口控制
function prepareContextMessages(allMessages, maxRounds = 4) {
  const systemMsg = allMessages.find(m => m.role === 'system');
  const recentDialogs = allMessages.filter(m => m.role !== 'system').slice(-maxRounds * 2);

  // 始终保留 System Prompt，中间历史裁剪，只带最新多轮
  return systemMsg ? [systemMsg, ...recentDialogs] : recentDialogs;
}
```

---

### 面试加分项

- **预知 Token 计数提醒（Token Pre-flight Estimator）**：在用户输入框右下角利用轻量分词器动态展示“当前提问约消耗 120 Tokens”，当用户粘贴了数万字超长文本时弹出“建议开启自动浓缩模式”提醒，引导用户自发节约用量。
