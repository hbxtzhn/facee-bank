---
id: q_01M6XBH1VZS4EPE5PMDGH2JPK1
title: ReentrantLock 的公平锁和非公平锁是怎么实现的？
type: concept
difficulty: hard
importance: 2
category: java-concurrency
tags: [aqs]
prerequisites: [q_01M6XBP6R1FTDJKQBM5SBM89EA]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java SE 21 API：AbstractQueuedSynchronizer（hasQueuedPredecessors 与公平性）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.html" }
  - { title: "OpenJDK jdk21u 源码：ReentrantLock.java（FairSync.tryAcquire）", url: "https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/util/concurrent/locks/ReentrantLock.java" }
---

## 一句话
两者的差别只在获取锁的那一步：公平锁先看队列里有没有人在等，有就排队；非公平锁不管有没有人等，先直接 CAS 抢一次。

## 要点
- [kp1|3] FairSync 在 CAS 抢锁前，先调用 hasQueuedPredecessors() 判断是否有人排在前面
- [kp2|3] NonfairSync 不看队列，直接 CAS 抢锁，抢不到再排队
- [kp3|2] 公平和非公平的释放逻辑相同，只有获取逻辑不同
- [kp4|2] 无参构造创建 NonfairSync，传 true 创建 FairSync
- [kp5] 非公平锁抢失败后也要进入队列，队列内部仍按先进先出

## 详解
### 先搞懂：同一个队列，两种规矩
上一题讲了公平和非公平的区别：排奶茶店队伍时能不能插队。这一题看代码层面是怎么实现的：两者用的是同一套 AQS 排队系统，区别只在于新来的线程进门时，要不要先看一眼队伍。

后文用到的术语：

- **AQS 等待队列**：抢不到锁的线程排的队。
- **CAS**：比较并交换，一条原子操作，用来把 state 从 0 改成 1。
- **插队（barging）**：新来的线程不排队，直接尝试拿锁。

### 非公平锁：直接抢
`NonfairSync` 的做法：

1. 线程调用 `lock()`，先直接用 CAS 尝试把 state 从 0 改成 1。
2. 成功，就拿到锁，完全没看队列。
3. 失败，走 AQS 的获取流程：再试一次，仍然不行就加入等待队列挂起。

所以刚释放锁时，恰好来的新线程可以抢在队列里的线程前面。

### 公平锁：先看队列
`FairSync` 的 `tryAcquire`：

1. 看 state 是否为 0；
2. 如果是 0，还要调用 `hasQueuedPredecessors()`，判断队列里有没有排在自己前面的线程；
3. 没有人排在前面，才用 CAS 抢锁；有人在前面，就返回失败，去队尾排队。
4. 如果 state 不为 0，但持有者是自己，就是重入，和非公平锁一样。

这一步检查，就是公平和不公平的全部区别。

### 对比
| 对比项 | FairSync | NonfairSync |
|---|---|---|
| 抢锁前先看队列吗 | 看（`hasQueuedPredecessors`） | 不看 |
| 新线程能插队吗 | 不能 | 能 |
| 抢不到之后 | 进入 AQS 队列 | 进入 AQS 队列 |
| 释放锁 | 相同 | 相同 |
| 代价 | 多一次判断，线程切换多 | 可能让队列中的线程被反复插队 |

结论：公平锁靠「多看一眼队列」换来顺序保证，非公平锁省掉这一步换取吞吐；其余代码两者共用。

### 进阶：为什么非公平锁抢到的概率高（基础薄弱可先跳过）
锁释放后，需要先唤醒队首线程，唤醒本身有延迟。这段空档里，如果有新线程来直接 CAS，很容易成功。队首线程醒来发现锁已被抢走，只能继续等。这就是非公平锁吞吐更高、也可能饥饿的原因。

## 示例
```java
// 简化后的公平锁获取逻辑，帮助理解，不是 JDK 源码原文
protected final boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        if (!hasQueuedPredecessors()          // 公平锁多了这一步
                && compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    } else if (current == getExclusiveOwnerThread()) {
        setState(c + acquires);               // 重入
        return true;
    }
    return false;
}
```

## 易错点
- 以为公平锁和非公平锁用了两套不同的队列；队列是同一个 AQS 队列
- 以为非公平锁抢到锁的线程会让整个队列乱序；已经在队列里的线程仍按先进先出
- 以为公平锁让线程的整体执行顺序绝对公平；它只管锁的获取顺序
- 忽略重入的情况：持有者再次加锁，两种锁都直接通过，不需要排队

## 追问
### [f1] hasQueuedPredecessors 是做什么的？
判断等待队列中是否有线程排在当前线程前面。有就返回 true，公平锁据此决定不能抢。

### [f2] 非公平锁没抢到之后，还会再抢吗？
会。进入队列后，线程在被唤醒或排到队首时会再次尝试获取，仍不行就继续挂起。
