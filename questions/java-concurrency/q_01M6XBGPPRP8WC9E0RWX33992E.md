---
id: q_01M6XBGPPRP8WC9E0RWX33992E
title: 什么是 wait() / notify() 等待通知机制？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics, synchronized]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
wait() 让当前线程挂起并释放锁，等别的线程对同一个对象调用 notify() 或 notifyAll() 唤醒它；这些方法必须在 synchronized 里调用。

## 要点
- [kp1|3] wait() 使当前线程进入等待，并释放它持有的该对象的锁
- [kp2|3] notify() 随机唤醒一个等待线程，notifyAll() 唤醒全部
- [kp3|2] 三个方法必须在 synchronized 中调用，否则抛 IllegalMonitorStateException
- [kp4|2] 被唤醒后要重新抢到锁才能继续，条件判断要用 while 循环

## 详解
### 先搞懂：生产者和消费者
做项目时常见这样的需求：一个线程往队列里放任务，另一个线程取任务。队列空时，取任务的线程该怎么办？不断循环检查太浪费 CPU。更好的办法是：先睡下，等有任务时再叫醒。

类比餐厅取餐号：没轮到你，你就坐着等，不用一直盯着窗口；叫到你的号，你再起来。wait/notify 就是这套「坐着等、叫号」机制。

后文用到的几个词：
- **监视器锁**：`synchronized` 使用的锁，每个对象都有一个。
- **等待队列**：调用 wait() 的线程在这个对象上排队等通知。

### wait：释放锁并等待
线程在 `synchronized` 块里调用 `obj.wait()` 后，会发生两件事：

1. 释放 obj 的锁，让别的线程能进入同步块；
2. 自己进入等待状态，直到被唤醒或被中断。

这样别的线程才有机会修改条件，再来通知它。

### notify / notifyAll：叫醒等待的线程
别的线程拿到同一个对象的锁，改完条件后调用 `obj.notify()`，会唤醒在这个对象上等待的一个线程；`notifyAll()` 则唤醒全部。

注意：notify 之后，当前线程要退出同步块、释放锁，被唤醒的线程才能重新抢到锁继续执行。

### 为什么必须在 synchronized 里
因为 wait 要释放锁，前提是你持有锁；notify 要在改完条件后通知，也需要和等待方共用同一把锁，避免「刚检查完条件、还没睡下，通知就已经发出」而错过。没拿到锁就调用，会抛 `IllegalMonitorStateException`。

## 示例
```java
synchronized (lock) {
    while (!ready) {      // 用 while，不用 if
        lock.wait();      // 释放锁并等待
    }
    // 条件满足，继续执行
}

// 另一个线程
synchronized (lock) {
    ready = true;
    lock.notifyAll();
}
```

## 易错点
- 用 if 判断条件而不是 while；线程可能被虚假唤醒或条件已被别人改变，醒来后必须重新检查
- 在 synchronized 外调用 wait/notify，或锁的对象与同步块的对象不一致，都会抛 IllegalMonitorStateException
- 以为 notify 会立刻让出锁；锁要到同步块结束才释放

## 追问
### [f1] notify 和 notifyAll 怎么选？
只有一类等待者、且唤醒一个就够时可用 notify。不确定时用 notifyAll 更稳，代价是多唤醒一些线程，醒来后再检查条件。
