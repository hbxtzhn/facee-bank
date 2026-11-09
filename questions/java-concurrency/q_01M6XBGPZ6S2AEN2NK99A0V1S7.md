---
id: q_01M6XBGPZ6S2AEN2NK99A0V1S7
title: Thread.yield() 是做什么的？
type: concept
difficulty: easy
importance: 1
category: java-concurrency
tags: [thread-basics, scheduling]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 1
---

## 一句话
Thread.yield() 是提示调度器「我愿意让出 CPU」，让别的线程先跑；调度器可以忽略这个提示，所以不保证有任何效果。

## 要点
- [kp1|3] yield() 只是向调度器提出让出 CPU 的请求，是一种建议
- [kp2|3] 调度器可以忽略，不能依赖它保证执行顺序
- [kp3|2] 线程调用 yield 后仍是可运行状态，随时可能再次被选中
- [kp4] yield 不会释放线程已持有的锁

## 详解
### 先搞懂：线程怎么抢 CPU
CPU 同一时刻只能运行有限个线程，操作系统的**调度器**决定谁来用。这像排队用打印机：你可以说「我先让一下」，但是否真的让、让给谁，由调度器决定。

后文用到的几个词：
- **调度器**：决定哪个线程获得 CPU 的系统组件。
- **可运行状态**：线程已经准备好、等着拿 CPU 的状态。

### yield 做了什么
线程调用 `Thread.yield()`，等于告诉调度器：我这会儿不急，可以让其他同级别的线程先执行。之后可能发生两种情况：

- 调度器接受提示，换别的线程运行；
- 调度器忽略提示，当前线程继续运行。

不管哪种，当前线程都不会进入阻塞，也不会释放持有的锁，它只是回到可运行状态，等待下一次被调度。

### 和 sleep 的区别
`sleep(ms)` 会让线程暂停指定时间，这段时间内一定不会运行；`yield` 没有时间概念，也没有保证。所以 yield 在业务代码里几乎不用，多见于调试和并发实验。

## 示例
```java
Thread t = new Thread(() -> {
    for (int i = 0; i < 100; i++) {
        // 做一点工作后，提示调度器可以换别的线程
        Thread.yield();
    }
});
t.start();
```

## 易错点
- 以为 yield 一定会切换到别的线程；调度器可以忽略
- 用 yield 来控制线程执行顺序；它没有这个保证，要用 join、锁等同步工具
- 以为 yield 会释放锁；不会

## 追问
### [f1] yield 和 sleep 有什么区别？
sleep 让线程暂停指定时间，期间一定不运行；yield 只是建议让出 CPU，线程仍是可运行状态，可能马上又被选中。两者都不释放锁。
