### 一句话总结

AI 乐观更新的核心是**“临时占位实体（Optimistic Entity） + 状态平滑过渡 + 失败无痕回滚”**。用户点击发送瞬间，UI 立即挂载一条带临时 ID 的 Assistant 占位消息并展示骨架打字动效；当首个流式 Chunk 到达时无缝将占位态转为真实生成态；若遇接口限流或报错，则自动将该条消息标记为失败并保留重发按钮。

---

### 详细回答

#### 1. 为什么 AI 场景极度需要乐观更新？
- 大模型存在较长的首字延迟（TTFT，通常 1~3 秒）；
- 若没有乐观更新，用户点击“发送”后输入框被清空，但界面毫无反应，用户会误以为卡死而频繁重复点击。

#### 2. 三阶段生命周期
1. **即时乐观呈现（0ms）**：
   - 用户消息立即入队；
   - 插入一条 `{ id: 'temp_assistant', content: '', status: 'pending' }`，界面渲染脉冲波或打字光标；
2. **渐进式覆写（首字到达）**：
   - 将 `status` 切为 `'streaming'`，用服务端返回的真实 `messageId` 替换临时 ID；
   - 逐字追加内容；
3. **异常回滚（Rollback）**：
   - 若遇到 500/429 报错，将该消息切换为错误卡片，用户输入的文字自动放回输入框或提供“一键重试”。

---

### 核心代码片段（极简记法）

```javascript
function sendPrompt(prompt) {
  const tempUserMsg = { id: Date.now(), role: 'user', content: prompt };
  const tempAiMsg = { id: `temp_${Date.now()}`, role: 'assistant', content: '', isOptimistic: true };

  // 1. 立即更新 UI
  setMessages(prev => [...prev, tempUserMsg, tempAiMsg]);

  // 2. 发起请求并流式修正
  fetchStream(prompt, {
    onFirstChunk: (realId) => {
      // 替换真实 ID
      updateMessage(tempAiMsg.id, { id: realId, isOptimistic: false });
    },
    onChunk: (delta) => appendChunk(delta),
    onError: () => markMessageFailed(tempAiMsg.id)
  });
}
```

---

### 面试加分项

- **微动效协同**：乐观更新不仅仅是塞一条空数据，配合 CSS 缓动动画让输入框文字飞入消息流，消除感知延迟。
