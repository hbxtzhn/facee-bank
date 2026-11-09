---
id: q_01M6XCD6TPR9H63ZZ94FDM0PMV
title: 强一致场景下怎么用读写锁保证缓存一致？
type: concept
difficulty: medium
importance: 1
category: redis
tags: [cache-consistency, lock-modes]
prerequisites: [q_01M6ZYJTQVAQ7HWT9GS31BX2VC, q_01M6XCD6JGZDC6AFB7KK4PV9G2]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
读数据时加共享读锁，写数据时加排他写锁，写没完成之前读请求只能等，所以读到的缓存一定和数据库一致，代价是读写并发降低。

## 要点
- [kp1|3] 读操作加读锁，写操作加写锁，二者用同一个锁名
- [kp2|3] 写锁持有期间，读请求被阻塞，读不到中间状态
- [kp3|2] 写操作包含改数据库和删除缓存两步，都在写锁里完成
- [kp4|2] 读读可并发，所以读多写少时代价可以接受
- [kp5] 代价是写时读等待，吞吐下降，且要保证释放锁

## 详解
### 先搞懂：改账本时先把本子锁起来
双写不一致的根源，是改数据库和改缓存两步之间，别人可以插进来读到旧值。要解决它，最直接的办法是：我改的时候，谁也别来读。

就像会计改账本，改的时候把本子锁在抽屉里，改完、两本都核对一致，再打开抽屉让别人看。别人想看，只能等。

后文用到的术语：

- **读锁（共享锁）**：多个读线程能同时持有。
- **写锁（排他锁）**：持有期间，其他读写都要等。
- **双写**：同时写数据库和缓存。

### 读流程：加读锁，再读缓存
1. 获取读锁。如果此时有人持有写锁，就等待。
2. 读缓存，命中就返回。
3. 未命中，查数据库，回填缓存。
4. 释放读锁。

多个读请求可以同时持有读锁，互不阻塞。

### 写流程：加写锁，改库、清缓存
1. 获取写锁。要等所有正在读的线程释放读锁。
2. 修改数据库。
3. 删除缓存（或更新缓存）。
4. 释放写锁。

整个写的过程中，没有读线程能进来，所以不会出现「读到旧值再写回缓存」的并发交叉。

### 为什么能保证一致
前面不一致的各种场景，本质都是读和写交叉执行。读写锁让读和写互斥，同一个 key 的读写不会交叉，旧值也就没机会被写回缓存。

### 代价
- 写锁持有期间，所有读请求都要排队，响应变慢。
- 每次读写都要访问 Redis 获取锁，增加网络开销。
- 写频繁时，读请求会长期被阻塞。

所以它只用在对一致性要求高、读多写少的场景。如果可以接受短暂不一致，用延迟双删或 TTL 更轻量。

## 示例
```java
RReadWriteLock rwLock = redisson.getReadWriteLock("lock:item:" + id);

Item read(long id) {
    RLock lock = rwLock.readLock();
    lock.lock();
    try {
        Item item = cache.get(id);
        if (item == null) {
            item = db.select(id);
            cache.put(id, item);
        }
        return item;
    } finally {
        lock.unlock();
    }
}

void write(Item item) {
    RLock lock = rwLock.writeLock();
    lock.lock();
    try {
        db.update(item);
        cache.delete(item.getId());
    } finally {
        lock.unlock();
    }
}
```

## 易错点
- 读写使用不同的锁名；这样读写不会互斥，起不到作用
- 只给写加锁、读不加锁；读线程仍可能和写交叉
- 以为加了锁就没有任何性能代价；写时读会被阻塞

## 追问
### [f1] 读多写少时为什么推荐读写锁，而不是普通互斥锁？
读写锁允许多个读线程并发，只有写才互斥。普通互斥锁连读也要排队，读多时白白浪费并发能力。
