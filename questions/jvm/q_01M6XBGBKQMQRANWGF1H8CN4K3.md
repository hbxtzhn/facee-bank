---
id: q_01M6XBGBKQMQRANWGF1H8CN4K3
title: 大对象为什么直接进入老年代？
type: concept
difficulty: medium
importance: 1
category: jvm
tags: [memory-area, gc-algorithm]
prerequisites: [q_01M6XBNZVKTVDA567PT9MX6AZC]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "OpenJDK 21 源码 gc_globals.hpp：PretenureSizeThreshold", url: "https://raw.githubusercontent.com/openjdk/jdk/jdk-21%2B35/src/hotspot/share/gc/shared/gc_globals.hpp" }
  - { title: "JDK 21 GC 调优指南：Garbage-First 收集器（Humongous Objects）", url: "https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html" }
estimatedMinutes: 3
---

## 一句话
大对象在新生代里来回复制代价高、还容易占满 Eden 和 Survivor，所以超过一定大小的对象直接分配到老年代，减少复制和提前触发回收。

## 要点
- [kp1|3] 新生代回收靠复制，大对象每次复制代价高
- [kp2|3] 超过阈值的大对象直接分配在老年代，避免在新生代来回复制
- [kp3|2] 大对象还可能很快占满 Eden，导致 Minor GC 变频繁
- [kp4|2] 典型的大对象：很长的数组、一次读入的大批数据
- [kp5] 不同收集器处理大对象的方式不同，G1 有专门的大对象区域

## 详解
### 先搞懂：搬家时最怕大件
搬家的时候，小物件几下就搬好；一个大衣柜，搬一次费力，来回搬就更麻烦。如果每次大扫除都要把衣柜在两间房之间搬来搬去，非常不划算，不如一开始就放在固定位置，不挪动。

后文用到的术语：

- **大对象**：需要大块连续内存的对象，常见的是很长的数组、很大的字符串。
- **复制**：新生代回收时把存活对象复制到另一块区域。
- **老年代**：存放活得久的对象的区域。

### 为什么大对象放在新生代不划算
- **复制成本高**：新生代回收靠复制存活对象，大对象每熬过一次回收就要被复制一次，在两个 Survivor 之间来回搬，开销大。
- **占用空间多**：大对象很容易一下子占满 Eden 或装不下 Survivor，导致 Minor GC 变得频繁，或者对象被迫提前晋升。

既然它大概率要在内存里待很久，直接放进老年代更省事。

### 怎么做到的
在 Serial、ParNew 这类收集器中，可以用 `-XX:PretenureSizeThreshold` 设置阈值，超过这个大小的对象不进新生代，直接在老年代分配。这个参数只对部分收集器有效。

G1 的做法不同：它把大小达到区域一半及以上的对象叫大对象（Humongous），放在专门的连续区域里，不走普通新生代分配。

### 副作用
- 老年代空间会被大对象更快消耗，可能引发 Full GC。
- 短命的大对象进了老年代，就要等到老年代回收才能释放，可能造成浪费。

所以实践中更好的做法是从代码上避免创建不必要的大对象，比如分页查询、分批处理。

## 易错点
- 以为所有大对象都直接进老年代；是否直接进入由收集器和参数决定
- 以为 `-XX:PretenureSizeThreshold` 对所有收集器都有效；它只对部分收集器有效
- 以为大对象进老年代就没有问题；大对象过多会让老年代更快被占满

## 追问
### [f1] 一次查询加载几十万行数据，为什么容易引起 Full GC？
这些数据会形成很大的对象，很可能直接进老年代，占用大量空间，如果又很快没用了，会让老年代频繁被填满，触发 Full GC。改成分页或流式处理能缓解。
