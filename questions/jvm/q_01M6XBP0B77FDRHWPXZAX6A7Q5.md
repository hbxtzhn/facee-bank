---
id: q_01M6XBP0B77FDRHWPXZAX6A7Q5
title: G1 的垃圾收集工作流程是怎样的？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [gc-collector]
prerequisites: [q_01M6XBG9CJ1NN7Z7NZ5BX0CP90, q_01M6XBGD643VQTH1N2G6ZAJVV1]
appliesTo: ["Java >= 9 默认 G1；G1 本身自 Java 7 起可用"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
G1 先在后台并发标记，找出各 Region 里的存活情况，再做混合收集：优先回收垃圾最多、收益最高的那些 Region，包括新生代和部分老年代。

## 要点
- [kp1|3] 并发标记阶段和业务线程同时运行，用来统计每个 Region 里有多少垃圾
- [kp2|3] 混合收集同时回收新生代和部分老年代 Region，优先选收益高的
- [kp3|2] 回收时把存活对象复制到别的 Region，既回收垃圾又整理碎片
- [kp4|2] 可用 `-XX:MaxGCPauseMillis` 设置期望停顿时间，G1 据此决定一次回收几个 Region
- [kp5] 极端情况下回收不及，会退化为 Full GC

## 详解
### 先搞懂：先摸底，再挑最划算的地方清理
假设你要清理一个大仓库，时间有限。聪明的做法是：先巡视一遍，记下每个格子里有多少废品；然后每次只清理废品最多的几个格子，花的时间少，腾出的地方多。

G1 就是这么做的。它把堆分成很多 Region，先摸清每个 Region 的垃圾量，再优先清理"回收价值最高"的 Region，所以叫 Garbage First。

后文用到的术语：
- **并发标记**：GC 线程和业务线程同时运行，标出存活对象。
- **混合收集**：一次回收中，同时包含新生代 Region 和一部分老年代 Region。
- **回收价值**：回收这个 Region 能腾出多少空间，相对于需要花多少时间。

### 年轻代回收：日常的小清理
新对象先放在 Eden Region。Eden 满了，G1 会暂停业务线程，把存活对象复制到 Survivor 或老年代 Region，原来的 Region 整块腾空。这一步是 STW，但因为只处理新生代 Region，通常较短。

### 并发标记：摸清每个 Region 的垃圾
当老年代占用的堆比例达到设定的阈值时，G1 启动一轮并发标记。其中大部分时间都和业务线程并发运行，不会暂停业务线程；只有开头和结尾的少数步骤需要短暂暂停。

标记结束后，G1 就知道每个老年代 Region 里存活对象有多少、垃圾有多少。

### 混合收集：优先回收收益最高的 Region
并发标记完成后，接下来几次回收就是混合收集：除了新生代 Region，还会顺带回收一部分垃圾最多的老年代 Region。

G1 会根据你设定的期望停顿时间，估算一次能回收多少个 Region，挑价值最高的那些。回收时把存活对象复制到空的 Region，所以回收的同时也整理了碎片。老年代的 Region 一轮回收不完，分多次慢慢回收。

### 进阶：失败时怎么办（基础薄弱可先跳过）
- 如果对象分配速度太快、回收跟不上，G1 会退化为 Full GC，这时停顿会很长，需要调大堆或调整阈值。
- 启动并发标记的阈值参数是 `-XX:InitiatingHeapOccupancyPercent`。
- 期望停顿时间 `MaxGCPauseMillis` 只是目标，不是保证。

## 示例
```bash
java -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -jar app.jar
```

## 易错点
- 以为 G1 的停顿时间是严格保证的；它只是尽力满足期望值
- 以为并发标记整个过程都不暂停；少数步骤仍需短暂 STW
- 以为 G1 每次都回收整个老年代；它每次只挑一部分 Region

## 追问
### [f1] G1 为什么叫 Garbage First？
因为它总是优先回收垃圾最多、收益最高的 Region，用最少的时间腾出最多的空间。

### [f2] G1 会产生内存碎片吗？
回收时 G1 把存活对象复制到空 Region，相当于顺便整理，所以整体上碎片问题比 CMS 轻。
