---
id: q_01M6XBNZBR9TM491TYBNY0SGT7
title: 什么时候会触发 Minor GC（Young GC）？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [gc-algorithm, memory-area]
prerequisites: [q_01M6XBG945J00KRDD6XQX1PSVP]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
新对象优先分配在 Eden 区，Eden 放不下新对象时，就会触发一次 Minor GC（Young GC）来清理新生代。

## 要点
- [kp1|3] 新对象优先分配在新生代的 Eden 区
- [kp2|3] Eden 区没有足够空间放新对象时，触发 Minor GC
- [kp3|2] Minor GC 之后 Eden 被清空，存活对象移到 Survivor 或老年代
- [kp4|2] 对象创建越快，Minor GC 触发越频繁
- [kp5] 触发 Minor GC 与老年代是否满无关，老年代满另有触发条件

## 详解
### 先搞懂：门口的垃圾桶满了就要倒
家里门口放一个垃圾桶（Eden 区），平时的垃圾都扔进去。桶装不下新垃圾了，就得先倒一次，才能继续扔。Eden 区装不下新对象时触发 Minor GC，道理一样。

后文用到的术语：

- **Eden 区**：新生代里专门放新创建对象的区域。
- **Minor GC / Young GC**：只回收新生代的垃圾回收。
- **Survivor 区**：新生代里存放熬过回收的对象的区域。

### 触发过程
1. 程序 `new` 对象，JVM 在 Eden 区里给它分配空间。
2. Eden 剩余空间放不下这个新对象，JVM 触发 Minor GC。
3. 回收时，把 Eden 和正在使用的 Survivor 区里还活着的对象复制出去，放到另一块 Survivor 区，年龄够大的对象放进老年代。
4. Eden 整体清空后，新对象继续在 Eden 里分配。

### 触发频率由什么决定
- **对象创建速度**：每秒创建的对象越多，Eden 填得越快，触发越频繁。
- **Eden 大小**：Eden 越小，装满得越快。

Eden 区只是新生代的一部分，所以新生代设得大，Eden 通常也更大，Minor GC 的频率会降低。

## 易错点
- 以为必须整个新生代都满了才触发；通常是 Eden 区放不下新对象时就触发
- 以为 Minor GC 不会暂停应用；它同样会 STW，只是时间较短
- 以为 Minor GC 只和新生代有关系；它也要检查晋升到老年代时老年代是否放得下，放不下会引发 Full GC

## 追问
### [f1] Minor GC 过于频繁说明什么？
通常说明 Eden 太小，或者对象创建太快。可以适当增大新生代，也可以检查代码里是否有不必要的对象创建。
