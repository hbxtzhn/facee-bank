---
id: q_01M6XBG945J00KRDD6XQX1PSVP
title: Minor GC 和 Full GC 分别回收哪些区域？
type: concept
difficulty: easy
importance: 2
category: jvm
tags: [gc-algorithm, memory-area]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Minor GC 只回收新生代，速度快、停顿短；Full GC 回收整个堆（新生代加老年代，通常还包括方法区），停顿长，要尽量避免。

## 要点
- [kp1|3] Minor GC（也叫 Young GC）只回收新生代
- [kp2|3] Full GC 回收新生代和老年代，一般还会清理方法区
- [kp3|2] Minor GC 频繁但停顿短，Full GC 少见但停顿长
- [kp4] 两者回收时通常都会暂停应用线程（STW）

## 详解
### 先搞懂：小扫除和大扫除
家里有「每天倒垃圾」和「年底大扫除」两种清理。每天倒垃圾只处理门口那一堆，几分钟就好；年底大扫除要把每个房间都翻一遍，花时间多，会打乱正常生活。

JVM 里也一样：新生代放新对象，天天清；老年代放老对象，不勤清。

后文用到的术语：

- **新生代**：存放新创建对象的区域。
- **老年代**：存放活得久的对象的区域。
- **STW（Stop The World）**：回收时暂停所有应用线程。

### Minor GC：只清新生代
新生代的 Eden 区满了，就会触发 Minor GC。它只回收新生代，把存活对象复制到 Survivor 区，必要时把年龄够大的对象晋升到老年代。新生代里存活的对象少，所以回收快，停顿通常很短。

### Full GC：清整个堆
Full GC 回收新生代、老年代，通常连方法区（元空间）也一起处理。要处理的内存多，老年代对象存活多，所以耗时长，停顿明显。线上服务如果频繁 Full GC，用户会感觉到卡顿甚至超时，所以要尽量避免。

### 区别一览
- **回收范围**：Minor GC 只有新生代，Full GC 是整个堆。
- **频率**：Minor GC 比较频繁，Full GC 应该很少发生。
- **停顿**：Minor GC 短，Full GC 长。

还有两个相关的名字：Major GC 一般指只针对老年代的回收，Mixed GC 是 G1 特有的混合回收。这些叫法在不同资料里含义不完全一致，面试时先说清楚自己指的范围。

## 易错点
- 以为 Minor GC 完全不暂停应用；它同样会 STW，只是时间短
- 以为 Full GC 只回收老年代；它是整个堆，还包括方法区
- 以为 Major GC 和 Full GC 一定是一回事；不同资料叫法不一致

## 追问
### [f1] 什么情况会触发 Full GC？
常见原因：老年代空间不足、晋升时老年代放不下、元空间不足、代码里调用了 `System.gc()` 等。具体触发条件和收集器有关。
