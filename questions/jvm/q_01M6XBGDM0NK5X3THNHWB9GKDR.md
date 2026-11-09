---
id: q_01M6XBGDM0NK5X3THNHWB9GKDR
title: CMS 和 G1 有什么区别，G1 有哪些优势？
type: concept
difficulty: hard
importance: 3
category: jvm
tags: [gc-collector]
appliesTo: ["CMS：Java <= 13（Java 14 起移除）", "G1 默认收集器：Java >= 9"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "Oracle JDK 21 垃圾收集调优指南：Garbage-First (G1) Garbage Collector", url: "https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html" }
  - { title: "Oracle JDK 8 垃圾收集调优指南：Concurrent Mark Sweep (CMS) Collector", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/cms.html" }
  - { title: "JEP 363: Remove the Concurrent Mark Sweep (CMS) Garbage Collector", url: "https://openjdk.org/jeps/363" }
---

## 一句话
CMS 用标记-清除，低停顿但有碎片、浮动垃圾，还吃 CPU；G1 把堆分成 Region，回收时复制整理，碎片少，并且能按设定的目标控制停顿，也更容易调优。

## 要点
- [kp1|3] CMS 用标记-清除，会产生内存碎片；G1 回收时复制存活对象，碎片少
- [kp2|3] G1 把堆划分为 Region，每次只回收收益最高的部分，停顿可预测
- [kp3|2] CMS 并发阶段会产生浮动垃圾，还会抢占业务线程的 CPU
- [kp4|2] CMS 碎片严重或回收不及时会退化为长时间 Full GC
- [kp5] CMS 在 Java 14 移除，Java 9 起默认收集器是 G1

## 详解
### 先搞懂：两种打扫房间的思路
CMS 像是边住人边打扫：只扫地不挪家具，所以人几乎不受影响，但扫完后房间里空地七零八落，想摆一个大沙发时可能放不下。

G1 像是把房子隔成许多小房间，每次只挑最脏的几间打扫，打扫时把有用的东西搬到干净的房间，所以空间始终比较整齐，也能估算每次打扫要花多久。

后文用到的术语：
- **内存碎片**：空闲空间被零散的存活对象切成很多小块，总量够用却放不下大对象。
- **浮动垃圾**：回收过程中新产生的垃圾，本轮来不及回收。
- **Region**：G1 把堆切成的等大小小块。
- **可预测停顿**：可以设置期望的停顿时间，收集器尽量满足。

### CMS：低停顿，但有三个明显的毛病
- **碎片**：标记-清除不整理内存，碎片多了放不下大对象，就会触发一次长时间的 Full GC 来整理。
- **浮动垃圾**：并发清除时业务线程还在运行，新产生的垃圾本轮清不掉，所以需要预留空间。预留不够，会出现 concurrent mode failure，退化为停顿很长的回收。
- **依赖 CPU**：并发阶段的 GC 线程要和业务线程抢 CPU，CPU 紧张时业务会变慢。

另外 CMS 的可调参数很多，调优依赖经验。

### G1：区域化管理，复制整理，停顿可控
- **区域化**：堆分成 Region，每次只回收一部分最划算的 Region，所以能控制每次停顿的长度。
- **整理**：回收时把存活对象复制到别的 Region，整体上碎片比 CMS 少得多。
- **可预测停顿**：可以通过 `-XX:MaxGCPauseMillis` 设定期望停顿时间，G1 据此选择每次回收的 Region 数量，这是目标而不是保证。
- **调优更简单**：不用手动划分新生代和老年代的大小，G1 会按目标自行调整。

### 方案对比：CMS 与 G1
| 对比项 | CMS | G1 |
|---|---|---|
| 内存布局 | 连续的新生代和老年代 | 等大小的 Region |
| 老年代算法 | 标记-清除 | 回收时复制整理 |
| 碎片 | 容易产生 | 较少 |
| 停顿时间 | 通常较短，但不易预测 | 可设定期望，更可预测 |
| 额外开销 | 占用 CPU，有浮动垃圾 | 要为 Region 维护额外的记录，占用一定内存 |
| 调优 | 参数多，依赖经验 | 自动化程度较高 |
| 状态 | Java 14 已移除 | Java 9 起默认 |

结论：新项目默认选 G1，不要再选 CMS；仅在老版本 Java 且已有 CMS 调优经验时才考虑继续使用 CMS。

### 进阶：G1 也不是万能的（基础薄弱可先跳过）
- G1 要为每个 Region 记录跨 Region 的引用，有额外的内存和 CPU 开销。
- 如果堆很小，或者回收速度跟不上分配速度，G1 同样会退化为 Full GC。
- 对停顿要求更苛刻的大堆场景，可以考虑 ZGC。

## 易错点
- 以为 CMS 和 G1 都不会 Full GC；回收不及或碎片严重时，两者都可能退化
- 以为 G1 的停顿时间是严格保证的；它只是尽力接近目标
- 以为 CMS 什么场景都比 G1 停顿短；两者各有适用场景，且 CMS 已被移除

## 追问
### [f1] 为什么说 G1 的停顿可预测？
G1 把堆分成 Region，能记录每个 Region 的回收收益和大致耗时，在设定的停顿目标内挑选最划算的若干 Region 回收，因此停顿时间更容易控制。

### [f2] CMS 为什么会产生碎片，怎么办？
因为它用标记-清除，清除只回收死对象占用的空间，不移动存活对象。碎片太多时，JVM 会触发整理式的 Full GC；更根本的办法是换用 G1。
