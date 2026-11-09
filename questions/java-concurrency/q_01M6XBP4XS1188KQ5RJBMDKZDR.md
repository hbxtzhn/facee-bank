---
id: q_01M6XBP4XS1188KQ5RJBMDKZDR
title: 线程池用完后怎么关闭？
type: concept
difficulty: easy
importance: 1
category: java-concurrency
tags: [thread-pool]
appliesTo: ["Java >= 19（close 方法）"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`shutdown()` 不再收新任务、把已提交的做完；`shutdownNow()` 尝试中断运行中的任务，并返回没执行的任务。

## 要点
- [kp1|3] `shutdown()` 不再接收新任务，队列里的任务会继续执行完
- [kp2|3] `shutdownNow()` 尝试中断正在执行的任务，返回未执行的任务列表
- [kp3|2] 两个方法都不等待，要等结束需调用 `awaitTermination`
- [kp4] 线程池不关闭，非守护的工作线程会让 JVM 迟迟无法退出

## 详解
### 先搞懂：餐厅打烊
餐厅打烊有两种方式：一种是门口挂牌「不再接客」，但已经坐下的客人和等位的客人都照常服务完（温和）；另一种是直接让客人别吃了，厨房停工，把没做的单子交还给老板（强制）。线程池关闭对应这两种。

后文术语：

- **中断**：给线程发一个「请你停下」的信号，线程需要自己响应，不是强行杀死。
- **守护线程**：不阻止 JVM 退出的后台线程；线程池的默认线程不是守护线程。

### shutdown：温和关闭
调用后，线程池进入 SHUTDOWN 状态：

- 不再接收新任务，再提交会被拒绝；
- 已经在执行的任务继续跑；
- 队列里等待的任务也会继续被执行；
- 全部完成后，线程池终止。

调用 `shutdown()` 后立刻返回，不会等待任务执行完。

### shutdownNow：强制关闭
调用后，线程池进入 STOP 状态：

- 不再接收新任务；
- 向正在执行任务的线程发送中断信号；
- 把队列里还没开始的任务取出，作为 `List<Runnable>` 返回。

注意中断只是通知，任务如果不检查中断状态，或者忽略中断，仍然会继续跑。

### 推荐写法：先温和后强制
1. 调用 `shutdown()`；
2. 用 `awaitTermination(时间)` 等一段时间；
3. 超时还没结束，再调用 `shutdownNow()`。

### 进阶：Java 19 之后（基础薄弱可先跳过）
Java 19 起 `ExecutorService` 实现了 `AutoCloseable`，可以用 try-with-resources，`close()` 会先 `shutdown()`，再等待任务完成。

## 示例
```java
pool.shutdown(); // 不再接收新任务
try {
    if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
        List<Runnable> pending = pool.shutdownNow(); // 强制关闭，拿回未执行的任务
    }
} catch (InterruptedException e) {
    pool.shutdownNow();
    Thread.currentThread().interrupt();
}
```

## 易错点
- 以为 `shutdown()` 会等任务执行完再返回；它立即返回，要等结束需用 `awaitTermination`
- 以为 `shutdownNow()` 一定能停掉任务；不响应中断的任务仍会继续
- 忘记关闭线程池；非守护工作线程会让程序无法正常退出

## 追问
### [f1] 关闭后再提交任务会怎样？
会走拒绝策略，默认抛出 `RejectedExecutionException`。

### [f2] shutdownNow 返回的任务该怎么处理？
这些是还没开始执行的任务，可以记录日志，或保存下来在重启后再次提交，避免任务丢失。
