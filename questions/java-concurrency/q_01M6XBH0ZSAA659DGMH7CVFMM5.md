---
id: q_01M6XBH0ZSAA659DGMH7CVFMM5
title: 什么是可重入锁？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [aqs, synchronized]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
可重入锁就是同一个线程已经拿着锁时，再次获取同一把锁不会被自己挡住；synchronized 和 ReentrantLock 都是可重入的。

## 要点
- [kp1|3] 同一线程已持有锁，再次获取同一把锁会直接成功
- [kp2|3] 不可重入的锁，线程再次获取会被自己阻塞，造成死锁
- [kp3|2] 可重入锁内部记录持有线程和重入次数
- [kp4|2] 加锁几次就要解锁几次，次数归零才真正释放
- [kp5] synchronized 和 ReentrantLock 都是可重入锁

## 详解
### 先搞懂：自己有钥匙，进里屋不用再申请
你拿钥匙进了一间办公室，里面还有一个小房间也用同一把钥匙。如果规定「进小房间要再申请一次，而且不能申请你正持有的钥匙」，你就卡死了：外面的门没出去，里面的门进不去。

可重入就是允许你拿着已经有的钥匙，继续进里面的房间。

后文用到的术语：

- **持有锁**：当前线程已经拿到了这把锁，还没释放。
- **重入**：持有锁的线程再次获取这把锁。
- **死锁**：线程互相等待对方，谁也进行不下去。

### 为什么需要可重入
实际代码里，一个同步方法调用另一个同步方法很常见，比如子类重写了父类的同步方法，又调用 `super.method()`：

```java
public synchronized void a() { b(); }
public synchronized void b() { ... }
```

线程进入 `a()` 时拿了 this 锁，`a()` 里面调用 `b()` 又要同一把 this 锁。如果锁不可重入，线程会等自己释放，永远等下去，把自己卡死了。

### 怎么实现：记次数
可重入锁内部多记两样东西：当前持有者是哪个线程，以及重入了几次。

- 线程第一次加锁：记下持有者，次数为 1。
- 同一线程再次加锁：发现持有者就是自己，次数加 1，直接通过。
- 每次解锁：次数减 1；减到 0 才真正释放，别的线程这时才能拿到。
- 别的线程来加锁：发现持有者不是自己，就要等待。

所以加锁几次就要解锁几次。synchronized 退出同步块时自动减，ReentrantLock 需要自己调用 `unlock()`。

## 示例
```java
ReentrantLock lock = new ReentrantLock();

void outer() {
    lock.lock();
    try {
        inner();          // 同一线程再次 lock，不会被卡住
    } finally {
        lock.unlock();
    }
}

void inner() {
    lock.lock();          // 重入，次数变为 2
    try {
        // ...
    } finally {
        lock.unlock();    // 次数回到 1
    }
}
```

## 易错点
- 以为可重入就是多个线程都能进；它只针对同一个线程
- ReentrantLock 重入了几次 lock，却只调用一次 unlock，锁永远释放不掉
- 以为 synchronized 不可重入；它是可重入的
- 以为不同的锁对象之间也能「重入」；重入只对同一把锁成立

## 追问
### [f1] 不可重入的锁会怎样？
线程在持有锁的情况下再次获取，会被自己阻塞，形成死锁。

### [f2] ReentrantLock 怎么知道重入了几次？
基于 AQS 的 state 变量计数：0 表示没人持有，每重入一次加 1，每解锁一次减 1。
