---
id: q_01M6XBP809BPV6ZBBAT2ZCSNQV
title: ThreadLocal 为什么会内存泄漏，怎么避免？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [thread-local, performance-diagnosis]
prerequisites: [q_01M6XBGRT4YN1FJSGZCZKGM6WB]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
线程一直存活（比如线程池里的线程）时，ThreadLocalMap 里的 value 被强引用着无法回收，就会越积越多；用完 ThreadLocal 后调用 remove() 清理就能避免。

## 要点
- [kp1|3] Entry 的 key 是弱引用，value 是强引用，key 被回收后 value 仍然留在线程里
- [kp2|3] 只有线程长期不结束（如线程池），残留的 value 才会一直占着内存
- [kp3|2] 用完 ThreadLocal 后在 finally 里调用 remove()，是最直接的解决办法
- [kp4|2] 线程结束时整个 ThreadLocalMap 随线程回收，所以短命线程一般没事
- [kp5] 残留的数据在线程池复用线程时，还可能被下一个任务读到，造成串数据

## 详解
### 先搞懂：抽屉里的东西没人清理
做项目时，常在拦截器里 `set` 当前用户，请求结束就完事了。请求线程来自线程池，用完并不会销毁，而是回到池里等下一个请求。

可以这样想：每个线程有个小抽屉，请求来了往抽屉里放东西。线程是长期员工，抽屉一直在，如果每次用完不清空，抽屉里的东西就越堆越多，永远没人拿走。

后文用到的词：
- **内存泄漏**：对象已经没用了，却因为还被引用着，垃圾回收器不能回收。
- **强引用 / 弱引用**：强引用会阻止对象被回收，弱引用不会。
- **ThreadLocalMap**：线程自己持有的存储表，里面存着你 set 进去的值。

### 泄漏是怎么发生的
引用关系是这样的：`Thread` → `ThreadLocalMap` → `Entry` → value（强引用）。而 Entry 的 key 是对 ThreadLocal 对象的弱引用。

1. 业务代码里的 ThreadLocal 变量不再使用，key 因为是弱引用，在垃圾回收后变成 null；
2. 但 Entry 里的 value 还被强引用着，线程只要不结束，value 就一直存在；
3. key 为 null 之后，没有任何办法通过 key 再访问到这个 value，它成了没人用却回收不掉的垃圾。

如果线程是用完即结束的，线程结束后整张表一起被回收，不会有问题。问题出在线程池这种「长命线程」上，并且 value 很大（比如存了大对象）或数量很多时，可能引发内存溢出（OOM）。

### 怎么避免：用完就 remove
1. 使用完 ThreadLocal 后，调用 `remove()`，把当前线程里对应的 Entry 清掉；
2. 一般写在 `finally` 里，保证即使业务抛异常也会清理；
3. `ThreadLocal` 变量通常声明为 `static final`，避免反复创建产生大量 key。

另外，JDK 在 `set`、`get` 时也会顺带清理一部分 key 为 null 的 Entry，但这是「顺便」做的，并不保证及时、彻底，不能依赖。

### 另一个坑：线程复用导致串数据
线程池里的线程被复用，如果上一个任务 set 的值没有清理，下一个任务可能 get 到上一个任务的数据，比如拿到别人的用户信息。这比泄漏更危险，因为是逻辑错误。所以 remove 不仅是为了省内存，也是为了正确性。

## 示例
```java
private static final ThreadLocal<User> CURRENT_USER = new ThreadLocal<>();

public void handle(Request request) {
    CURRENT_USER.set(loadUser(request));
    try {
        doBusiness();
    } finally {
        CURRENT_USER.remove(); // 用完必须清理，线程会被线程池复用
    }
}
```

## 易错点
- 以为 key 是弱引用就不会泄漏；真正泄漏的是强引用的 value
- 以为 remove 会清掉整个线程的所有 ThreadLocal；它只清除当前这个 ThreadLocal 对应的数据
- 把 remove 写在业务代码最后一行而不是 finally，异常时就清理不到
- 以为单靠垃圾回收或 set/get 的顺带清理就够了；这种清理不保证及时

## 追问
### [f1] 为什么 key 设计成弱引用，反而还是会泄漏？
弱引用只保证 key（ThreadLocal 对象）能被回收，没有处理 value。value 的清理依赖 remove 或后续 set/get 的顺带清理，所以仍可能泄漏。

### [f2] 线程池里用 ThreadLocal 还有什么风险？
线程复用会让旧值被新任务读到，造成数据串用；父子线程传值（InheritableThreadLocal）在线程池里也只在线程创建时复制一次，值可能是过期的。
