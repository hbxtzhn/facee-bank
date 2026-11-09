---
id: q_01M6XBGE4SKJEYKC6WNR16389X
title: 如何选择合适的垃圾收集器？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [gc-collector, performance-diagnosis]
prerequisites: [q_01M6XBGBVTQS9VEYNPH4VSS82C, q_01M6XBGC3YTS5TRR2AWMWBQWQ6]
appliesTo: ["ZGC 生产可用：Java >= 15", "CMS：Java <= 13"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Oracle JDK 21 垃圾收集调优指南：Available Collectors", url: "https://docs.oracle.com/en/java/javase/21/gctuning/available-collectors.html" }
  - { title: "JEP 377: ZGC: A Scalable Low-Latency Garbage Collector (Production)", url: "https://openjdk.org/jeps/377" }
  - { title: "JEP 363: Remove the Concurrent Mark Sweep (CMS) Garbage Collector", url: "https://openjdk.org/jeps/363" }
---

## 一句话
没有特殊要求就用默认的 G1；小堆或单核选 Serial，追求吞吐量选 Parallel，对停顿要求极严、堆又很大选 ZGC。

## 要点
- [kp1|3] 默认选 G1：在吞吐和停顿之间比较均衡，Java 9 起就是默认收集器
- [kp2|3] 小堆或单核、没有停顿要求，用 Serial
- [kp3|2] 只看整体吞吐量、能接受较长停顿（批处理），用 Parallel
- [kp4|2] 大堆且要求停顿很短，用 ZGC
- [kp5] CMS 已在 Java 14 移除，新项目不要再选

## 详解
### 先搞懂：选收集器就是选"你更怕什么"
选收集器本质上是在三件事里取舍：**吞吐量**（业务代码占 CPU 的比例）、**停顿时间**（业务被暂停多久）、**内存占用**。这三者很难同时做到最好。

可以想成选车：省油（吞吐）、平稳（低停顿）、便宜（占用少），你得先说清最在意哪个。

后文用到的术语：
- **吞吐量**：业务代码运行时间占总时间的比例。
- **停顿时间**：GC 暂停业务线程的时长。
- **堆**：JVM 存放对象的内存区域。

### 先看你最在意什么
- **在线接口，希望响应稳定**：选 G1 或 ZGC。
- **后台批处理，只要总时间短**：选 Parallel。
- **很小的程序或单核机器**：选 Serial，开销最小。

### 方案对比：几种收集器怎么选
| 收集器 | 特点 | 适合场景 | 注意 |
|---|---|---|---|
| Serial | 单线程，回收时暂停全部业务线程 | 小堆、单核、客户端工具 | 堆大了停顿明显 |
| Parallel | 多线程并行回收，重吞吐 | 批处理、离线计算 | 单次停顿可能较长 |
| G1 | Region 化，停顿可设目标 | 大多数在线服务，大中型堆 | 目标不是保证 |
| ZGC | 大部分工作并发，停顿很短 | 大堆、延迟要求很严 | Java 15 起生产可用 |
| CMS | 并发标记清除 | 老项目 | Java 14 已移除 |

结论：默认 G1；有明确的吞吐优先需求换 Parallel；堆很大、延迟要求苛刻时再评估 ZGC；小堆或单核用 Serial。

### 怎么确认选对了
- 先用默认配置跑，开启 GC 日志，观察停顿时间和 GC 频率。
- 只有出现了真实问题（停顿超标、吞吐不足）再换收集器或调参，换完要对比日志和监控。
- 同一个应用在不同堆大小、不同 CPU 核数下表现也不同，要用接近生产的环境验证。

## 示例
```bash
# 选择收集器的启动参数示例
java -XX:+UseSerialGC    -jar app.jar   # 小堆、单核
java -XX:+UseParallelGC  -jar app.jar   # 吞吐优先
java -XX:+UseG1GC        -jar app.jar   # 通用，Java 9+ 默认
java -XX:+UseZGC         -jar app.jar   # 大堆、低延迟，Java 15+
```

## 易错点
- 以为最新的收集器一定最好；要看业务是吞吐优先还是延迟优先
- 没看 GC 日志就盲目换收集器、调参数
- 在 Java 14 以后的版本里还想用 CMS；它已被移除

## 追问
### [f1] 为什么说 G1 适合作为默认选择？
它在吞吐和停顿之间比较均衡，能设置期望停顿时间，调优相对简单，对大多数在线服务都够用，所以从 Java 9 起成为默认收集器。

### [f2] 什么情况下要考虑 ZGC？
堆很大，且对停顿时间要求很严格，比如实时交易、低延迟接口。ZGC 把大部分工作放在并发阶段，停顿很短，但要结合版本和压测评估。
