---
id: q_01M6XBP03CBD1W3GZJERH5Q7X7
title: 对象什么时候会晋升到老年代？
type: concept
difficulty: medium
importance: 3
category: jvm
tags: [memory-area, gc-algorithm]
prerequisites: [q_01M6XBG8KPCG2V9K1SXQ2F3KPH, q_01M6XBNZVKTVDA567PT9MX6AZC]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java SE 8 java 命令参考：-XX:MaxTenuringThreshold、-XX:TargetSurvivorRatio", url: "https://docs.oracle.com/javase/8/docs/technotes/tools/windows/java.html" }
  - { title: "Java SE 8 HotSpot GC 调优指南：Sizing the Generations", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/sizing.html" }
  - { title: "OpenJDK 21 源码 gc_globals.hpp", url: "https://raw.githubusercontent.com/openjdk/jdk/jdk-21%2B35/src/hotspot/share/gc/shared/gc_globals.hpp" }
estimatedMinutes: 3
---

## 一句话
对象在新生代每熬过一次回收，年龄加一，达到阈值（最大 15）就晋升到老年代；有几种情况会提前晋升。

## 要点
- [kp1|3] 每熬过一次新生代回收，对象年龄加一
- [kp2|3] 年龄达到 MaxTenuringThreshold 就晋升到老年代，常见默认 15
- [kp3|2] 大对象可能直接进入老年代
- [kp4|2] Survivor 区装不下的存活对象，提前进入老年代
- [kp5] 不同收集器的默认阈值可能不同，G1 等还会动态调整

## 详解
### 先搞懂：新兵服役几年转正
新生代像新兵营，老年代像老兵营。新兵每熬过一次考核（一次垃圾回收），服役年限加一年；服够了年限，就转去老兵营。这个年限，就是对象的**年龄**，转去老兵营就叫**晋升**。

后文用到的术语：

- **年龄**：对象在新生代熬过的回收次数，记录在对象头里。
- **晋升**：对象从新生代搬到老年代。
- **阈值**：年龄达到多少就晋升，由 `-XX:MaxTenuringThreshold` 设置。

### 正常晋升：年龄够了
1. 新对象在 Eden 区创建，年龄为 0。
2. 第一次 Minor GC 后，如果还活着，被复制到 Survivor 区，年龄加一。
3. 之后每次 Minor GC，只要还活着，年龄继续加一。
4. 年龄达到阈值，下一次回收时被复制到老年代。

年龄信息放在对象头的几个二进制位里，空间有限，所以最大值只能是 15。常见默认阈值是 15，但具体收集器的默认值可能不同（例如 CMS 默认是 6），可以通过 `-XX:MaxTenuringThreshold` 调整。

### 提前晋升的情况
- **大对象直接进老年代**：对象太大时，在新生代来回复制代价高，会直接分配到老年代，不同收集器的具体做法不一样。
- **Survivor 区装不下**：一次回收后存活对象太多，Survivor 区放不下，多出来的直接晋升。
- **动态年龄判断**：JVM 每次回收时会重新选一个阈值，目标是让 Survivor 区保持在约一半满（`-XX:TargetSurvivorRatio`，默认 50%）。
  如果 Survivor 区中某个年龄及以下的对象总大小超过这个比例，年龄大于等于这个年龄的对象就不用等到最大阈值，直接晋升。
  这样可以避免 Survivor 被占满。

### 为什么要这样设计
让对象多熬几次，是为了把「运气不好刚好撞上回收」的短命对象留在新生代清掉，不污染老年代。但也不能一直熬，不然 Survivor 区会被长期存活的对象占满，反复复制又浪费时间，所以设一个阈值。

## 示例
```bash
# 把晋升阈值调成 10（数值仅为示例，需按实际情况测试）
java -XX:MaxTenuringThreshold=10 -jar app.jar
```

## 易错点
- 以为年龄大于 15 才晋升；是达到阈值就晋升，最大值是 15
- 以为所有收集器默认阈值都是 15；部分收集器默认值不同
- 以为晋升只看年龄；Survivor 装不下、动态年龄判断都会让对象提前晋升

## 追问
### [f1] 把阈值调得很大或很小，各有什么影响？
调得大，对象在新生代待得更久，可能被反复复制，占用 Survivor；调得小，对象很快进入老年代，老年代填得更快，Full GC 更频繁。要结合对象存活情况测试。
