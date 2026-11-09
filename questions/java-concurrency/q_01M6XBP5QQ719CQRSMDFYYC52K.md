---
id: q_01M6XBP5QQ719CQRSMDFYYC52K
title: ThreadLocal 的实现原理是什么？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [thread-local]
prerequisites: [q_01M6XBGRT4YN1FJSGZCZKGM6WB]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java SE 21 API：java.lang.ThreadLocal", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ThreadLocal.html" }
  - { title: "OpenJDK jdk21u 源码：java/lang/ThreadLocal.java（ThreadLocalMap、Entry 弱引用 key）", url: "https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/lang/ThreadLocal.java" }
---

## 一句话
每个线程自己带一个 ThreadLocalMap，ThreadLocal 只是 key，值存在当前线程自己的 Map 里，所以每个线程读写的都是自己的那一份。

## 要点
- [kp1|3] 值存在 Thread 对象的 ThreadLocalMap 里，ThreadLocal 本身不存值
- [kp2|3] Map 的 key 是 ThreadLocal（弱引用），value 是强引用
- [kp3|2] 线程池复用线程，不 remove 会残留旧值，还可能内存泄漏
- [kp4|2] 使用完在 finally 里调用 remove()
- [kp5] ThreadLocalMap 用开放寻址解决哈希冲突，不是链表

## 详解
### 先搞懂：每个线程一个自己的小抽屉
Web 项目里常见需求：每个请求处理时，需要在多层代码里都能拿到当前登录用户，又不想一层层传参数。常见做法是把用户信息放进 ThreadLocal。

可以这么想：公司每个员工（线程）桌上有一个自己的小抽屉。ThreadLocal 就像抽屉上的标签：你拿着标签去看，每个人打开的都是自己桌上的那个抽屉，互不干扰。

后文用到的术语：

- **ThreadLocal**：对外的工具类，提供 `get`、`set`、`remove`。
- **ThreadLocalMap**：真正存数据的容器，每个线程一份。
- **弱引用**：垃圾回收时，如果对象只被弱引用指着，就会被回收。

### 数据到底存在哪
很多人以为 ThreadLocal 里有个 Map，按线程存值。实际是反过来的：

1. `Thread` 类里有一个字段，指向 `ThreadLocalMap`。
2. 调用 `threadLocal.set(v)` 时，先拿到当前线程，取出它的 `ThreadLocalMap`（没有就创建），然后以这个 `threadLocal` 对象为 key，把 v 放进去。
3. `get()` 同理：取当前线程自己的 Map，用自己当 key 查。

所以不同线程用同一个 ThreadLocal 对象当 key，却读写各自 Map 里的条目，互不干扰。数据随线程存放，线程结束后跟着一起被回收。这样不加锁也是线程安全的，因为根本没有多线程共享同一份数据。

### 内存泄漏是怎么回事
ThreadLocalMap 里的 Entry，key 是对 ThreadLocal 的**弱引用**，value 却是**强引用**。如果外面不再引用这个 ThreadLocal，垃圾回收会把 key 回收，Entry 变成「key 为 null，value 还在」。这个 value 被线程的 Map 引着，只要线程不结束就回收不掉。

普通线程用完就结束，影响不大。**线程池**里的线程长期存活，这种残留就会一直堆积。ThreadLocalMap 在 `get`、`set`、`remove` 时会顺便清理一部分 key 为 null 的条目，但这种清理不保证彻底。

更实际的问题还有：线程池里的线程会被复用，上一个请求没清理的值，会被下一个请求读到，造成数据串了。

结论：用完在 `finally` 里调用 `remove()`，这是最稳妥的习惯。

### 进阶：哈希冲突（基础薄弱可先跳过）
ThreadLocalMap 没有用 HashMap 的链表，而是自己实现的数组。它用线性探测（开放寻址）处理冲突：位置被占了，就往后找下一个空位。这样设计得比较简单，因为一个线程里的 ThreadLocal 数量通常不多。

## 示例
```java
public class UserContext {
    private static final ThreadLocal<String> USER = new ThreadLocal<>();

    public static void set(String user) { USER.set(user); }
    public static String get() { return USER.get(); }
    public static void clear() { USER.remove(); }
}

// 在请求入口
try {
    UserContext.set("zhangsan");
    handle();           // 内部任意位置都可以 UserContext.get()
} finally {
    UserContext.clear(); // 用完必须清理
}
```

## 易错点
- 以为 ThreadLocal 里面存了所有线程的值；其实值在每个线程自己的 ThreadLocalMap 里
- 线程池中用完不 remove，下一个任务读到上一个任务的旧值
- 以为 key 是弱引用就不会泄漏；value 是强引用，key 被回收后 value 仍然留在 Map 里
- 以为子线程能读到父线程的 ThreadLocal 值；默认不能，需要 InheritableThreadLocal，线程池场景下它也不可靠

## 追问
### [f1] 为什么 ThreadLocal 不需要加锁？
因为每个线程操作的是自己的 ThreadLocalMap，没有多个线程共享同一份数据，也就没有竞争。

### [f2] ThreadLocal 通常声明成什么样？
一般声明为 `private static final`，作为全局的「标签」使用，不需要每个对象一个。
