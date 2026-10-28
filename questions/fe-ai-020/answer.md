### 一句话总结

语音同步朗读采用**“标点断句缓冲区（Sentence Splitter Buffer） + 音频切片队列（Audio Chunk Queue） + Web Audio API 调度”**。流式文本按标点（`。！？
`）实时切分为完整句子，异步请求 TTS 生成音频并压入播放队列；利用音频时长与高亮索引实现文字光标跟随，配合 `AudioContext` 精准控制暂停、恢复与打断。

---

### 详细回答

#### 1. 核心难点：为什么不能逐字朗读？
- 语音合成（TTS）必须以**完整语义句子**为最小输入单位，单字合成完全没有声调抑扬顿挫，机械感极强；
- 因此必须在前端实现“流式断句缓冲”。

#### 2. 断句与异步流水线设计
1. **分句检测**：当文本流中出现中英文句末标点（`。 ! ? ; 
`）时，将前面的一整句截出作为一个独立语音任务；
2. **并发预加载**：当前句正在播放时，后台并发请求下一句的 TTS 音频流，实现无缝衔接，消除卡顿；
3. **视觉字音对齐**：根据各分句在整段文本中的起止偏移量（`startIndex`, `endIndex`），在播放该句音频时为对应 DOM 节点添加高亮背景或下划线。

---

### 核心代码片段（极简记法）

```javascript
let textBuffer = '';
const audioQueue = [];

function onTokenReceive(token) {
  textBuffer += token;
  // 匹配句子结束标点
  const match = textBuffer.match(/^([\s\S]+?[。！？；
])([\s\S]*)$/);
  if (match) {
    const sentence = match[1];
    textBuffer = match[2]; // 剩余部分继续累加
    queueTTSPlayback(sentence);
  }
}

async function queueTTSPlayback(sentence) {
  const audioBlob = await fetchTTSAudio(sentence);
  audioQueue.push(audioBlob);
  if (!isPlaying) playNextAudio();
}
```

---

### 面试加分项

- **用户主动跳过与打断（Stop & Flush）**：用户点击“停止朗读”或直接提问新问题时，必须执行三清操作：
  1. 调用 `audioElement.pause()` 停止当前播放；
  2. 清空 `audioQueue` 队列中的所有后续音频；
  3. 通过 `AbortController` 取消正在后台请求的所有未决 TTS 网络接口。
