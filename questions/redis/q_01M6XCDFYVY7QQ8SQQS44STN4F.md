---
id: q_01M6XCDFYVY7QQ8SQQS44STN4F
title: Redisson 获取锁失败后怎么重试？
type: concept
difficulty: medium
importance: 1
category: redis
tags: [distributed-lock]
prerequisites: [q_01M6ZYJV9DSFGKHTGJ4J6B3ZH6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Redisson 拿不到锁时不会立刻失败，而是在 waitTime 内等锁释放后反复尝试，等待时间用完仍没拿到才返回失败。

## 要点
- [kp1|3] tryLock 带 waitTime，在这段时间内反复尝试加锁
- [kp2|3] 超过 waitTime 仍没拿到锁，tryLock 返回 false
- [kp3|2] 重试靠订阅锁释放的通知唤醒，不是疯狂轮询 Redis
- [kp4] lock() 没有等待上限，会一直阻塞到拿到锁

## 详解
### 先搞懂：排队等会议室
会议室被占用了，你有两种选择：马上放弃走人，或者在门口等一会儿，对方出来了就进去。你可以给自己定个上限，比如最多等 3 分钟，到点还没空就放弃。

Redisson 的重试就是这样。后文用到的词：

- **waitTime**：最多愿意等多久。
- **tryLock**：尝试加锁，成功返回 true，失败返回 false。

### 三种调用方式
| 方法 | 拿不到锁时 | 返回 |
|---|---|---|
| `tryLock()` | 立刻放弃 | true 或 false |
| `tryLock(waitTime, unit)` | 在等待时间内重试，超时放弃 | true 或 false |
| `lock()` | 一直等到拿到锁为止 | 无返回值 |

### 重试的过程
一次加锁失败时，Redis 返回的是锁还剩多久过期。线程拿到这个数值后：

1. 订阅这把锁的释放通知；
2. 阻塞等待：被通知唤醒，或者等到剩余时间用完；
3. 醒来后再次尝试加锁；
4. 如果总耗时已经超过 waitTime，直接返回 false。

所以重试不是 while 里不停地发命令，而是睡一会再试，对 Redis 压力小。

### 失败以后业务怎么办
返回 false 说明这次没抢到。常见做法：

- 抢单类：直接告诉用户“稍后重试”；
- 定时任务类：说明别的实例在执行，本实例跳过即可。

## 示例
```java
RLock lock = redisson.getLock("lock:order:1001");
// 最多等 2 秒
if (lock.tryLock(2, TimeUnit.SECONDS)) {
    try {
        doBusiness();
    } finally {
        lock.unlock();
    }
} else {
    // 没抢到，走兜底逻辑
}
```

## 易错点
- 以为重试是固定次数；Redisson 是以 waitTime 作为总等待上限
- 以为重试时在死循环里狂发命令；它是等通知后再尝试
- 没拿到锁却执行了 finally 里的 unlock；只有加锁成功才能解锁
- 在高并发入口用 lock()；线程会一直阻塞，可能拖垮线程池

## 追问
### [f1] waitTime 和 leaseTime 有什么区别？
waitTime 是我最多等多久来拿锁，leaseTime 是拿到锁后最多持有多久。前者管等待，后者管锁何时自动过期。
