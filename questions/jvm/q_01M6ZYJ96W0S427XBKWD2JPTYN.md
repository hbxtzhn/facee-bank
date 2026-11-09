---
id: q_01M6ZYJ96W0S427XBKWD2JPTYN
title: JVM 有哪些常用的调优参数？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [performance-diagnosis, gc-collector]
references:
  - { title: "JDK 21 java 命令手册：堆、新生代、元空间与垃圾收集器选项", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html" }
  - { title: "JEP 248：Make G1 the Default Garbage Collector", url: "https://openjdk.org/jeps/248" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
常用参数有堆大小（-Xms、-Xmx、-Xmn）、Eden 比例、晋升年龄阈值、线程栈大小（-Xss）和垃圾收集器选择。

## 要点
- [kp1|3] -Xms 设初始堆，-Xmx 设最大堆，线上常把两者设成一样
- [kp2|3] -Xmn 设新生代大小，-XX:SurvivorRatio 设 Eden 与单个 Survivor 的比例
- [kp3|2] -XX:MaxTenuringThreshold 控制对象在新生代熬过几次 GC 后晋升老年代
- [kp4|2] -Xss 设置每个线程的栈大小，递归深或线程多时才需要调整
- [kp5] 用 -XX:+UseG1GC 等参数选择垃圾收集器；元空间和直接内存也有各自的上限参数

## 详解
### 先搞懂：调参数就是“给房间分大小”
JVM 内存像一套房子：堆是客厅，栈是每个人自己的小桌，元空间放资料。调优参数就是决定每个房间多大、东西放多久搬到大仓库。

术语：
- **新生代**：新创建的对象先放这里，大部分很快就被回收；
- **老年代**：在新生代里活得久的对象搬到这里；
- **Eden / Survivor**：新生代里的分区，新对象先进 Eden，GC 后存活的在两个 Survivor 之间来回倒腾。

### 堆大小
| 参数 | 作用 |
|---|---|
| `-Xms` | 初始堆大小 |
| `-Xmx` | 最大堆大小 |
| `-Xmn` | 新生代大小 |

线上常把 `-Xms` 和 `-Xmx` 设成一样，避免堆在运行时反复扩缩容。

### 新生代内部和晋升
- `-XX:SurvivorRatio=8`：Eden 与单个 Survivor 的比例为 8:1，也就是 Eden:S0:S1 为 8:1:1；
- `-XX:MaxTenuringThreshold`：对象每熬过一次新生代 GC，年龄加一，超过阈值就晋升老年代。它有上限，不能无限调大。

### 栈、元空间和直接内存
- `-Xss`：每个线程栈的大小，调大可以支持更深的递归，但线程多时占用也更多；
- `-XX:MetaspaceSize` / `-XX:MaxMetaspaceSize`：元空间的触发阈值和上限；
- `-XX:MaxDirectMemorySize`：直接内存上限。

### 垃圾收集器选择
| 参数 | 收集器 | 特点 |
|---|---|---|
| `-XX:+UseSerialGC` | Serial | 单线程，适合小内存、单核环境 |
| `-XX:+UseParallelGC` | Parallel | 追求吞吐量 |
| `-XX:+UseG1GC` | G1 | 兼顾吞吐和停顿，JDK 9 起在服务器配置下为默认 |
| `-XX:+UseZGC` | ZGC | 追求极低停顿 |

结论：没有明确问题时，先用默认收集器和合理的堆大小；有 GC 日志或监控证明瓶颈，再有针对性地调参数。

## 示例
```bash
java -Xms2g -Xmx2g -Xss512k \
     -XX:+UseG1GC \
     -XX:+HeapDumpOnOutOfMemoryError \
     -jar app.jar
```

## 易错点
- 照搬网上的参数；不同业务、不同 JDK 版本的合适值不同
- 一遇到问题就调参数；多数性能问题根源在代码，调参数只是缓解
- 同时设置多个收集器参数；一个 JVM 只能选一种收集器

## 追问
### [f1] 为什么线上常把 -Xms 和 -Xmx 设成一样？
这样 JVM 启动时就申请好堆，运行中不会因为扩容、缩容而产生额外的 GC 和停顿，内存占用也更稳定、可预测。
