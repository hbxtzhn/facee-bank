### 一句话总结

事件驱动架构采用**“发布-订阅（Pub/Sub）事件总线”**切断输入框、网络请求引擎、Markdown 渲染器、TTS 语音播报模块之间的直接硬编码耦合。各模块仅对总线广播领域事件（如 `PROMPT_SUBMITTED`、`STREAM_CHUNK`、`GENERATION_FINISHED`）并监听自己关心的事件，实现模块间**高内聚、零依赖、自由拔插**。

---

### 详细回答

#### 1. 传统紧耦合调用的痛点
- 输入框组件在点击提交时，直接调用请求函数、直接更新消息 Store、直接触发滚动条滚动、直接启动 TTS 播放；
- 输入框组件代码迅速膨胀至上千行，牵一发而动全身。

#### 2. 事件总线解耦方案
- **模块 A（输入框）**：只做一件事——捕获用户敲击回车，广播 `bus.emit('ai:submit', { prompt })`；
- **模块 B（流式网络层）**：监听到 `ai:submit`，拉起 Fetch 流，不断向总线广播 `ai:chunk`；
- **模块 C（TTS 语音模块）**：独立监听到 `ai:chunk`，在后台静默做断句合成语音，完全不需要输入框知晓其存在。

---

### 核心代码片段（极简记法）

```javascript
import mitt from 'mitt';

// 1. 全局领域事件总线（利用 mitt 极致轻量）
export const aiBus = mitt();

// 2. 网络层：监听提交，广播流式数据
aiBus.on('ai:submit', async ({ prompt }) => {
  const stream = await fetchStream(prompt);
  for await (const chunk of stream) {
    aiBus.emit('ai:chunk', { delta: chunk });
  }
  aiBus.emit('ai:done');
});

// 3. 消费端（如语音合成）：按需订阅，彻底解耦
aiBus.on('ai:chunk', ({ delta }) => audioSpeaker.feed(delta));
```

---

### 面试加分项

- **TypeScript 类型强约束事件名与参数**：利用泛型类型 `mitt<EventsMap>`，防止事件名手误敲错或载荷数据类型不匹配，兼顾解耦与静态安全。
