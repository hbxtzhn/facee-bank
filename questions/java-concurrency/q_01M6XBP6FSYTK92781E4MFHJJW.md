---
id: q_01M6XBP6FSYTK92781E4MFHJJW
title: 怎么用 ReentrantLock 加锁和解锁？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [aqs]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 lock() 加锁，把要保护的代码放进 try，在 finally 里调用 unlock() 解锁，保证不管是否抛异常，锁都会释放。

## 要点
- [kp1|3] 创建 ReentrantLock 对象，用 lock() 加锁，unlock() 解锁
- [kp2|3] unlock() 必须写在 finally 块里，保证异常时也会释放
- [kp3|2] lock() 写在 try 之前，不要写在 try 里面
- [kp4|2] 加锁几次就要解锁几次，只有持有锁的线程才能解锁
- [kp5] 不想一直等可以用 tryLock()，拿不到立刻返回 false

## 详解
### 先搞懂：手动开关的门
synchronized 像自动门，进去出来自动开关。ReentrantLock 是手动门：进门时你要锁上，出门时必须你自己开。如果出门的路上摔了一跤（抛异常），没来得及开，门就一直锁着，别人永远进不来。

所以用 ReentrantLock 有一个固定的写法模板，目的就是保证「无论如何都会开门」。

后文用到的术语：

- **加锁 / 解锁**：获取和释放锁。
- **finally**：Java 里不管是否抛异常，都一定会执行的代码块。
- **阻塞**：线程拿不到锁时在原地等待。

### 标准写法
```java
lock.lock();        // 1. 加锁
try {
    // 2. 访问共享数据
} finally {
    lock.unlock();  // 3. 一定要在 finally 里解锁
}
```

为什么 `lock()` 放在 `try` 之前：如果 `lock()` 自己出了问题（没拿到锁就抛异常），而它又放在 try 里面，finally 会执行 `unlock()`。此时当前线程根本没有持有锁，会抛出 `IllegalMonitorStateException`，还会把真正的异常盖住。放在外面就没有这个问题。

### 其他加锁方式对比
| 方法 | 拿不到锁时 | 适合 |
|---|---|---|
| `lock()` | 一直等待 | 一般情况 |
| `tryLock()` | 立刻返回 false | 拿不到就去做别的 |
| `tryLock(time, unit)` | 等指定时间，超时返回 false | 不能无限等待 |
| `lockInterruptibly()` | 等待时可以被中断 | 需要能取消等待 |

结论：普通场景用 `lock()` 加 `finally` 即可，需要超时或可中断时再换其他方法。

### 和 synchronized 的区别
最大的不同就是释放：synchronized 自动释放，ReentrantLock 必须手动。这是它灵活的代价，也是最容易出错的地方。

## 示例
```java
public class Counter {
    private final ReentrantLock lock = new ReentrantLock();
    private int count;

    public void inc() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();
        }
    }

    public boolean tryInc() {
        if (lock.tryLock()) {       // 拿不到就放弃
            try {
                count++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
}
```

## 易错点
- 忘记 unlock，或者 unlock 没写在 finally 里，抛异常后锁永远不释放
- 把 lock() 写在 try 里面，加锁失败时 finally 里的 unlock 会抛 IllegalMonitorStateException
- 用不同的 ReentrantLock 对象保护同一份数据，等于没锁
- 没拿到锁（tryLock 返回 false）却执行了 unlock

## 追问
### [f1] 为什么不用 synchronized 而用 ReentrantLock？
需要超时获取、可中断、公平锁或多个条件队列时，才用 ReentrantLock；普通场景 synchronized 更简单。

### [f2] 没有持有锁就调用 unlock 会怎样？
会抛出 IllegalMonitorStateException。
