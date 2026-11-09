---
id: q_01M6XBP703BWJ9PRSQ3F2155S7
title: CAS 自旋为什么会有循环性能开销，怎么解决？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [atomic-operation]
prerequisites: [q_01M6XBH24PS1VMJ25KY5CA4GP1]
appliesTo: ["LongAdder：Java >= 8", "Thread.onSpinWait：Java >= 9"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：LongAdder", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html" }
  - { title: "Java SE 21 API：Thread.onSpinWait", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html#onSpinWait()" }
---

## 一句话
自旋 CAS 失败后会一直重试，竞争激烈时线程空转占满 CPU；解决办法是限制自旋次数，超过就停止或改用阻塞，还可以分散竞争。

## 要点
- [kp1|3] 自旋 CAS 一直失败会持续占用 CPU，却没有做有用的事
- [kp2|3] 常见解决：限制自旋次数，超过后停止自旋或改为阻塞等待
- [kp3|2] 从根源减少竞争，如用 LongAdder 把热点变量拆成多份
- [kp4] 重试之间可以退避，或用 Thread.onSpinWait() 提示 CPU
- [kp5] 锁升级里的轻量级锁转重量级锁，也是限制自旋的体现

## 详解
### 先搞懂：在门口一直转圈等
你去开会议室的门，发现里面有人。你不走开，也不坐下，就在门口不停地试门把手：开了没？开了没？如果里面的人开很久，你就一直这样白白耗着力气，什么事也干不了。

自旋 CAS 就是这样：线程的 CAS 失败了，立刻再试，一直试到成功。竞争不激烈时，试一两次就成功，非常快；竞争激烈时，大量线程同时空转，CPU 白白被占满。

后文用到的术语：

- **自旋**：失败后在循环里不断重试，不进入睡眠。
- **CAS**：比较并交换，值等于预期才修改。
- **阻塞（挂起）**：线程暂停，让出 CPU，等被唤醒再继续。

### 问题出在哪
自旋适合「很快就能成功」的情形。如果某个线程长时间持有资源，或者很多线程争同一个变量，失败的线程每次都是空转。它们占着 CPU，没有进展。真正需要 CPU 的线程反而拿不到时间。

### 办法一：限制自旋次数
自旋到一定次数还不成功，就不再空转：

- 直接放弃，返回失败，让调用方决定怎么办；
- 或者改用阻塞，让线程挂起等待，把 CPU 让出来。

JDK 内部不少地方就是这样做的，例如 synchronized 的轻量级锁先自旋，不行就升级为重量级锁让线程阻塞。AQS 里线程也是先尝试几次，再挂起。

### 办法二：减少竞争
自旋久，是因为很多线程在争同一个变量。如果能把这一个变量拆成多份，竞争自然少了。

`LongAdder` 就是这个思路：内部维护多个分散的计数单元，不同线程更新不同的单元，读取总数时再把它们加起来。JDK 文档说明，在竞争激烈的情况下，它的吞吐量通常高于 `AtomicLong`。

### 办法三：重试时退让
失败后不要立刻再冲，可以等一小会儿再试（退避）。Java 9 起还有 `Thread.onSpinWait()`，在自旋循环里调用，提示 CPU 当前处于忙等状态，让它可以做相应优化。

### 对比
| 办法 | 做法 | 适合 |
|---|---|---|
| 限制自旋次数 | 超过次数就停止或阻塞 | 自己写重试循环时 |
| 分散热点（LongAdder） | 拆成多个变量 | 高并发计数 |
| 退避 / onSpinWait | 重试前稍等 | 自旋等待较短时 |

结论：先想办法减少竞争（如换成 LongAdder），重试循环一定要设置上限，别无限空转。

## 示例
```java
// 限制自旋次数的重试
AtomicInteger value = new AtomicInteger();
boolean success = false;
for (int i = 0; i < 100 && !success; i++) {   // 次数只是示例
    int old = value.get();
    success = value.compareAndSet(old, old + 1);
}
if (!success) {
    // 自旋超限，改用锁或阻塞等其他方式
}
```

## 易错点
- 以为无锁就没有性能问题；高竞争下，自旋失败同样消耗大量 CPU
- 以为自旋次数越多越好；次数过多只是在空转
- 以为 LongAdder 是 AtomicLong 的完全替代；它适合累加统计，不适合需要精确读取瞬时值的场景
- 以为限制次数之后就没事了；超限后必须有后续处理，否则操作实际上失败了

## 追问
### [f1] synchronized 里是怎么限制自旋的？
轻量级锁先自旋，自旋一段时间仍拿不到锁，就升级为重量级锁，让线程阻塞。

### [f2] 什么时候自旋比阻塞划算？
持有资源的时间很短时。线程挂起再唤醒的开销，比原地等一小会儿还大。
