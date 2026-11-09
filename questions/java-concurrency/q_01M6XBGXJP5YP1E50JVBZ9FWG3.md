---
id: q_01M6XBGXJP5YP1E50JVBZ9FWG3
title: 线程池满了以后，新提交的任务怎么处理？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-pool]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
队列满了、线程数也到了最大值，新任务就交给拒绝策略（RejectedExecutionHandler）处理；默认策略是直接抛出 RejectedExecutionException。

## 要点
- [kp1|3] 触发条件：队列已满，且线程数已达最大线程数
- [kp2|3] 默认策略 AbortPolicy：抛出 RejectedExecutionException
- [kp3|2] 线程池关闭后再提交任务，同样会走拒绝策略
- [kp4] 可通过构造器传入 handler，或自己实现接口定制处理

## 详解
### 先搞懂：餐厅爆满以后
餐厅等位区坐满了，服务员也都在忙，再来的客人怎么办？可以直接告诉他「今天满了」，也可以让他自己端盘子，也可以把等得最久的客人请走，给新客人让位。不同做法，就是不同的拒绝策略。

后文术语：

- **拒绝策略**：线程池无法接收新任务时的处理方式。
- **RejectedExecutionHandler**：拒绝策略的接口，只有一个方法 `rejectedExecution`。

### 什么时候会触发拒绝
- 线程池正常运行，但任务队列已满，线程数也已经到最大线程数；
- 线程池已经调用了 `shutdown()` 或 `shutdownNow()`，再提交的任务也会被拒绝。

### 默认怎么处理：AbortPolicy
不指定时，线程池使用 `AbortPolicy`，直接抛出 `RejectedExecutionException`。调用方能马上知道任务没有被接收，可以捕获异常后做补救，比如记录日志、重试或返回错误给用户。

### 其他的处理方式
JDK 还提供另外三种，下一道题会逐个对比场景：

- `CallerRunsPolicy`：由提交任务的线程自己执行；
- `DiscardPolicy`：悄悄丢弃；
- `DiscardOldestPolicy`：丢掉队列里最老的任务，再尝试提交新任务。

也可以自己实现 `RejectedExecutionHandler`，比如把任务存到数据库、发告警，稍后再处理。

## 示例
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        1, 1, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(1),
        (task, executor) -> {
            // 自定义策略：记录并抛出异常
            System.err.println("任务被拒绝：" + task);
            throw new RejectedExecutionException("线程池已满");
        });
```

## 易错点
- 以为任务提交后一定会执行；被拒绝的任务不会运行
- 以为拒绝只发生在线程池满的时候；池关闭后提交也会被拒绝
- 没捕获 RejectedExecutionException；业务入口可能直接报错

## 追问
### [f1] 线程池满了，怎么避免任务丢失？
可以使用 `CallerRunsPolicy` 让提交线程自己执行，减慢提交速度；或者自定义策略，把任务持久化到队列或数据库，等线程池空闲后再处理。

### [f2] 怎么知道线程池正在拒绝任务？
可以在自定义 handler 里统计拒绝次数并上报监控，也可以观察队列长度和活跃线程数是否长期打满。
