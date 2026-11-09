---
id: q_01M6XBP4NN4GG2BD6WF4TC6KDV
title: 常见阻塞队列有哪些，各自有什么区别？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [thread-pool, collections]
prerequisites: [q_01M6XBGX1MD0HRTZMCXDBB3PXV]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "JDK 21 API：LinkedBlockingQueue", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/LinkedBlockingQueue.html" }
  - { title: "JDK 21 API：PriorityBlockingQueue", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/PriorityBlockingQueue.html" }
  - { title: "JDK 21 API：ThreadPoolExecutor（Queuing 一节）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html" }
estimatedMinutes: 3
---

## 一句话
常见的有数组有界队列、链表队列（默认几乎无界）、按优先级的无界队列，以及不存任务的直接交接队列。

## 要点
- [kp1|3] ArrayBlockingQueue：底层数组，容量固定，先进先出
- [kp2|3] LinkedBlockingQueue：底层链表，不指定容量时默认是 Integer.MAX_VALUE，相当于无界
- [kp3|2] PriorityBlockingQueue：无界，按优先级而不是先后顺序出队
- [kp4|2] SynchronousQueue：不存元素，放入必须等有线程来取

## 详解
### 先搞懂：不同的排队方式
线程池的任务队列，像不同的取号机：有的只有 10 个号位，满了就不给号（有界）；有的号位几乎取不完（实际无界）；有的按 VIP 等级叫号，不管先来后到（优先级）；还有的根本不排队，必须当面交给窗口里正在等的人（直接交接）。

后文术语：

- **有界队列**：容量固定，满了就放不进去。
- **无界队列**：理论上没有容量限制，会一直堆积到内存耗尽。
- **FIFO**：先进先出。

### 方案对比：几种常见阻塞队列
| 队列 | 底层结构 | 容量 | 出队顺序 | 适合场景 |
|---|---|---|---|---|
| ArrayBlockingQueue | 数组 | 必须指定，有界 | 先进先出 | 固定大小的线程池，想控制积压 |
| LinkedBlockingQueue | 链表 | 可指定；不指定默认 Integer.MAX_VALUE | 先进先出 | 任务量可控；建议指定容量 |
| PriorityBlockingQueue | 堆（数组） | 无界 | 按优先级 | 任务有轻重缓急 |
| SynchronousQueue | 无存储 | 容量为 0 | 直接交接 | 任务多而短，配合很大的最大线程数 |
| DelayQueue | 文档未规定 | 无界 | 按到期时间 | 延迟执行的任务 |

结论：线程池默认选带容量上限的 ArrayBlockingQueue 或指定了容量的 LinkedBlockingQueue；需要优先级才用 PriorityBlockingQueue，并留意它无界。

### 几个要点
**ArrayBlockingQueue**：创建时必须给容量，之后不能改。满了就放不进去，能防止积压。

**LinkedBlockingQueue**：容量是可选的。不写容量就几乎无界，配 `newFixedThreadPool` 时任务堆积可能耗尽内存，生产中要写上容量。

**PriorityBlockingQueue**：任务要实现 `Comparable` 或者传入比较器。无界，所以线程数最多只会涨到核心数。优先级相同的任务，出队顺序不保证先进先出。

**SynchronousQueue**：没有容量，`offer` 只在有线程正等着取时才成功。线程池里用它，相当于「不排队，没有空闲线程就扩线程」，`newCachedThreadPool` 就是这样。

## 示例
```java
// 有界，容量 100
BlockingQueue<Runnable> q1 = new ArrayBlockingQueue<>(100);
// 链表，显式指定容量
BlockingQueue<Runnable> q2 = new LinkedBlockingQueue<>(100);
// 不指定容量：几乎无界，要小心
BlockingQueue<Runnable> q3 = new LinkedBlockingQueue<>();
```

## 易错点
- 以为 LinkedBlockingQueue 一定有界；不指定容量时默认是 Integer.MAX_VALUE
- 用无界队列又期待线程扩到最大值；队列不会满，最大线程数用不上
- 以为 PriorityBlockingQueue 里相同优先级的任务一定先进先出；顺序不保证

## 追问
### [f1] ArrayBlockingQueue 和 LinkedBlockingQueue 怎么选？
需要严格限制积压，选 ArrayBlockingQueue；用 LinkedBlockingQueue 时务必指定容量。两者都是先进先出。

### [f2] newCachedThreadPool 为什么用 SynchronousQueue？
它希望任务不排队，没有空闲线程就立刻新建线程，所以用不存任务的 SynchronousQueue，代价是线程数可能暴涨。
