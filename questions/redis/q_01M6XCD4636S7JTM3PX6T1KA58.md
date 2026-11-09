---
id: q_01M6XCD4636S7JTM3PX6T1KA58
title: 缓存击穿时怎么用互斥锁重建缓存？
type: concept
difficulty: medium
importance: 3
category: redis
tags: [cache-failure, distributed-lock]
prerequisites: [q_01M6XCD3XFRZHY4YEE5VSN04R3]
references:
  - { title: "Redis 文档：SET 命令（NX / EX 选项与加锁 Patterns）", url: "https://redis.io/docs/latest/commands/set/" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
热点 key 过期时，让线程先抢一把互斥锁，只有抢到的那个去查库并重建缓存，其他线程等一会再读缓存，这样数据库只被查一次。

## 要点
- [kp1|3] 缓存击穿：热点 key 过期瞬间，大量请求同时打到数据库
- [kp2|3] 未命中的线程先抢互斥锁，抢到的查库并写回缓存
- [kp3|2] 没抢到锁的线程休眠一会，再重新查缓存，不直接查库
- [kp4|2] 优点是强一致，缺点是等待的线程多，性能较低
- [kp5] 锁要设过期时间，重建完成后在 finally 里释放

## 详解
### 先搞懂：热点商品过期的那一刻
做过秒杀或商品详情页的人都见过这种情况：一个爆款商品的详情缓存到期了，下一毫秒有几千个请求同时来读，缓存里没有，它们就一起去查数据库。数据库一下子被打满，这就是**缓存击穿**。

可以把它想成一家店只有一本价目表，表突然被收走了，所有顾客都跑去问老板。比较好的办法是：只让一个顾客去问老板、重新抄一份贴出来，其他人在旁边等着看新表。

后文用到的术语：

- **互斥锁**：同一时刻只允许一个线程持有的锁，别人只能等。
- **重建缓存**：查数据库拿到最新数据，再写回 Redis。
- **TTL**：key 的存活时间，到点就过期。

### 互斥锁重建：只放一个人去查库
流程按发生顺序是这样：

1. 线程先查缓存，命中就直接返回。
2. 没命中，尝试获取互斥锁。常见做法是 Redis 的 `SET key value NX EX`，key 不存在时才能设置成功。
3. 抢到锁的线程再查一次缓存，因为可能刚好有别的线程已经重建好了。确实没有，才去查数据库，把结果写回缓存，最后释放锁。
4. 没抢到锁的线程休眠一小段时间，然后回到第 1 步重新来。

这样无论多少请求涌进来，同一个 key 同一时刻只有一个线程在查数据库。

### 为什么说它强一致，但性能低
抢到锁的线程重建完成之前，其他线程拿不到任何数据，只能等。等到的一定是刚重建的新数据，所以数据是一致的。

代价也在这里：重建越慢，排队等待的线程越多，请求的响应时间就被拖长。线程在循环里休眠重试，也会占用服务器资源。所以它适合对一致性要求高、能接受偶尔变慢的场景。

### 实现时要注意的几点
- 锁一定要设过期时间。否则抢到锁的线程宕机，锁永远不释放，所有人都卡住。
- 释放锁要放在 `finally` 里，保证查库报错也能释放。
- 释放时最好确认锁还是自己的，避免误删别人后来抢到的锁。
- 抢到锁之后要再查一次缓存，避免重复重建。

## 示例
```java
String getWithMutex(String key) throws InterruptedException {
    while (true) {
        String json = redis.opsForValue().get(key);
        if (json != null) return json;                 // 命中，直接返回

        String lockKey = "lock:" + key;
        Boolean ok = redis.opsForValue()
                .setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);
        if (Boolean.TRUE.equals(ok)) {
            try {
                json = redis.opsForValue().get(key);   // 抢到锁后再查一次
                if (json != null) return json;
                json = loadFromDb(key);                // 查库重建
                redis.opsForValue().set(key, json, 30, TimeUnit.MINUTES);
                return json;
            } finally {
                redis.delete(lockKey);                 // 释放锁
            }
        }
        Thread.sleep(50);                              // 没抢到，休眠后重试
    }
}
```

## 易错点
- 以为每个线程都要查库；实际只有抢到锁的那一个查，其余等待后读缓存
- 没给锁设过期时间；持锁线程挂掉后，其他线程会一直重试
- 抢到锁就直接查库；别的线程可能刚重建完，应该先再读一次缓存

## 追问
### [f1] 互斥锁方案的缺点是什么？
重建期间其他线程只能休眠重试，响应变慢，线程资源被占用。如果重建很慢或锁没释放，还可能出现请求堆积。可以改用逻辑过期，先返回旧数据，牺牲一点一致性换可用性。

### [f2] 单机用 synchronized 行不行？
多个服务实例各自有一把本地锁，每个实例都会放一个线程去查库，数据库被查的次数等于实例数。要保证全局只查一次，需要分布式锁，比如 Redis 的 `SET NX` 或 Redisson。
