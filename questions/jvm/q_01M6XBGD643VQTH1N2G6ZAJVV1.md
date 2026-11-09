---
id: q_01M6XBGD643VQTH1N2G6ZAJVV1
title: G1 垃圾收集器的堆是怎么划分的？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [gc-collector, memory-area]
prerequisites: [q_01M6XBGBVTQS9VEYNPH4VSS82C]
appliesTo: ["Java >= 9 默认 G1；G1 本身自 Java 7 起可用"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
G1 把整个堆切成许多大小相等的 Region，每个 Region 可以灵活充当 Eden、Survivor 或老年代；超过半个 Region 的大对象放进专门的 Humongous 区。

## 要点
- [kp1|3] 堆被划分为大小相等的 Region，不再是连续的新生代和老年代两大块
- [kp2|3] 每个 Region 的角色可以变化：Eden、Survivor、老年代，或空闲
- [kp3|2] 对象大小达到半个 Region 及以上就属于大对象，放进 Humongous 区
- [kp4] Region 大小是 2 的幂，范围为 1MB 到 32MB，可用 `-XX:G1HeapRegionSize` 指定

## 详解
### 先搞懂：把大仓库隔成一格一格的小格子
传统收集器把堆分成两大块：一块放新生代，一块放老年代，大小基本固定。就像仓库分成"新货区"和"旧货区"，哪个区不够用就很难腾挪。

G1 的做法是把整个仓库隔成很多一样大的格子，每个格子叫一个 **Region**。今天这个格子放新货，明天回收后可以改放旧货，灵活得多。

后文用到的术语：
- **Region**：堆被切成的等大小小块，G1 回收的基本单位。
- **Eden / Survivor**：新生代的两种区域，新对象在 Eden，熬过一次回收后到 Survivor。
- **Humongous 区**：专门放大对象的 Region。

### Region：角色不固定的小格子
每个 Region 在某一时刻有一个角色：Eden、Survivor、老年代，或者空闲。角色可以变化：一个 Region 被回收清空后，可以重新当作 Eden 使用。

新生代和老年代在逻辑上仍然存在，但它们由许多不连续的 Region 组成。这样 G1 可以只挑选一部分 Region 回收，而不必每次回收整个新生代或老年代，更容易控制停顿时间。

### Humongous：大对象住专门的格子
如果一个对象的大小达到半个 Region 及以上，就被认为是大对象。比如 Region 是 2MB，一个 1MB 以上的对象就算大对象。

大对象直接放进 Humongous 区；如果一个 Region 装不下，就占用多个连续的 Region。大对象分配和回收的代价都比较高，所以应尽量避免频繁创建超大对象。

### 进阶：Region 大小怎么定（基础薄弱可先跳过）
Region 大小由 JVM 根据堆大小自动选择，必须是 2 的幂。堆越大，默认的 Region 也越大。如果程序有不少接近 Region 一半大小的对象，可以用 `-XX:G1HeapRegionSize` 调大 Region，让它们不再算大对象。

## 示例
```bash
java -XX:+UseG1GC -XX:G1HeapRegionSize=4m -Xmx8g -jar app.jar
```

## 易错点
- 以为 G1 没有新生代和老年代；仍然有，只是它们由不连续的 Region 组成
- 以为 Humongous 是和 Region 无关的独立内存；它由一个或多个连续的 Region 构成
- 以为超过整个 Region 才算大对象；达到半个 Region 就算

## 追问
### [f1] G1 为什么要把堆分成 Region？
分成 Region 后，G1 可以每次只回收收益最高的一部分 Region，而不是整个新生代或老年代，这样能控制每次回收的停顿时间，同时不需要预先固定新生代和老年代的大小。
