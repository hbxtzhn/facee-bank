---
id: q_01M6XBP7R8ESH4N9Z29RM4W1WJ
title: ThreadLocalMap 怎么解决哈希冲突？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [thread-local, hash-table]
prerequisites: [q_01M6XBP5QQ719CQRSMDFYYC52K]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "OpenJDK 21 源码：java/lang/ThreadLocal.java（ThreadLocalMap、nextIndex）", url: "https://github.com/openjdk/jdk/blob/jdk-21+35/src/java.base/share/classes/java/lang/ThreadLocal.java" }
---

## 一句话
ThreadLocalMap 用开放定址法解决哈希冲突：下标被别的 key 占了，就顺着数组往后一个个找空位，找到末尾回到头部继续。

## 要点
- [kp1|3] ThreadLocalMap 用开放定址法（线性探测），不用 HashMap 那样的链表
- [kp2|3] 目标位置被占用时，依次检查下一个槽位，直到找到空位或相同的 key
- [kp3|2] 查找时同样从原下标往后找，遇到空槽位才停止，说明 key 不存在
- [kp4] 探测到 key 已被回收的失效 Entry 时，会顺手清理或替换它

## 详解
### 先搞懂：停车位被占了就往后找
哈希表的做法是：根据 key 算出一个编号，放进对应编号的格子。但不同的 key 可能算出同一个编号，这就叫**哈希冲突**。

比如停车场每辆车有个「推荐车位号」，推荐的位置被占了怎么办？

- HashMap 的办法：同一个车位上叠着放，用链表串起来；
- ThreadLocalMap 的办法：看下一个车位空不空，不空就再看下一个，找到空位就停。

后文用到的词：
- **哈希冲突**：不同的 key 算出了同一个数组下标。
- **开放定址法**：冲突时在数组里按某个规则往后找空位，所有数据都直接存在数组里。
- **线性探测**：开放定址法里最简单的一种，每次往后挪一格。

### 存值：从下标开始往后找
调用 `set` 时，大致顺序如下：

1. 用 key 的哈希值算出初始下标 `i`；
2. 看 `table[i]`：如果是空的，直接放进去；
3. 如果有 Entry 且 key 相同，说明是同一个 ThreadLocal，覆盖 value；
4. 如果 key 不同，说明冲突，转到下一个下标 `i + 1`（到达数组末尾就回到 0），重复上面的判断；
5. 如果遇到 key 已经被回收的失效 Entry，会把它替换掉，同时做一些清理。

### 取值：同样从下标开始往后找
`get` 时先到初始下标看，key 一致就返回；不一致就往后继续找，直到遇到空槽位为止，遇到空槽位说明这个 key 没存过。

所以数据存放的位置，可能不在它「应该在」的下标上，而是在后面某个位置。这也是为什么删除和清理时要处理好后面元素的位置，不能随便把中间的槽位变成空的，否则后面的 Entry 会找不到。

### 为什么这样设计
ThreadLocalMap 一般存的数据不多，一个线程里的 ThreadLocal 变量通常也就几个。这种数据量小的场景，用数组加线性探测结构简单、没有额外的链表节点，对缓存也友好。HashMap 的拉链法更适合数据量大且需要处理大量冲突的通用场景。

### 进阶：探测式清理（基础薄弱可先跳过）
由于 key 是弱引用，探测过程中常会遇到 key 为 null 的失效 Entry。JDK 在 `set`、`get`、`remove` 等操作中会顺带清理这些槽位。后面被挤过去的元素也会被重新放回合适的位置。这样能减少无用数据，但清理是顺带的，并不保证清理干净。

## 示例
```java
// 下标计算与向后探测的简化示意
static int nextIndex(int i, int len) {
    return (i + 1 < len) ? i + 1 : 0; // 到达末尾回到数组头部
}
```

## 易错点
- 以为 ThreadLocalMap 和 HashMap 一样用链表或红黑树；它只有数组，用线性探测
- 以为冲突时会扩容；扩容只在元素数量达到阈值时才发生，与是否冲突无关
- 以为删除一个 Entry 就是把槽位置空；中间留空会让后面的元素查不到，要重新整理

## 追问
### [f1] 开放定址法有什么缺点？
元素扎堆后，查找要往后找很多格，冲突越多越慢；删除元素也比较麻烦。ThreadLocalMap 数据量小，并且有容量阈值控制，所以问题不大。

### [f2] HashMap 是怎么解决冲突的？
HashMap 用拉链法：同一个下标下用链表串起冲突的节点，链表较长时在满足条件时会转成红黑树。
