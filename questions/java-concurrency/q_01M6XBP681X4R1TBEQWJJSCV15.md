---
id: q_01M6XBP681X4R1TBEQWJJSCV15
title: synchronized 和 ReentrantLock 有什么区别？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [synchronized, aqs]
prerequisites: [q_01M6XBGYPJXM20MV9Q8KEXDR5P]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
两者都是可重入的互斥锁；synchronized 简单、自动释放，ReentrantLock 更灵活，支持超时、可中断、公平锁和多个条件队列。

## 要点
- [kp1|3] synchronized 是关键字，自动释放；ReentrantLock 要手动 unlock
- [kp2|3] ReentrantLock 支持 tryLock、超时获取、响应中断
- [kp3|2] ReentrantLock 可选公平锁；synchronized 只能是非公平
- [kp4|2] ReentrantLock 可以创建多个 Condition；synchronized 只有一个等待队列
- [kp5] 两者都可重入，简单场景优先用 synchronized

## 详解
### 先搞懂：自动门和手动门
假设你要进一间办公室。synchronized 像自动门：走进去门自动关，出来后自动打开，你不用管。ReentrantLock 像手动门：门锁在你手里，进去要自己锁，出来要自己开。

手动门的好处是花样多：可以敲门等一会儿就走（超时），等的时候可以被人叫走（中断），还能设置先来后到的排队规则（公平）。代价是出来时忘记开门，别人就永远进不来了。

后文用到的术语：

- **可重入**：同一个线程拿到锁后，再次要这把锁不会被自己卡住。
- **公平锁**：按排队先后分配锁；**非公平锁**允许新来的线程插队。
- **Condition**：配合锁使用的条件队列，用于线程之间等待和通知。
- **AQS**：JDK 里用来实现各种锁的基础框架，ReentrantLock 基于它实现。

### 逐项对比
| 对比项 | synchronized | ReentrantLock |
|---|---|---|
| 本质 | JVM 关键字，由虚拟机实现 | JDK 类，基于 AQS 实现 |
| 释放方式 | 退出同步块自动释放，异常也释放 | 必须手动 `unlock()`，通常写在 finally |
| 获取方式 | 拿不到就一直等 | `tryLock()`、`tryLock(超时)`、`lockInterruptibly()` |
| 能否响应中断 | 等锁时不能被中断 | `lockInterruptibly()` 等锁时可被中断 |
| 公平性 | 只有非公平 | 构造时传 `true` 即公平，默认非公平 |
| 条件队列 | 一个（`wait/notify`） | 可创建多个 `Condition` |
| 可重入 | 支持 | 支持 |

结论：大多数场景优先用 synchronized，代码简单，不会忘记释放。只有需要尝试获取、超时、可中断、公平或多个条件队列时，才换 ReentrantLock。

### 几个差异的具体含义
- **尝试获取锁**：`tryLock()` 拿不到立刻返回 false，线程可以去干别的事，而不是干等。这在避免死锁时很有用。
- **条件队列**：synchronized 配合 `wait/notify` 时，所有等待的线程在同一个队列里，`notify` 随机叫一个。ReentrantLock 可以建多个 Condition，例如「队列不满」和「队列不空」分开，精确唤醒该醒的那一批线程。
- **实现层面**：synchronized 底层依赖对象头和监视器；ReentrantLock 依赖 AQS 的状态变量和等待队列。

### 进阶：性能怎么比（基础薄弱可先跳过）
早期 synchronized 比 ReentrantLock 慢得多，后来 JVM 对 synchronized 做了大量优化（锁升级、自旋等），两者的差距不再是选择依据。具体哪个快，取决于 JDK 版本和竞争情况，应该看压测，不要凭印象。

## 示例
```java
// synchronized：自动释放
synchronized (lock) {
    doWork();
}

// ReentrantLock：手动释放，且支持超时
ReentrantLock rl = new ReentrantLock();
if (rl.tryLock(1, TimeUnit.SECONDS)) {   // 最多等 1 秒
    try {
        doWork();
    } finally {
        rl.unlock();                     // 一定要在 finally 中释放
    }
} else {
    // 拿不到锁，走降级逻辑
}
```

## 易错点
- 忘记在 finally 中 unlock，抛出异常后锁永远不释放
- 以为 ReentrantLock 一定比 synchronized 快；性能要看场景和压测
- 以为 synchronized 不可重入；它是可重入的
- 把 lock() 写进 try 内部，加锁失败时 finally 里的 unlock 会抛 IllegalMonitorStateException

## 追问
### [f1] 公平锁一定更好吗？
不一定。公平锁严格按顺序，避免线程饿死，但线程切换更多，吞吐量通常低于非公平锁，默认用非公平。

### [f2] ReentrantLock 怎么避免死锁？
可以用 `tryLock` 带超时：拿不到锁就放弃已持有的锁并重试，或者走别的处理，不会一直死等。
