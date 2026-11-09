---
id: q_01M6XBP7G6932CMG5P4JAQ1CB4
title: ThreadLocalMap 的结构是怎样的，为什么 key 用弱引用？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [thread-local, gc-algorithm]
prerequisites: [q_01M6XBP5QQ719CQRSMDFYYC52K]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
ThreadLocalMap 是线程自带的哈希表，底层是 Entry 数组，key 是 ThreadLocal 的弱引用，value 是强引用。key 用弱引用，是为了让没人用的 ThreadLocal 能被回收。

## 要点
- [kp1|3] 每个 Thread 对象里有一个 ThreadLocalMap，数据存在线程自己身上
- [kp2|3] Entry 继承 WeakReference，key 是 ThreadLocal 的弱引用，value 是强引用
- [kp3|2] 用弱引用是为了：ThreadLocal 变量没人用了，不会因为被 Map 引用而一直无法回收
- [kp4] 底层是 Entry 数组，不是链表加数组，用 hash 值定位下标
- [kp5] 它没有实现 Map 接口，只是 ThreadLocal 的内部类

## 详解
### 先搞懂：每个线程自带一个小抽屉
做项目时，常用 ThreadLocal 存「当前登录用户」，不同请求线程之间互不干扰。

可以把它想成：每个线程自己带着一个小抽屉，抽屉里放自己的东西。`ThreadLocal` 对象本身像是抽屉里每格的「标签」，真正的东西放在线程自己的抽屉里，而不是放在 ThreadLocal 里。

后文用到的词：
- **ThreadLocalMap**：线程自己的那个抽屉，本质是一张简易的哈希表。
- **强引用**：普通的对象引用，只要还有强引用指着，对象就不会被回收。
- **弱引用**：不会阻止回收的引用，垃圾回收时只要没有强引用，对象就会被回收，引用变成 null。

### 结构：Thread 持有 Map，Map 里是 Entry 数组
调用 `threadLocal.set(value)` 时，大致过程是：

1. 取当前线程 `Thread`；
2. 线程里有个字段 `threadLocals`，类型就是 `ThreadLocalMap`，没有就创建；
3. 以这个 ThreadLocal 对象作为 key，把 value 存进去。

`ThreadLocalMap` 虽然叫 Map，但并没有实现 `Map` 接口，只是 ThreadLocal 的内部类。它主要有两个部分：

- 元素数组 `Entry[] table`；
- 定位方法：用 key 的哈希值与数组长度取下标。

Entry 的定义很特别：它继承了 `WeakReference<ThreadLocal<?>>`，key 通过父类的弱引用保存，value 则是 Entry 自己的一个普通强引用字段。

### 为什么 key 用弱引用
假设代码里有个局部变量 `ThreadLocal<User> tl`，用完后方法结束，变量被销毁，这个 ThreadLocal 对象就没有人用了。

- 如果 Entry 对 key 是强引用：线程只要还活着（比如线程池里的线程），Map 就一直引用着这个 ThreadLocal。它永远不能回收；
- 用弱引用：外面没有强引用后，垃圾回收时这个 ThreadLocal 对象就能被回收，Entry 的 key 变成 null。

这样至少 key 不会泄漏。但要注意：key 变成 null 后，value 仍然被 Entry 强引用着，所以并不能完全避免泄漏，这就要靠 `remove()` 主动清理（详见另一道题）。

### 进阶：哈希与容量（基础薄弱可先跳过）
- 每个 ThreadLocal 创建时会拿到一个哈希码，每次在上一个基础上加一个固定的魔数（0x61c88647），使哈希值分布比较均匀。
- 数组长度始终是 2 的幂，下标是 `hash & (length - 1)`。
- 初始容量是 16，元素个数超过容量的约三分之二时会触发清理，清理后仍然偏多就扩容为两倍。
- 哈希冲突用开放定址法解决，不是 HashMap 的拉链法。

## 示例
```java
ThreadLocal<String> userHolder = new ThreadLocal<>();

userHolder.set("alice");        // 存到当前线程自己的 ThreadLocalMap 里
String name = userHolder.get(); // 只能取到当前线程自己存的值
userHolder.remove();            // 用完清理，避免残留
```

## 易错点
- 以为数据存在 ThreadLocal 对象里；实际存在每个线程的 ThreadLocalMap 里，ThreadLocal 只是 key
- 以为 key 是弱引用就不会泄漏；value 是强引用，线程不结束且不 remove 就会残留
- 以为 ThreadLocalMap 是 HashMap 的实现；它没有实现 Map 接口，冲突解决方式也不同

## 追问
### [f1] ThreadLocalMap 的 value 为什么不也用弱引用？
value 是业务数据，如果也用弱引用，数据可能在线程还没用完时就被垃圾回收，get 会取到 null，行为不可预期。所以 value 必须是强引用。

### [f2] 为什么每个线程各有一个 Map，而不是每个 ThreadLocal 里存一个 Map？
让数据随线程生命周期存在，线程结束时整张表一起被回收；访问时也不需要加锁，因为只有本线程会访问自己的表。
