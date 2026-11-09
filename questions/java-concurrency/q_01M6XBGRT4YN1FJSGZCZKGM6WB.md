---
id: q_01M6XBGRT4YN1FJSGZCZKGM6WB
title: ThreadLocal 是做什么的，怎么用？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-local, thread-safety]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
ThreadLocal 给每个线程一份独立的变量副本，线程之间互不干扰；用 set 存、get 取、remove 清理，常用来保存线程内的上下文，比如当前登录用户。

## 要点
- [kp1|3] ThreadLocal 让每个线程拥有自己的变量副本，实现线程隔离
- [kp2|3] 常用方法：set 存值、get 取值、remove 删除
- [kp3|2] 典型场景：保存当前用户、请求 ID 等线程内上下文
- [kp4|2] 线程池里线程会复用，用完必须 remove，否则可能串数据或泄漏内存

## 详解
### 先搞懂：每个线程自己的小抽屉
Web 项目里，一个请求由一个线程处理。你想在 Controller、Service、DAO 各层都能拿到「当前登录用户」，但又不想每个方法都加一个参数传来传去。这时可以把用户信息放进 ThreadLocal，当前线程处理请求的任何地方都能取。

类比：每个员工有自己的抽屉，放自己的东西，别人的抽屉看不到，所以不需要加锁抢。

后文用到的几个词：
- **线程隔离**：每个线程有自己的数据，互不可见。
- **副本**：同一个 ThreadLocal 在每个线程里对应的独立值。

### 怎么用
- `set(value)`：把值存到当前线程的副本里；
- `get()`：取当前线程的副本，没设置过返回 null（或初始值）；
- `remove()`：删除当前线程的副本；
- `ThreadLocal.withInitial(...)`：创建时指定初始值。

不同线程对同一个 ThreadLocal 调用 get，拿到的是各自的值，所以它不存在线程安全竞争。

### 为什么要 remove
线程池里的线程执行完一个任务后不会销毁，而是去执行下一个任务。如果上一个任务 set 的值没有 remove：

- 下一个任务可能读到上一个任务遗留的数据，出现串数据；
- 值一直挂在线程上，占用内存，可能造成内存泄漏。

所以最好在 `try ... finally` 里 remove。

### 它不适合解决什么
ThreadLocal 是「让每个线程各用各的」，不是让多个线程共享同一份数据。需要多个线程协作修改同一个对象，还是要用锁等同步手段。

## 示例
```java
private static final ThreadLocal<String> CURRENT_USER = new ThreadLocal<>();

void handle(String user) {
    CURRENT_USER.set(user);
    try {
        service(); // 内部任意位置可用 CURRENT_USER.get()
    } finally {
        CURRENT_USER.remove(); // 线程池场景必须清理
    }
}
```

## 易错点
- 以为 ThreadLocal 能在线程间共享数据；它的作用正好相反，是隔离
- 线程池里用完不 remove；会串数据，也可能泄漏内存
- 以为子线程能读到父线程的值；默认读不到，需要时用 InheritableThreadLocal，但线程池下要谨慎

## 追问
### [f1] ThreadLocal 为什么可能内存泄漏？
每个线程内部有一个 map 保存各 ThreadLocal 的值，key 是弱引用，value 是强引用。key 被回收后 value 还在，线程不结束就一直占着，所以用完要 remove。
