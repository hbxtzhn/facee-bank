## 追问 1：前端如何实现麦克风回声消除（AEC）与降噪？

**回答要点**：
无需在 JS 手写算法！
在调用 `navigator.mediaDevices.getUserMedia()` 时，直接传入底层浏览器硬件级约束：
`{ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } }` 即可开启内置硬件回声抑制。

---

## 追问 2：AudioWorklet 线程与主线程之间如何高效传输音频二进制数据？

**回答要点**：
使用 `port.postMessage(pcmBuffer, [pcmBuffer.buffer])`，利用 **Transferable Objects** 将底层的 ArrayBuffer 所有权直接转移给主线程，实现真正的零拷贝内存交换。
