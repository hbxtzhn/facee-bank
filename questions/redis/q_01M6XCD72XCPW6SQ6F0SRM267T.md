---
id: q_01M6XCD72XCPW6SQ6F0SRM267T
title: Redisson 读写锁里的共享锁和排他锁分别怎么工作？
type: concept
difficulty: medium
importance: 1
category: redis
tags: [lock-modes, distributed-lock]
prerequisites: [q_01M6XCD6JGZDC6AFB7KK4PV9G2]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Redisson 读写锁的读锁是共享锁，多个线程可以同时拿；写锁是排他锁，拿到后别人既不能读也不能写。

## 要点
- [kp1|3] 读锁是共享锁，没有写锁时，多个线程都能加读锁
- [kp2|3] 写锁是排他锁，持有期间其他线程的读锁、写锁都加不上
- [kp3|2] 读锁和写锁来自同一个 `RReadWriteLock`，使用同一个锁名
- [kp4|2] 锁的状态保存在 Redis 里，多个服务实例共享
- [kp5] 需要主动释放；Redisson 默认带看门狗自动续期

## 详解
### 先搞懂：会议室的使用规则
有一间会议室，如果只是开放参观，很多人可以同时进去看，这相当于读。如果有人要布置会场，就得清场、锁门，布置期间谁也不能进，也不能有别人同时布置，这相当于写。

在 Java 里，同一个 JVM 内用 `ReentrantReadWriteLock` 就够了。但服务部署了多个实例，每个实例有自己的内存，普通锁拦不住别的实例。Redisson 把「谁在读、谁在写」记录在 Redis 里，让所有实例看到同一份状态。

后文用到的术语：

- **共享锁**：能被多个线程同时持有，用于读。
- **排他锁**：只能被一个线程持有，用于写。
- **看门狗**：Redisson 在持锁期间自动延长过期时间的机制。

### 共享锁：读线程之间不互斥
调用 `rwLock.readLock()` 得到读锁。加读锁时：

- 如果当前没人持有写锁，加锁成功，可以和其他读线程同时持有。
- 如果有别人持有写锁，只能等待写锁释放。

所以读多的时候，读线程几乎不会因为锁而排队。

### 排他锁：写线程独占
调用 `rwLock.writeLock()` 得到写锁。加写锁时：

- 如果已有读锁或写锁被别人持有，必须等待。
- 加锁成功后，其他线程的读锁和写锁都被阻止，直到写锁释放。

### 一个重要细节：读写锁要用同一个锁名
读锁和写锁必须从同一个 `RReadWriteLock` 对象（同名）获取，Redisson 才能判断它们之间是否冲突。读用 `lock:item:1`、写用 `lock:item:2`，就起不到互斥作用。

### 不释放锁会怎样
Redisson 的 `lock()` 在没有指定过期时间时，会启动看门狗，持锁线程活着就持续续期，避免业务没做完锁就过期。但持锁线程如果忘了解锁，锁会一直占着，所以要在 `finally` 里释放。

## 示例
```java
RReadWriteLock rwLock = redisson.getReadWriteLock("lock:item:1");

rwLock.readLock().lock();     // 共享锁，多个线程可同时持有
try {
    // 读操作
} finally {
    rwLock.readLock().unlock();
}

rwLock.writeLock().lock();    // 排他锁，持有时其他读写都被阻止
try {
    // 写操作
} finally {
    rwLock.writeLock().unlock();
}
```

## 易错点
- 读写用不同的锁名；二者不会互斥
- 以为读锁也独占；读锁之间可以并发
- 加锁后不在 `finally` 里解锁；异常时锁无法释放

## 追问
### [f1] Redisson 的看门狗是做什么的？
调用 `lock()` 不指定过期时间时，Redisson 会为锁设置一个默认的租期，并在持有期间定时续期，避免业务没做完锁就过期。如果指定了租期，就不会续期。
