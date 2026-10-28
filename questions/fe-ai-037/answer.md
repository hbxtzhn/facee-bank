### 一句话总结

实时语音采样的核心是**“用 `AudioWorklet` 取代已废弃的 `ScriptProcessorNode`”**。在独立的音频渲染线程中采集麦克风 PCM 原始流，完成**降采样（如 48kHz 转 16kHz）、单声道转换与 VAD 静音切除**；仅在检测到有效人声时通过二进制 WebSocket 发往后端模型，大幅节省网络与前端 CPU 占用。

---

### 详细回答

#### 1. 为什么严禁使用 ScriptProcessorNode？
- `ScriptProcessorNode` 在主线程执行音频回调，若主线程有复杂 DOM 重绘或 JS 计算，音频回调会被阻塞导致**破音、音频数据丢帧（Audio Glitch）**；
- 现代 W3C 标准已强制由 `AudioWorklet` 替代。

#### 2. AudioWorklet 独立音频线程优势
- 运行在与 UI 完全隔离的高优先级音频线程中，延迟低至几毫秒，不受主线程渲染和卡顿影响；
- 内部处理 128 采样点帧切片。

#### 3. 前端 VAD（语音活动检测，Voice Activity Detection）
- 若麦克风一直开启，无声环境也会持续产生大量的音频数据包发往服务端计费；
- 前端计算短时能量和零交叉率，未说话期间不发包，检测到人声瞬间启动推流。

---

### 核心代码片段（极简记法）

```javascript
// 注册并连接 AudioWorklet
const audioContext = new AudioContext({ sampleRate: 16000 });
await audioContext.audioWorklet.addModule('pcm-processor.js');

const source = audioContext.createMediaStreamSource(micStream);
const workletNode = new AudioWorkletNode(audioContext, 'pcm-processor');

// 接收来自独立音频线程转换好的 16kHz PCM 数据
workletNode.port.onmessage = (e) => {
  const pcmChunk = e.data; // ArrayBuffer
  websocket.send(pcmChunk);
};

source.connect(workletNode);
```

---

### 面试加分项

- **移动端用户手势激活限制**：指出 `AudioContext` 必须在用户直接触发的事件（如 `onClick`）中调用 `audioContext.resume()` 解冻，否则在 iOS Safari 上会被浏览器直接挂起处于 `suspended` 状态无法录音。
