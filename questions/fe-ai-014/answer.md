### 一句话总结

优先级流式队列采用**“有限并发池 + 优先级大顶堆 + 动态抢占式 Abort 机制”**。当高优先级任务入队且并发已满时，通过绑定的 `AbortController` 暂停或中断正在运行的低优先级任务并将其回填回待执行队列，立即将网络与计算资源让位给高优先级任务。

---

### 详细回答

#### 1. 为什么普通 FIFO 队列无法满足需求？
- 普通队列遵循先入先出，若用户先发起了耗时 30 秒的“全文翻译”，紧接着发起了紧急的“修复代码报错”，代码任务只能干等 30 秒；
- 浏览器同域名并发通道有限，多流并行会导致互相抢带宽严重卡顿。

#### 2. 调度器核心要素
- **Priority PriorityQueue**：根据任务权重排序（High = 3, Normal = 2, Low = 1）；
- **抢占模式（Preemption）**：
  - 判定：当前活动任务的优先级若低于新入队任务；
  - 动作：触发当前任务的 `abortController.abort()`，保存其中断状态（以便后续断点恢复），立即调度高优先级任务启动。

---

### 核心代码片段（极简记法）

```javascript
class PriorityStreamScheduler {
  constructor(maxConcurrent = 1) {
    this.maxConcurrent = maxConcurrent;
    this.running = [];
    this.queue = []; // 按 priority 降序
  }

  add(task) {
    this.queue.push(task);
    this.queue.sort((a, b) => b.priority - a.priority);
    this.schedule();
  }

  schedule() {
    // 抢占逻辑：若队列头部任务优先级 > 正在运行任务的最低优先级
    if (this.running.length >= this.maxConcurrent) {
      const lowestRunning = this.running.sort((a, b) => a.priority - b.priority)[0];
      const highestPending = this.queue[0];
      if (highestPending && highestPending.priority > lowestRunning.priority) {
        lowestRunning.abort(); // 掐断低优先级
      }
      return;
    }

    const nextTask = this.queue.shift();
    if (nextTask) {
      this.running.push(nextTask);
      nextTask.run().finally(() => {
        this.running = this.running.filter(t => t !== nextTask);
        this.schedule();
      });
    }
  }
}
```

---

### 面试加分项

- **支持断点暂停而不是废弃**：被抢占的低优先级任务不是直接销毁，而是记录当前的 `lastEventId` 并重新塞入队列头部。当高优先级任务完成后，低优先级任务自动发起断点续传。
