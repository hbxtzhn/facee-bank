---
id: q_01M6ZYJ8MV50PPMW04F3XGV0YQ
title: 如何排查 Java 内存泄漏？
type: scenario
difficulty: medium
importance: 2
category: jvm
tags: [performance-diagnosis]
prerequisites: [q_01M6XBGGS35P0MM6X0YARGNB9S]
references:
  - { title: "Java SE 21 故障排查指南：Troubleshoot Memory Leaks", url: "https://docs.oracle.com/en/java/javase/21/troubleshoot/troubleshooting-memory-leaks.html" }
  - { title: "JDK 21 jcmd 手册：GC.heap_dump", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html" }
  - { title: "JDK 21 jstat 手册：-gcutil", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/jstat.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
先用 top、jstat 看 Full GC 是否越来越频繁，再用 jmap 导出堆 dump，用 VisualVM 找出最多的对象和引用链，回到代码修复。

## 要点
- [kp1|3] 泄漏的迹象：Full GC 越来越频繁，回收后堆占用仍持续升高
- [kp2|3] 用 jmap 或 -XX:+HeapDumpOnOutOfMemoryError 获取堆 dump
- [kp3|2] 用 VisualVM 或 MAT 看哪类对象最多、谁持有它们
- [kp4|2] jps 找进程号，top 看资源占用，jstat 看 GC 次数和各区使用率
- [kp5] 定位到代码后，释放引用、关闭资源或给缓存加上限

## 详解
### 先搞懂：像找“漏水点”，先看水表再找管道
家里水费突然变高，先看水表确认是不是真的在漏，再顺着管道找漏点。内存泄漏排查同样分两步：先确认**确实在漏**，再定位**漏在哪里**。

术语：
- **jstat**：JDK 自带命令，能实时看 GC 次数、各内存区使用率；
- **堆 dump**：某一时刻堆内存的快照，用来分析里面有哪些对象。

### 第一步：确认是不是泄漏
1. `jps` 查出 Java 进程号；
2. `top -p <pid>` 看这个进程的 CPU 和内存占用；
3. `jstat -gcutil <pid> 1000` 每秒输出一次，观察老年代使用率和 Full GC 次数。

判断依据：Full GC 次数持续增加，而每次 GC 后老年代占用基本不降，甚至越来越高，大概率是泄漏。

### 第二步：导出 dump
- 手动：`jmap -dump:live,format=b,file=heap.hprof <pid>`；`live` 表示只导出存活对象，导出前会触发一次 Full GC；
- 自动：启动时加 `-XX:+HeapDumpOnOutOfMemoryError`，OOM 时自动生成。

### 第三步：分析 dump
用 VisualVM 加载离线的 `.hprof` 文件（MAT 也行）：
- 先看按数量或占用大小排序的类，找出异常多的对象；
- 再看它们被谁引用，顺着引用链找到持有者，如某个静态集合；
- 结合业务代码阅读上下文，确认是哪一段逻辑一直在往里放、没有删除。

### 第四步：修复并验证
常见做法：缓存加上限和过期、`finally` 中释放资源、ThreadLocal 用完 `remove`。修复后再观察 Full GC 趋势，确认老年代不再持续升高。

## 示例
```bash
jps                              # 找到进程号
jstat -gcutil 12345 1000         # 每秒看一次 GC 情况，关注 O 列和 FGC 列
jmap -dump:live,format=b,file=heap.hprof 12345
```

## 易错点
- 只看一次 GC 数据就下结论；要观察一段时间的趋势
- 导出 dump 时应用会停顿，且文件可能很大，生产环境要提前评估
- 找到“最多的对象”就改它；要看是谁持有它，根因通常在持有者身上

## 追问
### [f1] 内存泄漏不严重、Full GC 不频繁时怎么发现？
可以长期监控堆使用量趋势，对比同一时间点的两份 dump，看哪类对象数量一直在增长。
