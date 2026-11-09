---
id: q_01M6XBGB5YTVCAD276P54A925Z
title: 新生代为什么划分 Eden 和 Survivor 区，并用复制算法？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [memory-area, gc-algorithm]
prerequisites: [q_01M6XBNZVKTVDA567PT9MX6AZC]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java SE 8 HotSpot GC 调优指南：Sizing the Generations", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/sizing.html" }
  - { title: "Java SE 8 HotSpot GC 调优指南：Generations", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/generations.html" }
estimatedMinutes: 3
---

## 一句话
新生代对象存活少，适合复制算法；纯对半分会浪费一半内存，所以划成一个大 Eden 加两个小 Survivor（常见比例 8:1:1），只浪费一小块空间。

## 要点
- [kp1|3] 新生代存活对象少，复制的量小，所以用复制算法
- [kp2|3] 复制算法要预留空闲空间，对半分会浪费一半内存
- [kp3|2] Eden 加两个 Survivor 的划分，常见比例是 8:1:1，只预留约十分之一
- [kp4|2] 回收时把 Eden 和使用中的 Survivor 的存活对象复制到另一个 Survivor
- [kp5] 一次回收后存活对象超过 Survivor 容量，多出来的会进入老年代

## 详解
### 先搞懂：搬家时只带必需品
假设要清理一间堆满杂物的房间，大部分东西其实是该扔的，只有少数几件值得留下。最省力的办法是：把要留的几件搬进另一间空房，然后把原来那间整个清空。要留的越少，搬起来越省力。

新生代就是这个情况：对象大多朝生夕死，每次回收存活的只有一小部分。

后文用到的术语：

- **复制算法**：把存活对象复制到空闲区域，原区域整块清空。
- **Eden 区**：新对象诞生的区域。
- **Survivor 区**：存放熬过回收的对象，有两块，分别叫 from 和 to。

### 为什么选复制算法
复制算法的工作量只取决于存活对象的数量，不管垃圾有多少。新生代存活少，复制量小，所以回收很快。而且复制后存活对象是连续摆放的，没有内存碎片，之后分配新对象也快。

### 为什么不是简单对半分
对半分的办法是把新生代分成相等的两块，每次只用一块，另一块空着。问题是总有一半空间闲置，利用率只有一半，很浪费。

既然每次存活的对象很少，其实不需要预留那么大。所以把新生代分成：

- 一个较大的 **Eden** 区，大部分新对象都在这里分配；
- 两个较小的 **Survivor** 区，同一时刻只用一个。

分配新对象只用 Eden 和其中一个 Survivor，另一个 Survivor 空着。常见比例是 Eden:Survivor:Survivor = 8:1:1，也就是只有约十分之一的空间空着。

### 一次回收的过程
1. 回收时，把 Eden 区和正在使用的那个 Survivor 区里的存活对象，一次性复制到空着的 Survivor 区。
2. 然后直接清空 Eden 和原来的 Survivor 区。
3. 两个 Survivor 的角色互换，下次回收再来一遍。

### 万一装不下怎么办
如果某次回收后存活对象太多，放不下一个 Survivor 区，多出来的对象会借助老年代来存放（这叫分配担保），直接进入老年代。

### 进阶：比例并非固定（基础薄弱可先跳过）
- 8:1:1 是常见默认，由 `-XX:SurvivorRatio` 控制；有的收集器会根据运行情况自动调整各区大小，实际比例不一定是 8:1:1。

## 易错点
- 以为 Eden 和 Survivor 是平均分的；Eden 比 Survivor 大得多
- 以为 8:1:1 是任何情况下的固定值；它是常见默认，可调整，部分收集器会自适应
- 以为浪费的空间是一半；这种设计只预留很小一块

## 追问
### [f1] 如果存活对象经常超过 10% 会怎样？
Survivor 区装不下，多出的对象提前晋升到老年代，老年代增长变快，可能更早触发 Full GC。这时需要调整 Survivor 大小或检查对象存活情况。
