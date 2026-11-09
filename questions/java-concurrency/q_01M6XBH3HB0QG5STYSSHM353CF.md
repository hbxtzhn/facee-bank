---
id: q_01M6XBH3HB0QG5STYSSHM353CF
title: 乐观锁和悲观锁各适合什么场景？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [optimistic-pessimistic-lock]
prerequisites: [q_01M6XBH30ENEMEQ84SNRXHQ3M0, q_01M6XBH38F1VMGD9XFXYVX20T8]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：java.util.concurrent.atomic 包说明（compareAndSet 等无锁更新）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/package-summary.html" }
  - { title: "Java SE 21 API：LongAdder（高竞争下与 AtomicLong 的对比）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html" }
---

## 一句话
冲突少、读多写少、操作很短时选乐观锁；冲突频繁、临界区较长或重试代价大时选悲观锁。关键看冲突多不多，以及重试要花多少成本。

## 要点
- [kp1|3] 冲突少、读多写少的场景适合乐观锁，省掉加锁和阻塞的开销
- [kp2|3] 冲突频繁、临界区较长的场景适合悲观锁
- [kp3|2] 乐观锁冲突时要重试，冲突越多，白做的重试越多
- [kp4|2] 重试一次成本很高（如远程调用、复杂计算）时，倾向用悲观锁
- [kp5] 乐观锁常见实现：CAS、原子类、数据库版本号

## 详解
### 先搞懂：两种锁的赌注不同
想象两个人改同一份共享文档：

- **悲观锁**：改之前先「锁住文档」，别人只能等。省心，但就算没人跟你抢，也要先排队拿锁。
- **乐观锁**：不锁，直接改；提交时检查「我读到的版本之后有没有被别人改过」，没改过就成功，改过了就重新读、重新改。

所以选哪个，本质是在赌：**冲突到底多不多**。

后文用到的词：
- **冲突**：两个线程同时想改同一份数据。
- **重试**：乐观锁更新失败后，重新读取最新值再做一遍。
- **临界区**：需要独占执行的那段代码。

### 乐观锁适合：冲突少、操作短
- **读多写少**：读操作不需要加锁，也不会有冲突，比如商品详情的浏览、配置读取。
- **更新简单**：比如计数器加一，一次 CAS（比较并交换）就完成，失败了重来也很便宜。
- 没有线程阻塞，也就不会因为等锁而被挂起、再被唤醒。

### 悲观锁适合：冲突多、操作长
- **冲突频繁**：比如秒杀扣同一件商品的库存，大量线程同时抢，乐观锁会让大部分线程更新失败、反复重试，白白占用 CPU。
- **临界区较长**：一次操作要做很多事（查多张表、调远程接口），一旦失败重来，前面的工作全部作废；不如先锁住，让线程排队一个个做完。
- **重试代价大或不能重复做**：有副作用的操作，重复执行可能出问题，先加锁更稳妥。

### 方案对比：乐观锁 vs 悲观锁
| 维度 | 乐观锁 | 悲观锁 |
|---|---|---|
| 基本假设 | 冲突很少 | 冲突很可能发生 |
| 做法 | 不加锁，更新时检查，失败重试 | 先加锁，别人等待 |
| 冲突少时 | 开销小，没有阻塞 | 仍要加解锁，有额外开销 |
| 冲突多时 | 大量重试，浪费 CPU | 线程排队，行为可预期 |
| 典型实现 | CAS、AtomicInteger、版本号 | synchronized、ReentrantLock |

结论：默认从简单可靠的角度出发，读多写少、更新短小就用乐观锁（原子类）；冲突多、操作长或不适合重试就用悲观锁。

### 进阶：重试成本怎么衡量（基础薄弱可先跳过）
- 乐观锁在高冲突下，CAS 自旋会持续占用 CPU，Java 的 `LongAdder` 就是通过分散热点来减少冲突。
- 乐观锁也可以限制重试次数，超过次数再退化为加锁。
- 数据库层面同理：版本号更新失败就重试或返回错误；冲突很多时，用 `SELECT ... FOR UPDATE` 更直接。

## 示例
```java
// 乐观锁思路：冲突少、操作短
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet(); // 内部是 CAS，失败会自动重试

// 手写 CAS 重试：失败就重读再试
int old, next;
do {
    old = count.get();
    next = old + 1;
} while (!count.compareAndSet(old, next));
```

## 易错点
- 以为乐观锁一定比悲观锁快；冲突频繁时，大量重试会比排队等锁更浪费资源
- 以为乐观锁完全没有锁；CAS 底层依赖 CPU 的原子指令，只是不让线程阻塞
- 临界区里有远程调用、写文件等操作，却用乐观锁重试，失败时这些操作会被重复执行

## 追问
### [f1] 秒杀扣库存应该用哪种锁？
同一件商品被大量请求同时抢，冲突很多，乐观锁会产生大量失败重试。通常会先在入口限流、削峰，再对真正进入扣减的请求用悲观锁或数据库原子更新来保证不超卖。

### [f2] 乐观锁在数据库里怎么实现？
表里加一个 version 字段，更新时写成 `UPDATE ... SET ..., version = version + 1 WHERE id = ? AND version = ?`。影响行数为 0 说明已被别人改过，需要重试或报错。
