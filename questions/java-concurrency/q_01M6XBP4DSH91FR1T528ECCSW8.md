---
id: q_01M6XBP4DSH91FR1T528ECCSW8
title: 四种拒绝策略各适合什么场景？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [thread-pool]
prerequisites: [q_01M6XBGXJP5YP1E50JVBZ9FWG3]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "JDK 21 API：ThreadPoolExecutor（Core and maximum pool sizes / Queuing / Rejected tasks / Keep-alive times）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html" }
estimatedMinutes: 3
---

## 一句话
四种策略分别是抛异常、提交线程自己执行、直接丢弃、丢最老任务；任务不能丢时选前两种。

## 要点
- [kp1|3] AbortPolicy 抛 RejectedExecutionException，是默认策略
- [kp2|3] CallerRunsPolicy 由提交线程自己执行，起到降低提交速度的作用
- [kp3|2] DiscardPolicy 直接丢弃新任务，没有任何提示
- [kp4|2] DiscardOldestPolicy 丢弃队头最老的任务，再重试提交新任务

## 详解
### 先搞懂：爆满的餐厅有四种应对
餐厅满了，老板有四种做法：直接告诉客人今天满了（报错）；让客人自己端盘子（自己干）；悄悄不理新客人（丢弃）；把等得最久的客人请走给新客人腾位置（丢最老）。哪种合适，要看这家店是怎么做生意的。

线程池也一样，没有哪种策略永远最好，关键是任务丢了会怎么样。后文术语：

- **拒绝策略**：队列满、线程数也到最大值时，对新任务的处理方式。
- **背压**：下游处理不过来时，让上游放慢速度的机制。

### 方案对比：四种策略
| 策略 | 做法 | 任务会丢吗 | 适合场景 | 注意点 |
|---|---|---|---|---|
| AbortPolicy | 抛出 RejectedExecutionException | 新任务被拒，调用方能感知 | 任务重要，需要调用方处理失败 | 要捕获异常，否则直接报错 |
| CallerRunsPolicy | 提交线程自己执行任务 | 一般不丢 | 不能丢、可以接受提交变慢 | 提交线程被占用，可能影响它的其他工作 |
| DiscardPolicy | 直接丢弃新任务 | 丢，且没有异常 | 可有可无的任务，如统计、日志 | 丢了也不知道，慎用 |
| DiscardOldestPolicy | 丢队头最老任务，再提交新任务 | 丢旧任务 | 新任务比旧任务更有价值，如刷新最新状态 | 被丢的旧任务可能是重要的 |

结论：默认用 AbortPolicy，让失败显式暴露；任务不能丢又能接受变慢时选 CallerRunsPolicy；只有任务确实可丢，才考虑 Discard 系列。

### 每种策略细讲
**AbortPolicy**：抛异常，调用方可以捕获后记录日志、重试或返回提示。好处是失败是明确的。

**CallerRunsPolicy**：谁提交谁执行。提交线程忙着执行任务，就没法继续提交新任务，等于自动降低了提交速度。但如果提交线程是处理请求的关键线程，它被占用，会拖慢整体响应。线程池已关闭时，任务会被丢弃而不是执行。

**DiscardPolicy**：什么都不做，任务消失。风险是业务根本不知道任务丢了，排查困难。

**DiscardOldestPolicy**：从队列头部取走最老的一个任务丢弃，再尝试重新提交新任务。适合「只关心最新」的场景。

## 示例
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        2, 4, 60, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(100),
        new ThreadPoolExecutor.CallerRunsPolicy()); // 换成其他策略只改最后一个参数
```

## 易错点
- 以为 DiscardPolicy 会打印日志；它什么都不做，任务悄悄消失
- 以为 CallerRunsPolicy 一定安全；提交线程被占用，可能拖慢它原本的工作
- 以为 DiscardOldestPolicy 丢的是最先提交的任务；它丢的是队列头部的任务，队列为优先级队列时头部不是最老

## 追问
### [f1] 四种策略都不满意怎么办？
可以自己实现 `RejectedExecutionHandler`，例如把任务写入数据库或消息队列，稍后重试，同时上报告警。

### [f2] CallerRunsPolicy 为什么说能减缓压力？
提交线程自己执行任务时，没空继续提交新任务，上游的提交速度被拖慢，给线程池消化积压的时间。
