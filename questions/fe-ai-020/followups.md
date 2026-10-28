## 追问 1：使用浏览器原生的 SpeechSynthesisUtterance（Web Speech API）有什么坑？

**回答要点**：
原生 Web Speech API 在长文本播放超过 15 秒时，Chrome 会出现静默停止播放的底层 Bug；且移动端 iOS Safari 必须由用户手势（Click）同步激活音频上下文才能发声。生产级严肃项目建议使用服务端 TTS（如 Edge-TTS 或 OpenAI TTS）。

---

## 追问 2：句与句衔接播放时有微小的静音断档，怎么消除？

**回答要点**：
利用 `Web Audio API` 的 `AudioBufferSourceNode` 双缓冲机制：在上一段音频即将结束的前 50ms（`audioContext.currentTime + duration`），预先调度启动下一段音频，实现零缝隙交叉淡入淡出（Cross-fade）。
