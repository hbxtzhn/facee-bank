---
id: q_01M6XBH2D9CTBFCNYK6QJVV6BE
title: CAS 的 ABA 问题是什么，怎么解决？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [atomic-operation, optimistic-pessimistic-lock]
prerequisites: [q_01M6XBH24PS1VMJ25KY5CA4GP1]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：AtomicStampedReference", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicStampedReference.html" }
  - { title: "Java SE 21 API：AtomicMarkableReference", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicMarkableReference.html" }
---

## 一句话
ABA 问题是变量从 A 变成 B 又变回 A，CAS 只比较值，发现不了中间被改过；用版本号（如 AtomicStampedReference）一起比较就能解决。

## 要点
- [kp1|3] ABA：值经历 A → B → A，CAS 看到「还是 A」就认为没变过
- [kp2|3] 解决办法：每次修改都带版本号或时间戳，CAS 同时比较值和版本号
- [kp3|2] Java 提供 AtomicStampedReference，用 int 版本号标记修改
- [kp4] AtomicMarkableReference 只用 boolean 标记是否被改过
- [kp5] 只关心最终值、不在乎过程的场景，ABA 通常无害

## 详解
### 先搞懂：箱子看起来一样，但被人动过
假设你出门前，桌上放着一张 100 元。你回来发现桌上还是一张 100 元，就以为没人动过。其实期间有人把它拿去花了，后来又放回一张新的 100 元。钱看起来一样，但中间发生过事情。

对只关心「桌上有没有 100 元」的场景，无所谓；但如果你还关心「有没有人动过」，就出问题了。CAS 只比较值，碰到这种情况就会被蒙混过去。

后文用到的术语：

- **CAS**：比较并交换，值等于预期才修改。
- **版本号 / 时间戳**：每次修改就加 1，用来记录改过几次。
- **栈**：后进先出的数据结构，无锁栈是 ABA 的经典例子。

### ABA 是怎么发生的
1. 线程 1 读到变量值是 A，准备做 CAS，但被暂停了。
2. 线程 2 把变量从 A 改成 B，又从 B 改回 A。
3. 线程 1 恢复，做 CAS：当前值是 A，等于预期值 A，成功。

线程 1 不知道变量已经被改过两次。大多数简单计数场景没影响，但在无锁链表、无锁栈这类结构里，节点可能已经被弹出又换了新状态，仅凭「地址还是那个」去操作就会出错。

### 怎么解决：加版本号
思路是不只比较值，还要比较版本号。每次修改，值和版本号一起更新。这样 A → B → A 虽然值回来了，版本号已经从 1 变成了 3，线程 1 用旧版本号 1 去 CAS 就会失败。

Java 里的工具：

- `AtomicStampedReference<V>`：用一个 int 的 stamp 做版本号。
- `AtomicMarkableReference<V>`：用 boolean 标记「是否被改过」，只能区分两种状态，不记录次数。

### 对比
| 方案 | 能否发现 ABA | 额外信息 | 适合 |
|---|---|---|---|
| 普通 CAS（如 AtomicInteger） | 不能 | 无 | 只关心值的计数 |
| AtomicStampedReference | 能 | int 版本号 | 需要精确判断是否被改过 |
| AtomicMarkableReference | 部分能 | boolean 标记 | 只需知道是否变动 |

结论：只关心值的场景用普通原子类；一旦「中间被改过」会影响正确性，就用带版本号的原子类。

## 示例
```java
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(100, 0);

int[] stampHolder = new int[1];
Integer value = ref.get(stampHolder);    // 同时拿到值和版本号
int stamp = stampHolder[0];

// 值和版本号都匹配才修改，修改后版本号加 1
boolean ok = ref.compareAndSet(value, 101, stamp, stamp + 1);
System.out.println(ok);  // true；若期间被别人改过，版本号不同，就会返回 false
```

## 易错点
- 以为 ABA 会导致计数不准；对只加减的计数，ABA 通常没有危害
- AtomicStampedReference 比较的是引用（地址），不是 equals；预期值要用 get 取到的同一个对象
- 以为版本号可以随便写；每次修改都必须更新版本号，否则起不到作用
- 以为 AtomicMarkableReference 能记录改了几次；它只有一个布尔标记

## 追问
### [f1] ABA 在什么场景下会造成真正的问题？
无锁的链表、栈、队列等结构里，节点可能被移除又被复用，只凭引用相等判断，会误以为结构没变。

### [f2] 为什么版本号能解决？
版本号只增不减，A → B → A 期间版本号变了，旧的版本号就对不上，CAS 会失败。
