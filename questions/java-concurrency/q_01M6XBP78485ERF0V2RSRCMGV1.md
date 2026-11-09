---
id: q_01M6XBP78485ERF0V2RSRCMGV1
title: CAS 为什么只能保证单个变量的原子操作，多个变量怎么办？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [atomic-operation]
prerequisites: [q_01M6XBH24PS1VMJ25KY5CA4GP1]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
一次 CAS 只能原子地比较并修改一个变量；要同时改多个变量，可以加锁，或者把它们装进一个不可变对象，用 AtomicReference 整体替换。

## 要点
- [kp1|3] CAS 一次只作用于一个内存位置，无法同时保证多个变量
- [kp2|3] 办法一：改用锁，把多个变量的修改放进同一个临界区
- [kp3|2] 办法二：把多个变量封装成一个不可变对象，用 AtomicReference 整体替换
- [kp4] 封装后的对象要不可变，每次修改都创建新对象
- [kp5] 多个变量各用一个原子类，整体仍然不是原子的

## 详解
### 先搞懂：转账要同时改两个账户
最常见的场景是转账：A 账户减 100，B 账户加 100。这两件事必须一起成功或一起失败。如果各自用 CAS，A 减完了、B 还没加之前，别的线程看到的是「少了 100 块」的中间状态，甚至中途失败还会对不上。

CAS 的比较并交换只针对一个变量，没法把两个变量的修改变成不可拆分的一件事。

后文用到的术语：

- **原子**：一个操作要么全部完成，要么完全没发生，别人看不到中间状态。
- **不可变对象**：创建后内容不能再改的对象。
- **AtomicReference**：对一个对象引用做 CAS 的原子类。

### 办法一：用锁
最直接：把对多个变量的修改放进同一把锁保护的代码里。别的线程要访问，必须等锁，看不到中间状态。

代价是线程可能阻塞。但逻辑复杂、涉及多个变量时，这是最可靠、最容易写对的方案。

### 办法二：合并成一个对象，用 AtomicReference
CAS 只能保证一个变量，那就把多个变量变成一个变量：

1. 定义一个类，把需要同时变化的字段都放进去，并让它不可变；
2. 用 `AtomicReference` 保存这个对象的引用；
3. 修改时，创建一个新对象，里面是所有字段的新值，再用 CAS 把引用从旧对象换成新对象。

换引用这一步是一次 CAS，整体成功或失败。别的线程要么看到旧对象，要么看到新对象，不会看到「改了一半」的状态。

### 对比
| 方案 | 做法 | 优点 | 缺点 | 适合 |
|---|---|---|---|---|
| 加锁 | 同一把锁保护多个变量 | 简单可靠，逻辑复杂也行 | 线程可能阻塞 | 一般场景，逻辑复杂 |
| AtomicReference + 不可变对象 | 整体替换引用 | 无锁、不阻塞 | 每次修改创建新对象；逻辑要简单 | 状态简单、读多写少 |
| 多个原子类分别操作 | 每个变量各自 CAS | 写法简单 | 整体不是原子的 | 变量之间没有关联时 |

结论：默认用锁；变量之间有关联、操作很简单且想避免阻塞时，才用 AtomicReference 封装。

## 示例
```java
public class Range {
    // 不可变：lower 和 upper 必须一起变
    private static final class Bounds {
        final int lower;
        final int upper;
        Bounds(int lower, int upper) { this.lower = lower; this.upper = upper; }
    }

    private final AtomicReference<Bounds> bounds =
            new AtomicReference<>(new Bounds(0, 10));

    public boolean setBounds(int newLower, int newUpper) {
        if (newLower > newUpper) return false;
        Bounds old;
        do {
            old = bounds.get();
        } while (!bounds.compareAndSet(old, new Bounds(newLower, newUpper)));
        return true;
    }
}
```

## 易错点
- 以为两个 AtomicInteger 组合起来就是原子的；分别原子不等于整体原子
- 封装的对象可变，别人直接改了里面的字段，就绕过了 CAS
- 以为用 AtomicReference 就没有 ABA 问题；引用可能被换回原对象，需要时用 AtomicStampedReference
- 逻辑复杂也硬用无锁，代码很难写对；复杂场景应优先用锁

## 追问
### [f1] 为什么要求封装的对象是不可变的？
如果能被原地修改，线程拿到引用后改字段，就绕过了 CAS 的检查，整体的原子性被破坏。

### [f2] AtomicReference 的 CAS 比较的是什么？
比较的是引用本身（是不是同一个对象），不是对象内容是否相等。
