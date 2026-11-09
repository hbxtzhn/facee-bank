---
id: q_01M6XBH38F1VMGD9XFXYVX20T8
title: 什么是悲观锁？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [optimistic-pessimistic-lock]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
悲观锁假设冲突一定会发生，所以访问共享资源之前先加锁，同一时刻只让一个线程进去，Java 里的 synchronized 和 ReentrantLock 都是悲观锁。

## 要点
- [kp1|3] 悲观锁认为冲突很可能发生，操作数据前必须先拿到锁
- [kp2|3] 拿到锁的线程独占资源，其他线程只能阻塞等待
- [kp3|2] Java 中 synchronized 和 ReentrantLock 都属于悲观锁
- [kp4] 数据库的 SELECT ... FOR UPDATE 也是悲观锁思路

## 详解
### 先搞懂：先上锁再干活
扣库存时，两个请求同时读到库存是 1，各自减 1，结果卖出去两件，这就是并发冲突。

可以把共享资源想成公共厕所：悲观的人觉得「肯定有人跟我抢」，所以进去先把门锁上，用完再开锁，别人只能在外面排队。这就是悲观锁的思路。

后文会用到的词：
- **共享资源**：多个线程都能读写的数据，比如库存数量。
- **临界区**：必须加锁保护、同一时刻只能一个线程执行的那段代码。
- **阻塞**：拿不到锁的线程暂停下来等，不占 CPU 干别的事。

### 悲观锁：先锁再用，别人只能等
流程很简单：

1. 线程进入临界区之前先获取锁；
2. 拿到锁就执行，期间别的线程来拿锁会失败并进入等待；
3. 执行完释放锁，等待的线程再有一个拿到锁，继续执行。

这样做的代价是：没有冲突时也要加锁、释放锁，拿不到锁的线程要等，所以会有额外开销。好处是逻辑直观，不需要考虑「失败后怎么办」。

### Java 里的两种悲观锁
- **synchronized**：关键字，可以修饰方法或代码块，进出临界区时由 JVM 自动加锁和解锁。
- **ReentrantLock**：`java.util.concurrent.locks` 包里的锁，要自己调用 `lock()` 和 `unlock()`，并且是可重入的，也就是同一个线程拿到锁后可以再次加锁而不会把自己卡死。

## 示例
```java
class Stock {
    private int count = 10;

    // synchronized：同一时刻只有一个线程能执行这个方法
    public synchronized boolean deduct() {
        if (count <= 0) return false;
        count--;
        return true;
    }
}

class Stock2 {
    private final ReentrantLock lock = new ReentrantLock();
    private int count = 10;

    public boolean deduct() {
        lock.lock();
        try {
            if (count <= 0) return false;
            count--;
            return true;
        } finally {
            lock.unlock(); // 必须放在 finally 里，否则异常时锁不会释放
        }
    }
}
```

## 易错点
- 以为悲观锁一定比乐观锁慢；两者各有适合的场景，冲突频繁时悲观锁反而更合适
- 用 ReentrantLock 时把 unlock 写在 try 外面或忘记写，一旦出现异常锁就永远释放不了
- 以为悲观锁只存在于 Java 里；数据库的行锁（如 SELECT ... FOR UPDATE）也是同样的思路

## 追问
### [f1] 悲观锁有什么缺点？
线程拿不到锁就会阻塞，阻塞和唤醒都有开销；使用不当还可能出现死锁。没有冲突时，加锁本身也是白花的成本。

### [f2] 悲观锁的对立面是什么？
乐观锁。它假设冲突很少，不先加锁，而是更新时检查数据有没有被别人改过，改过就重试。Java 里的 CAS 和原子类就是这种思路。
