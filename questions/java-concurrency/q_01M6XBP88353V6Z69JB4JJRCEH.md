---
id: q_01M6XBP88353V6Z69JB4JJRCEH
title: 父子线程怎么共享 ThreadLocal 的数据？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [thread-local, thread-pool]
prerequisites: [q_01M6XBGRT4YN1FJSGZCZKGM6WB]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：InheritableThreadLocal", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/InheritableThreadLocal.html" }
---

## 一句话
用 InheritableThreadLocal 代替 ThreadLocal：子线程创建时，会把父线程里的值复制一份过去，所以子线程能读到父线程设置的值。

## 要点
- [kp1|3] 普通 ThreadLocal 的值只属于当前线程，子线程读不到
- [kp2|3] InheritableThreadLocal 在创建子线程时，把父线程的值复制给子线程
- [kp3|2] 复制只发生在子线程创建那一刻，之后父子线程各改各的，互不影响
- [kp4|2] 线程池里的线程是复用的，不会再次复制，传值会失效或过期
- [kp5] 底层是 Thread 里的 inheritableThreadLocals 字段

## 详解
### 先搞懂：新员工入职时领一份资料
假设请求线程里保存了一个 traceId（链路追踪号），业务里又 `new Thread` 开了个子线程干活，希望子线程打日志时也能带上同一个 traceId。

可是普通 ThreadLocal 里的数据属于线程自己的小抽屉，子线程有自己的抽屉，是空的，读不到。

InheritableThreadLocal 好比：新员工入职时，把老员工抽屉里的资料复印一份交给他。复印完以后，两个人的抽屉就各是各的了。

后文用到的词：
- **父线程**：执行 `new Thread(...)` 的那个线程；**子线程**：被它创建出来的线程。
- **复制**：子线程创建时，把父线程的值拷贝一份给自己。

### 机制：创建子线程时复制
每个 `Thread` 对象里有两个字段：

- `threadLocals`：存普通 ThreadLocal 的数据；
- `inheritableThreadLocals`：存 InheritableThreadLocal 的数据。

创建子线程（执行 `Thread` 的构造过程）时，如果父线程的 `inheritableThreadLocals` 不为空，就会基于它创建一份新的表，给子线程使用。

所以子线程可以读到父线程在**创建子线程之前**设置的值。创建之后，父线程再改值，子线程看不到；子线程自己改了，也不会影响父线程。

### 局限：线程池里不灵
线程池里的线程是提前创建好或者按需创建后反复使用的，值只在线程**被创建那一刻**复制一次：

- 任务提交时，父线程的值不会重新传给工作线程；
- 工作线程如果已经存在，拿到的可能是以前的旧值，甚至是别的请求遗留的数据。

需要在线程池里传值时，通常会借助第三方工具（如阿里的 TransmittableThreadLocal）。也可以在提交任务时手动把值取出来、传进任务里，再在任务中自己 set。

## 示例
```java
InheritableThreadLocal<String> traceId = new InheritableThreadLocal<>();
traceId.set("T-100");

Thread child = new Thread(() -> {
    System.out.println(traceId.get()); // 能读到父线程创建它之前设置的 T-100
});
child.start();
```

## 易错点
- 以为父线程之后修改的值，子线程也能实时看到；复制只发生一次，且是创建时
- 以为 InheritableThreadLocal 在线程池里也能正常传值；复用线程不会再复制
- 以为复制的是对象副本；复制的是引用，父子线程可能指向同一个可变对象，仍要注意线程安全

## 追问
### [f1] 线程池里怎么把上下文传给任务？
最直接的办法是提交任务前取出值，通过任务对象传进去，任务开始时自己 set，结束时 remove。也可以用 TransmittableThreadLocal 等封装好的方案。

### [f2] 子线程里改了值，父线程能看到吗？
看不到，两边各有自己的表。不过如果存的是同一个可变对象的引用，对象内容的修改是共享的。
