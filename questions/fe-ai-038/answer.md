### 一句话总结

调度器核心基于 **“浏览器原生 `scheduler.postTask` API 或宏微任务切片分级队列”**。将 UI 任务划分为 **`user-blocking`（最高优：点击打字即时响应）**、**`user-visible`（次高优：输入框光标）** 与 **`background`（最低优：大段流式 Markdown 格式化）**；利用时间切片在每帧空闲时执行低优先级任务，一旦有用户交互到达立即让出主线程。

---

### 详细回答

#### 1. 优先级三级划分模型
- **Immediate（不可中断）**：输入框 onChange、点击“停止生成”按钮、弹窗关闭；
- **Normal（平滑渲染）**：当前正在输入的纯字符渲染；
- **Background（延后计算）**：代码语法高亮计算、KaTeX 数学公式渲染、历史消息自动持久化存储。

#### 2. 原生 Scheduler API 驱动
```javascript
// 最高优先级（立即抢占执行）
scheduler.postTask(urgentTask, { priority: 'user-blocking' });

// 最低优先级（闲时执行）
scheduler.postTask(heavyHighlightTask, { priority: 'background' });
```

#### 3. 降级兼容机制：MessageChannel + requestIdleCallback
- 不支持原生 scheduler 的浏览器，使用 `MessageChannel` 模拟宏任务调度，结合 `performance.now()` 计算单帧已用时间，若耗时超过 5ms 主动 `yield` 让出控制权。

---

### 核心代码片段（极简记法）

```javascript
class RenderScheduler {
  scheduleHeavyTask(taskFn) {
    if ('scheduler' in window) {
      return window.scheduler.postTask(taskFn, { priority: 'background' });
    }
    // 降级使用 requestIdleCallback
    return new Promise(resolve => {
      requestIdleCallback(deadline => {
        resolve(taskFn());
      });
    });
  }
}
```

---

### 面试加分项

- **`scheduler.yield()` 现代时间切片 API**：Chrome 129+ 推出的全新标准，允许长任务内部像写普通代码一样 `await scheduler.yield()`，优雅暂停并让出主线程给点击事件插队，之后再自动恢复执行。
