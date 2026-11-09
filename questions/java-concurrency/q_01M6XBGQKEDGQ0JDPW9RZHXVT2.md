---
id: q_01M6XBGQKEDGQ0JDPW9RZHXVT2
title: Thread.sleep() 是做什么的？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 1
---

## 一句话
Thread.sleep() 让当前线程暂停指定时间，时间到后重新参与 CPU 调度；睡眠期间它不会释放已持有的锁。

## 要点
- [kp1|3] sleep 是 Thread 的静态方法，暂停的是当前线程
- [kp2|3] 睡眠期间不释放已持有的锁
- [kp3|2] 时间到后线程变为可运行，要重新抢到 CPU 才继续执行
- [kp4|2] 睡眠时被中断会抛 InterruptedException，需要处理

## 详解
### 先搞懂：让线程歇一会儿
做项目时，你可能让程序每隔几秒轮询一次接口，或者模拟耗时操作。这时需要让线程「先停一停」，而不是空转占着 CPU。`sleep` 就是干这个的：睡下去，到点再醒。

类比定闹钟打盹：你睡着时不干活，但你手里拿的钥匙（锁）还在手上，别人想用也拿不到。

后文用到的几个词：
- **监视器锁**：`synchronized` 使用的锁。
- **调度**：操作系统决定哪个线程占用 CPU。

### sleep 的行为
调用 `Thread.sleep(毫秒数)` 后：

1. 当前线程暂停执行，让出 CPU，别的线程可以使用；
2. 线程持有的锁**不会释放**，其他线程想进入同一把锁保护的代码，只能等；
3. 睡眠时间到后，线程回到可运行状态，要等调度器分到 CPU 才继续；所以实际暂停时间可能比设定的长一点，不保证精确。

### 被中断时
如果睡眠过程中有别的线程对它调用 `interrupt()`，`sleep` 会提前结束并抛出 `InterruptedException`。这是受检异常，必须捕获或声明。

## 示例
```java
try {
    Thread.sleep(1000); // 当前线程暂停约 1 秒
} catch (InterruptedException e) {
    Thread.currentThread().interrupt(); // 恢复中断标志
}
```

## 易错点
- 以为 sleep 会释放锁；在 synchronized 块里 sleep 会让其他线程一直等
- 以为睡眠时间精确；到点后还要重新被调度，实际可能略长
- 在 catch 里空处理 InterruptedException；会吞掉别人的停止请求

## 追问
### [f1] sleep(0) 有什么用？
效果依赖实现，不要依赖它做同步。想让出 CPU 的话，用 `Thread.yield()` 更符合意图，但同样不保证效果。
