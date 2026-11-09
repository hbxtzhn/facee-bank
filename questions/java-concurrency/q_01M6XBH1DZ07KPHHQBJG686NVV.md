---
id: q_01M6XBH1DZ07KPHHQBJG686NVV
title: ReentrantLock 是怎么基于 AQS 实现的？
type: concept
difficulty: hard
importance: 2
category: java-concurrency
tags: [aqs, atomic-operation]
prerequisites: [q_01M6XBH0ZSAA659DGMH7CVFMM5]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "Java SE 21 API：ReentrantLock", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html" }
  - { title: "OpenJDK jdk21u 源码：ReentrantLock.java（Sync、NonfairSync、FairSync）", url: "https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/util/concurrent/locks/ReentrantLock.java" }
---

## 一句话
ReentrantLock 内部有个继承 AQS 的 Sync 类：用 state 记录重入次数，0 表示没人持有，抢不到锁的线程由 AQS 放进等待队列挂起。

## 要点
- [kp1|3] ReentrantLock 内部类 Sync 继承 AQS，lock 和 unlock 都委托给它
- [kp2|3] state 为 0 表示空闲，大于 0 表示持有，数值就是重入次数
- [kp3|2] 获取锁：state 为 0 就 CAS 抢占；持有者是自己则 state 加 1
- [kp4|2] 释放锁：state 减 1，减到 0 才清空持有者并唤醒后继
- [kp5] Sync 有公平和非公平两个子类，构造时选择

## 详解
### 先搞懂：AQS 是排队系统，ReentrantLock 定规则
上一题讲过，AQS 负责排队、挂起和唤醒，子类只需要定义「什么算抢到、什么算释放」。ReentrantLock 就是这样一个子类：用 AQS 的 state 来表示锁的状态，其余的事交给 AQS。

可以想象成餐馆里的叫号系统（AQS）加一条店规（ReentrantLock）：「桌子空着（state 为 0）就能坐；已经坐在桌子上的人自己可以再点单（重入）；吃完才算空出来」。

后文用到的术语：

- **state**：AQS 的 int 变量，在这里表示重入次数。
- **持有线程（owner）**：当前拿着锁的线程。
- **CAS**：比较并交换，一条原子操作。

### 结构：Sync 加公平、非公平两个子类
ReentrantLock 内部有一个抽象类 `Sync`，继承 `AbstractQueuedSynchronizer`，它的两个子类是 `NonfairSync` 和 `FairSync`。构造 ReentrantLock 时，根据参数创建其中一个，`lock()`、`unlock()` 都转给它处理。

### 加锁：看 state 和持有者
获取锁的逻辑（以非公平为例，简化后）：

1. 取当前 state。
2. 如果是 0，用 CAS 把它改成 1，成功就把「持有线程」设为当前线程，加锁成功。
3. 如果不是 0，但持有线程就是当前线程，说明是重入，state 加 1，成功。
4. 否则失败。失败后由 AQS 把当前线程包装成节点，加入等待队列，并把它挂起。

### 解锁：减到 0 才真正释放
1. 检查：当前线程必须是持有者，否则抛 `IllegalMonitorStateException`。
2. state 减 1。
3. 如果减到 0，把持有线程清空，说明锁真正释放，AQS 唤醒队列里的后继线程去竞争。
4. 如果没到 0，说明还有外层的重入，没有真正释放。

### 条件队列
`lock.newCondition()` 返回的 Condition 对象，也是 AQS 里的 `ConditionObject`。一个锁可以有多个，线程在 `await()` 时会释放锁并进入各自的条件队列，被 `signal()` 唤醒后重新回到 AQS 的等待队列争抢锁。

### 对比：ReentrantLock 与 AQS 的分工
| 内容 | 谁负责 |
|---|---|
| 判断能不能拿到锁、重入计数 | ReentrantLock 的 Sync（`tryAcquire` / `tryRelease`） |
| 排队、挂起、唤醒 | AQS |
| 公平或非公平 | 创建的是 FairSync 还是 NonfairSync |

结论：ReentrantLock 自己只写了规则，等待队列的复杂逻辑全由 AQS 承担。

## 示例
```java
// 简化后的逻辑，帮助理解，不是 JDK 源码原文
boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        if (compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    } else if (current == getExclusiveOwnerThread()) {
        setState(c + acquires);          // 重入
        return true;
    }
    return false;                        // 失败，交给 AQS 排队
}

boolean tryRelease(int releases) {
    if (Thread.currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException();
    int c = getState() - releases;
    boolean free = (c == 0);
    if (free) setExclusiveOwnerThread(null);
    setState(c);
    return free;                         // 返回 true 才会唤醒后继
}
```

## 易错点
- 以为 ReentrantLock 自己实现了等待队列；排队挂起是 AQS 做的
- 以为 state 只能是 0 或 1；重入会让它大于 1
- unlock 次数少于 lock 次数，state 到不了 0，锁一直不释放
- 以为公平和非公平是两套完全不同的代码；差别主要在获取锁前要不要先看队列

## 追问
### [f1] state 为什么要用 volatile？
保证多个线程能立刻看到最新值，配合 CAS 修改，才能安全地判断锁是否空闲。

### [f2] 重入次数有上限吗？
有。state 是 int 类型，超过范围会溢出，JDK 的实现会在溢出时抛出 Error，实际用不到这么多。
