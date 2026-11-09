---
id: q_01M6XBNZKS6SPX0QH0HMMC3V0K
title: 什么时候会触发 Full GC？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [gc-algorithm, memory-area]
prerequisites: [q_01M6XBG945J00KRDD6XQX1PSVP]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "JDK 17 垃圾回收调优指南：Garbage Collector Implementation（老年代填满触发整堆回收）", url: "https://docs.oracle.com/en/java/javase/17/gctuning/garbage-collector-implementation.html" }
  - { title: "OpenJDK 17u 源码：psScavenge.cpp（晋升估算不足时退化为 Full GC）", url: "https://github.com/openjdk/jdk17u/blob/master/src/hotspot/share/gc/parallel/psScavenge.cpp" }
  - { title: "JDK 17 java 命令文档：-XX:+DisableExplicitGC", url: "https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html" }
estimatedMinutes: 3
---

## 一句话
Full GC 多半是老年代放不下了：Young GC 前预判会放不下，或 Young GC 后晋升失败，或老年代本身不足。

## 要点
- [kp1|3] 老年代空间不足时会触发 Full GC
- [kp2|3] Young GC 前老年代剩余空间小于历次晋升的平均大小，会先做 Full GC
- [kp3|2] Young GC 后有对象要晋升而老年代放不下，会触发 Full GC
- [kp4] 调用 `System.gc()`、元空间不足等也可能触发 Full GC

## 详解
### 先搞懂：新货区往旧货区搬东西，旧货区要放得下
想象一个仓库分「新货区」和「旧货区」。每次清理新货区时，活下来的货可能要搬到旧货区。如果旧货区的空位不够，只能先把旧货区也整理一遍。这就是 Full GC：老年代放不下，要整个堆清理。

后文用到的术语：

- **晋升**：对象从新生代搬到老年代。
- **担保**：Young GC 时，新生代放不下的存活对象由老年代来「兜底」接收。
- **Full GC**：回收新生代、老年代（通常还有方法区）的整体回收。

### 场景一：Young GC 之前，先检查老年代
Young GC 之后，可能有一批对象要晋升到老年代。JVM 在 Young GC 之前先估算：老年代剩余的连续空间，够不够放这批对象。估算时会参考历次 Young GC 后晋升对象大小的平均值。如果老年代剩余空间比这个平均值还小，说明这次很可能放不下，JVM 就先做一次 Full GC，腾出老年代空间。

### 场景二：Young GC 之后，老年代放不下
有时估算没问题，但实际晋升的对象比平均值多，老年代还是放不下，这叫晋升失败，也会触发 Full GC。

### 场景三：老年代自身空间不足
- 大对象直接分配到老年代，老年代放不下。
- 老年代被长期存活的对象填满。
- 使用 CMS 这类收集器时，老年代并发回收来不及，也会退化为 Full GC。

### 其他原因
- 代码调用 `System.gc()`，通常会触发 Full GC，除非用参数禁用。
- 元空间（存放类信息）不足，也可能触发 Full GC。

### 进阶：不同收集器的细节不同（基础薄弱可先跳过）
- 上面的「提前检查」是分代收集器中老年代担保的思路，具体判断条件在不同版本和收集器里有差异，面试时说出思路即可。
- G1 在回收速度跟不上分配速度时，会退化为 Full GC，这类 Full GC 效率低，是需要排查的信号。

## 易错点
- 以为 Full GC 只在老年代满了才发生；Young GC 前的检查失败也会触发
- 以为代码里调用 `System.gc()` 是个好办法；它可能触发 Full GC，造成长时间停顿
- 以为 Full GC 是正常现象；线上频繁发生通常说明有问题

## 追问
### [f1] 线上发现 Full GC 很频繁，第一步看什么？
先用 `jstat -gcutil` 看老年代使用率是否持续上升，再结合 GC 日志判断是哪种触发原因，必要时 dump 堆分析。

### [f2] 老年代还有空间，为什么还会触发 Full GC？
空闲空间可能是碎片，没有足够大的连续空间放大对象；或者是元空间不足、有人调用了 `System.gc()`。
