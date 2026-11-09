---
id: q_01M6XBGHF49W2ZMQZ1F9YSXVGB
title: 内存泄漏常见的原因有哪些？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [performance-diagnosis, thread-local]
prerequisites: [q_01M6XBGDWFFA8CBHD1T08VB0RM, q_01M6XBGGS35P0MM6X0YARGNB9S]
references:
  - { title: "Java SE 21 故障排查指南：Troubleshoot Memory Leaks", url: "https://docs.oracle.com/en/java/javase/21/troubleshoot/troubleshooting-memory-leaks.html" }
  - { title: "Java SE 21 API：java.lang.ThreadLocal", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ThreadLocal.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
内存泄漏的共同原因是“长寿对象一直拿着短命对象的引用”：常见的有静态集合只加不删、单例持有外部对象、连接和流没关闭、ThreadLocal 用完没 remove。

## 要点
- [kp1|3] 静态集合与应用同寿，往里放对象不删，对象就一直回收不了
- [kp2|3] 单例对象存活到应用结束，它持有的外部对象也跟着不能回收
- [kp3|2] 数据库连接、IO 流、Socket 用完不 close，占用的资源不会释放
- [kp4|2] 线程池中的线程长期存活，ThreadLocal 的值不 remove 就会一直留着
- [kp5] 监听器、回调注册后不注销，也会让对象一直被引用

## 详解
### 先搞懂：谁长寿，谁就“拽”着别人不放
想象一个公司的前台登记本：每个来访的人都登记一行，但从来没人划掉。登记本一直在，登记的人哪怕早走了，名字也还留着。

Java 里也是这样。**长寿对象**（静态变量、单例、线程池里的线程）持有**短命对象**的引用，短命对象就没法被 GC 回收。找泄漏，就是找“谁拽着它”。

术语：
- **引用**：变量指向对象；只要有引用链能到达，GC 就不回收；
- **GC Roots**：GC 判断对象存活的起点，如静态变量、线程栈上的变量。

### 静态集合：和应用同寿
静态变量属于类，只要类没有被卸载，它就一直存在。静态的 `Map`、`List` 里放了对象却不清理，这些对象就一直活着。常见于自己写的本地缓存，没有大小上限，也没有过期。

### 单例：一旦持有就不放
单例对象创建后通常存活到应用结束。如果它的字段里存了某个请求、某个 Activity 或某个大对象的引用，这些对象就随单例一起存活。

### 资源没关闭：连接、流、Socket
数据库连接、文件流、Socket 用完必须调用 `close`。不关闭，底层占用的资源不释放，连接池也会被耗尽。推荐用 try-with-resources，自动关闭。

### ThreadLocal：线程不死，值就不丢
每个线程有自己的一张 `ThreadLocalMap`，存着该线程设置的值。线程池里的线程会长期存活，如果设置了值却不调用 `remove()`，值就一直留在线程里；还可能把上一个请求的数据带到下一个请求。

### 其他常见原因
- 监听器、回调注册后不注销；
- 缓存、集合没有大小上限；
- 内部类（非静态）隐式持有外部类的引用。

## 示例
```java
// 泄漏：静态 Map 只放不删
static final Map<String, byte[]> CACHE = new HashMap<>();
void handle(String id) { CACHE.put(id, new byte[1024 * 1024]); }

// 正确：ThreadLocal 用完及时清理
THREAD_USER.set(user);
try {
    doWork();
} finally {
    THREAD_USER.remove();
}
```

## 易错点
- 以为 Java 有 GC 就不会泄漏；GC 只回收不可达对象，被引用着的无用对象不会被清理
- 以为 ThreadLocal 的 key 是弱引用就不会泄漏；value 仍是强引用，线程不结束就一直在
- 以为关了连接对象就行；要调用 `close`，不是把变量置空

## 追问
### [f1] 怎么避免静态缓存泄漏？
给缓存加上大小上限和过期策略，使用成熟的缓存库（如 Caffeine），不要用无限增长的静态 `HashMap`。
