---
id: q_01M6XCDFPMXDBXYQ13X4WZ6761
title: Redisson 的看门狗（watch dog）是做什么的？
type: concept
difficulty: medium
importance: 3
category: redis
tags: [distributed-lock, expiration]
prerequisites: [q_01M6ZYJV9DSFGKHTGJ4J6B3ZH6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
看门狗是 Redisson 的后台续期任务：业务还没做完时，每隔一段时间自动延长锁的过期时间，免得业务没完锁就过期。

## 要点
- [kp1|3] 看门狗定期把锁的过期时间重置，防止业务没完成锁就失效
- [kp2|3] 只有加锁时不指定 leaseTime，看门狗才会启动
- [kp3|2] 默认锁过期时间 30 秒，大约每隔三分之一的时间续期
- [kp4|2] 释放锁后看门狗停止；进程宕机时续期也停止，锁自动过期

## 详解
### 先搞懂：不用自己盯着时间
设想你在会议室开会，不确定会开多久。如果每次只订 30 秒，到点就被赶出去；如果订一整天，又怕你提前走了别人用不了。

折中的办法是：有个管理员每隔十秒看一眼，只要你还在里面，就帮你把预订时间重新延长到 30 秒。你走了，他就不再续。这个管理员就是看门狗。

后文用到的词：

- **leaseTime**：加锁时指定的锁持有时间，到点自动释放。
- **续期**：把锁的过期时间重置到初始长度。

### 什么时候启动
看门狗只在你没有指定 leaseTime 时才工作：

- `lock.lock()` 或 `tryLock(waitTime, unit)`：不指定 leaseTime，启动看门狗；
- `lock.lock(10, TimeUnit.SECONDS)`：指定了 leaseTime，不启动，10 秒后锁就过期。

### 它是怎么续期的
默认锁的过期时间是 30 秒，由配置项 `lockWatchdogTimeout` 控制。加锁成功后，Redisson 起一个定时任务，大约每隔十秒检查一次：锁还在、还是自己持有，就把过期时间重新设为 30 秒。

锁释放后，续期任务被取消，不再继续。

### 为什么宕机时锁还能自己释放
续期任务运行在持锁的进程里。进程宕机后，续期也就停了，锁最多再撑过剩下的过期时间就会失效，别人就能拿到锁，不会永远卡住。

### 使用时要注意
- 业务线程如果卡住不返回，看门狗会一直续期，锁一直不释放，要给业务加超时控制。
- 看门狗解决的是“业务比预期慢”，不能防“主从切换丢锁”之类的问题。

## 示例
```java
RLock lock = redisson.getLock("lock:report");
lock.lock(); // 不指定 leaseTime：看门狗自动续期
try {
    generateReport();
} finally {
    lock.unlock(); // 释放后停止续期
}
```

## 易错点
- 指定了 leaseTime 还期待自动续期；指定之后看门狗不会启动
- 忘记 unlock，以为进程活着锁也会过期；进程活着时看门狗会一直续期
- 以为看门狗能让锁绝对安全；主从切换、长时间 GC 暂停仍可能出问题

## 追问
### [f1] 默认的续期时间可以改吗？
可以，通过 Redisson 配置的 `lockWatchdogTimeout` 修改，默认 30 秒。续期间隔大约是它的三分之一。
