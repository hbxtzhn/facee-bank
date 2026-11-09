---
id: q_01M6XBGP15G7XSYWR0QQCQN6P7
title: AtomicInteger 怎么用来保证计数的原子性？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [atomic-operation]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
AtomicInteger 提供 incrementAndGet() 等方法，一步完成自增，底层用 CAS 实现，不需要加锁就能保证多线程计数不丢。

## 要点
- [kp1|3] incrementAndGet() 自增并返回新值，整个过程是原子的
- [kp2|3] 底层是 CAS：值还是旧值才更新，否则重试
- [kp3|2] 不加锁，线程不会被挂起阻塞
- [kp4] 还有 getAndIncrement、addAndGet、compareAndSet 等常用方法

## 详解
### 先搞懂：计数器为什么要原子类
统计接口调用次数时，多个请求线程同时执行 `count++`，会丢次数（读取、加一、写回三步会交错）。最直接的办法是加锁，但还有更轻的办法：让「加一」这件事本身不可打断。

打个比方：普通 `count++` 像先看一眼黑板上的数、擦掉、再写新数，中间别人也会来写。`AtomicInteger` 像一支特殊的笔：「只有黑板上还是我刚才看到的数，才允许写，不是就重新看一眼再来」。

后文用到的几个词：
- **原子操作**：一步完成、中间不会被别的线程插进来的操作。
- **CAS**（比较并交换）：先比较当前值是不是预期的旧值，是才改成新值，不是就放弃。

### 怎么用
`AtomicInteger` 常用方法：

- `incrementAndGet()`：加一，返回加完后的值；
- `getAndIncrement()`：加一，返回加之前的值；
- `addAndGet(n)`：加 n；
- `get()`：读取当前值；
- `compareAndSet(expect, update)`：手动做一次 CAS，成功返回 true。

### 底层：CAS 加循环重试
以 `incrementAndGet()` 为例，大致过程是：

1. 读到当前值，比如 5；
2. 用 CAS 尝试把 5 改成 6；
3. 如果期间被别的线程改成了 6，CAS 失败，就重新读、重新算、再尝试，直到成功。

CAS 由 CPU 的一条原子指令完成，所以不需要给整段代码加锁，线程也不会因为抢锁而被挂起。代价是竞争激烈时会不断重试，白白消耗 CPU。

## 示例
```java
AtomicInteger count = new AtomicInteger(0);

Runnable task = () -> {
    for (int i = 0; i < 1000; i++) {
        count.incrementAndGet();
    }
};
// 多个线程同时执行 task，最终 count 一定是线程数 * 1000
```

## 易错点
- 以为 AtomicInteger 能保证多个操作整体原子；它只保证单个方法原子，先 get 再 set 的组合仍然会出错
- 以为无锁就一定更快；竞争很激烈时，反复重试也会浪费 CPU

## 追问
### [f1] CAS 有什么问题？
一是竞争激烈时重试多，消耗 CPU；二是一次只能保证一个变量；三是有 ABA 问题：值从 A 变成 B 又变回 A，CAS 看不出中间变过，需要版本号（如 `AtomicStampedReference`）解决。
