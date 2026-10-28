### 一句话总结

长任务（Long Task）是指**在浏览器主线程上连续执行超过 50 毫秒的任何 JavaScript 任务**。统计标准是利用浏览器原生提供的 **`PerformanceObserver` 监听 `longtask` 条目类型**；通过采集长任务的耗时（`duration`）、发生起点（`startTime`）与归属容器（`attribution`），在上报监控平台后用于量化页面卡顿与计算 TBT（总阻塞时间）指标。

---

### 详细回答

#### 1. 为什么 50ms 是长任务的分水岭？
- 根据 Google RAIL 性能模型，人脑对 100ms 以内的交互无感知；
- 浏览器为了保证在用户点击或按键后能在 100ms 内给出视觉反馈，留给主线程响应交互的时间大约是 50ms；
- 若单个 JS 任务霸占主线程超过 50ms，用户的输入事件就会排队等待，引发明显掉帧卡顿。

#### 2. PerformanceObserver 核心采集
- 实例监听 `entryTypes: ['longtask']`；
- 每个 entry 返回字段：
  - `entry.duration`：阻塞主线程的总耗时（单位毫秒）；
  - `entry.startTime`：相对于 `timeOrigin` 的发生时间戳；
  - `entry.attribution`：指示长任务是来源于主页面还是某个特定的 `iframe`。

#### 3. 计算核心指标：TBT（Total Blocking Time）
- 每一个长任务超出 50ms 的部分被称为阻塞时间：$	ext{BlockingTime} = 	ext{duration} - 50$；
- 在 FCP 到 TTI 之间所有长任务的阻塞时间累加和，即为衡量首屏流畅度的核心指标 TBT。

---

### 核心代码片段（极简记法）

```javascript
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.warn(`检测到长任务！耗时: ${entry.duration.toFixed(2)}ms`);
    // 异步上报监控服务
    reportMetric('LONG_TASK', {
      duration: entry.duration,
      startTime: entry.startTime,
      name: entry.name
    });
  }
});

// 开始监听长任务
observer.observe({ entryTypes: ['longtask'] });
```

---

### 面试加分项

- **长任务定位到源码调用栈（Long Animation Frames API）**：`longtask` 无法获知具体的 JS 函数名。Chrome 123+ 推出了全新的 **LoAF（Long Animation Frames）API**（`entryTypes: ['long-animation-frame']`），能精准采集到具体是哪一个 JS 脚本文件、哪一行代码函数的执行造成了长任务，堪称前端卡顿治理神器。
