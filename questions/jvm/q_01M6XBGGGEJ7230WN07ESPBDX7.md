---
id: q_01M6XBGGGEJ7230WN07ESPBDX7
title: 什么是内存溢出（OOM）？
type: concept
difficulty: easy
importance: 2
category: jvm
tags: [performance-diagnosis, memory-area]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
内存溢出（OOM）是程序申请内存时，JVM 里已经没有足够的可用空间，于是抛出 OutOfMemoryError。

## 要点
- [kp1|3] 申请内存而可用空间不够时，JVM 抛出 `OutOfMemoryError`
- [kp2|3] 常见原因：内存泄漏、一次加载的数据太多、堆等内存设置过小
- [kp3|2] 不只堆会溢出，元空间、直接内存、线程数过多等也会 OOM
- [kp4] 排查常用 `-XX:+HeapDumpOnOutOfMemoryError` 保存堆转储，再用工具分析

## 详解
### 先搞懂：杯子装不下水了
内存就像一个杯子，程序不断往里倒水（创建对象）。水倒满了还继续倒，就会溢出来。如果杯子里有一堆早就不用的水没倒掉（内存泄漏），杯子更容易满。

后文用到的术语：
- **堆**：JVM 存放对象的主要内存区域。
- **堆转储（heap dump）**：把堆里所有对象在某一时刻保存成文件，用来分析。
- **内存泄漏**：不再使用的对象仍被引用，无法回收。

### OOM 是怎么来的
当程序创建对象需要内存，JVM 先尝试分配，空间不够就触发垃圾回收；回收后仍然不够，就抛出 `OutOfMemoryError`。注意它是 `Error` 而不是 `Exception`，通常说明程序遇到了严重问题。

### 常见的几种 OOM
- **`Java heap space`**：堆空间不足，最常见。
- **`Metaspace`**：存放类信息的元空间不足，比如动态生成了大量类。
- **`Direct buffer memory`**：直接内存用完了。
- **`unable to create new native thread`**：创建的线程太多，系统无法再创建。
- **`GC overhead limit exceeded`**：GC 花了大量时间却回收很少的内存。

### 常见原因
1. **内存泄漏**：对象不用了却一直被引用，日积月累占满内存；
2. **一次加载太多**：比如一次性把几百万行数据查出来放进内存；
3. **内存配置太小**：业务确实需要更多内存，而 `-Xmx` 设置得太小。

### 出现 OOM 怎么办
先保留现场：启动时加 `-XX:+HeapDumpOnOutOfMemoryError`，让 JVM 在 OOM 时自动生成堆转储，再用 MAT 等工具分析哪些对象占了最多的内存。是泄漏就修代码，是数据量太大就分批处理，确认是配置问题再调大内存。

## 示例
```bash
java -Xmx256m -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=./dump.hprof -jar app.jar
```

## 易错点
- 以为 OOM 只会发生在堆上；元空间、直接内存、线程数也会
- 以为一出现 OOM 就应该调大内存；先确认是不是泄漏，否则只是推迟问题
- 把 OOM 和 `StackOverflowError` 混为一谈；后者是栈深度超限，通常因为递归过深

## 追问
### [f1] OOM 和内存泄漏是什么关系？
内存泄漏是原因之一：泄漏的对象持续占用内存，最终导致 OOM。但 OOM 也可能是因为一次性申请太多，并不一定有泄漏。

### [f2] OOM 之后程序还能继续运行吗？
有时能继续，但状态可能已经不一致。通常应记录日志、保留堆转储并重启，而不是捕获后继续运行。
