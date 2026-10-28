## 追问 1：如果大模型正在推流时由于用户网络断开导致报错，如何防止 Sentry 产生海量无意义的网络噪点报警？

**回答要点**：
在 `ignoreErrors` 列表中配置过滤规则，或者在 `beforeSend` 中检查 `err.name === 'AbortError'` 或包含 `Failed to fetch` 且当前 `navigator.onLine === false`，判定为用户主动取消或断网事件，直接丢弃（返回 `null`），不占用 Sentry 配额。

---

## 追问 2：Sentry 录制的会话回放（Session Replay）在多轮长对话中会导致流量过大吗？

**回答要点**：
全量录制会导致体积过大。
生产中推荐采用 **`replaysOnErrorSampleRate: 1.0` + `replaysSessionSampleRate: 0.05`** 策略：正常会话仅低采样率抽查，只有在发生严重代码崩溃时才完整抓取崩溃前后 1 分钟的 DOM 录屏回放。
