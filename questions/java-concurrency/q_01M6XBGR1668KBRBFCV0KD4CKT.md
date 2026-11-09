---
id: q_01M6XBGR1668KBRBFCV0KD4CKT
title: Condition 的 await 和 signal 是做什么的？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics, aqs]
prerequisites: [q_01M6XBGPPRP8WC9E0RWX33992E]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Condition 是配合 Lock 使用的等待通知工具：await() 让线程等待并释放锁，signal() 或 signalAll() 唤醒等待的线程，作用类似 wait/notify，但更灵活。

## 要点
- [kp1|3] Condition 由 lock.newCondition() 创建，必须和某个 Lock 配合
- [kp2|3] await() 释放锁并等待，被唤醒后要重新拿到锁才返回
- [kp3|2] signal() 唤醒一个等待线程，signalAll() 唤醒全部
- [kp4|2] 一个 Lock 可以创建多个 Condition，能按条件分开等待和唤醒
- [kp5] await、signal 都要在持有锁时调用

## 详解
### 先搞懂：显式锁怎么「等通知」
用 `synchronized` 时，可以用 `wait/notify` 做等待通知。如果换成 `ReentrantLock` 这样的显式锁，对应的工具就是 `Condition`。

类比：医院里有挂号、取药两个窗口的等候区。`wait/notify` 像所有人坐在同一个大厅，叫号时要把全部人叫醒再自己判断；`Condition` 则可以分成挂号区和取药区，只叫对应区域的人。

后文用到的几个词：
- **Lock**：显式锁接口，常用实现是 `ReentrantLock`。
- **Condition**：绑定在某个 Lock 上的「等候区」。

### 基本用法
1. 先 `lock.lock()` 拿到锁；
2. 条件不满足时调用 `condition.await()`：当前线程释放锁并进入这个 Condition 的等待队列；
3. 另一个线程拿到同一把锁，改变条件后调用 `condition.signal()` 或 `signalAll()`；
4. 被唤醒的线程要重新竞争拿到锁，`await()` 才会返回，然后继续执行。

### 和 wait/notify 的对比
| 对比项 | wait/notify | Condition |
|---|---|---|
| 搭配的锁 | synchronized | Lock |
| 一把锁上的等待队列 | 一个 | 可创建多个 |
| 唤醒哪类线程 | 无法区分条件 | 可按条件分别唤醒 |

结论：简单场景用 wait/notify 就够；需要按不同条件分别等待时用 Condition，例如阻塞队列里分开「队列非空」和「队列非满」。

## 示例
```java
Lock lock = new ReentrantLock();
Condition notEmpty = lock.newCondition();

// 消费者
lock.lock();
try {
    while (queue.isEmpty()) {
        notEmpty.await();   // 释放锁并等待
    }
    // 取数据
} finally {
    lock.unlock();
}

// 生产者
lock.lock();
try {
    // 放数据
    notEmpty.signal();
} finally {
    lock.unlock();
}
```

## 易错点
- 没有持有锁就调用 await 或 signal；会抛 IllegalMonitorStateException
- 用 if 而不是 while 检查条件；被唤醒后条件可能已变化，要重新检查
- 把 Condition 的 await 写成 Object 的 wait；两套机制不能混用

## 追问
### [f1] 为什么说 Condition 比 wait/notify 灵活？
一个 Lock 可以创建多个 Condition，每个 Condition 有自己的等待队列，可以精确唤醒某一类线程，而 notify 只能随机唤醒该对象上的某一个。
