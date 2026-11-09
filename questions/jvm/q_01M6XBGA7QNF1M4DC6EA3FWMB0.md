---
id: q_01M6XBGA7QNF1M4DC6EA3FWMB0
title: 频繁 Full GC 该怎么排查和优化？
type: scenario
difficulty: medium
importance: 3
category: jvm
tags: [performance-diagnosis, gc-algorithm]
prerequisites: [q_01M6XBG8KPCG2V9K1SXQ2F3KPH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
先用 jstat 和 GC 日志确认 Full GC 的原因，再 dump 堆定位：常见是大对象进老年代、内存泄漏、长生命周期对象过多；然后改代码或调参数。

## 要点
- [kp1|3] 先用 `jstat -gcutil` 和 GC 日志确认 Full GC 的频率和老年代使用率
- [kp2|3] 常见原因：大对象直接进入老年代、内存泄漏、长生命周期对象过多
- [kp3|2] 怀疑内存问题时 dump 堆，用分析工具找占用最多的对象
- [kp4|2] 优先改代码（分页、释放资源），再考虑调整堆和新生代大小
- [kp5] 提前配置 OOM 时自动 dump，方便事后分析

## 详解
### 先搞懂：仓库为什么老是被清空重来
Full GC 是整个堆的大清理，停顿长。频繁发生，说明老年代这间仓库总被塞满。要排查，就得回答两个问题：是什么东西把它塞满的？这些东西本来该不该存在？

后文用到的术语：

- **老年代**：存放活得久的对象的区域。
- **堆 dump**：把某一时刻堆里的所有对象保存成文件，用于离线分析。
- **内存泄漏**：对象已经没用，但仍被引用，GC 回收不掉。

### 第一步：确认现象
- 用 `jstat -gcutil <pid> 1000` 观察：老年代使用率是否一路上升，Full GC 的次数和每次之后老年代能降多少。
- 开启 GC 日志（如 `-Xlog:gc*`），看每次 Full GC 的触发原因和耗时。

两种典型形态：每次 Full GC 后老年代降下去很多，说明有大量垃圾在积累；Full GC 后老年代几乎没降，说明里面的对象确实是活的，要查是不是泄漏。

### 第二步：按原因逐类排查
- **大对象**：一次性加载太多数据到内存，比如 SQL 没做分页，查出几十万行放进 List，这类大对象容易直接进入老年代。解决：分页、流式处理、限制单次读取数量。
- **内存泄漏**：对象一直被静态集合、缓存、线程里的变量引用着，没用了也不释放；或者 IO 对象用完没有 `close`。解决：找到持有引用的地方，加上清理或过期机制。
- **长生命周期对象过多**：程序频繁生成短时间内存活的对象，但 Survivor 区装不下，或存活时间超过阈值，提前进入老年代。解决：调整新生代、Survivor 大小或晋升年龄，同时优化代码减少这类对象。

### 第三步：dump 堆定位
- 在服务器上用 `jmap -dump:live,format=b,file=heap.hprof <pid>` 或 `jcmd <pid> GC.heap_dump` 导出堆。注意 `live` 会先触发一次 Full GC，线上要谨慎。
- 用 MAT 之类的分析工具打开，按占用大小排序，看哪些类的实例最多、占内存最大，并沿引用链找出是谁持有它们。
- 提前配置 `-XX:+HeapDumpOnOutOfMemoryError`，这样一旦发生 OOM 会自动保存堆。

### 第四步：优化
优先改代码，参数调整只是辅助：

1. 修复泄漏、做分页、减少大对象。
2. 堆本身确实太小，再增大堆。
3. 对象晋升过快，再调整新生代和 Survivor。

## 示例
```bash
jstat -gcutil <pid> 1000
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# 启动参数：OOM 时自动导出堆
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp -jar app.jar
```

## 易错点
- 一上来就加大堆；如果有泄漏，只是延后出问题
- 在线上随手 dump 堆；dump 过程会让应用暂停，堆越大越久
- 把 Full GC 当作一定是 JVM 问题；根源往往在业务代码

## 追问
### [f1] 老年代使用率一直涨、Full GC 后也降不下来，说明什么？
说明老年代里的对象确实是活的，高度怀疑内存泄漏或缓存无上限，要 dump 堆沿引用链找持有者。
