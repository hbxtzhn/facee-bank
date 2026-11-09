---
id: q_01M6XBFZTSPMHVQE5AN77AZK14
title: HashMap 是什么，怎么存取键值对？
type: concept
difficulty: easy
importance: 3
category: java
tags: [hash-table, collections]
prerequisites: [q_01M6XBFZJMZD7VG6THZ137E4WW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
HashMap 是基于哈希表的键值对容器：put 时根据 key 的哈希码决定存放位置，get 时按同样方式定位，再用 equals 找到对应的 value。

## 要点
- [kp1|3] HashMap 以 key 到 value 的映射存数据，key 不能重复
- [kp2|3] put 和 get 都先用 key 的 hashCode 定位桶，再用 equals 比对 key
- [kp3|2] 同一个桶里的多个元素，会用链表或红黑树串起来
- [kp4|2] 重复 put 同一个 key，新值会覆盖旧值
- [kp5] 允许一个 null key，不是线程安全的

## 详解
### 先搞懂：像有分格的储物柜
想象一排带编号的储物柜。存东西时，先根据你的名字算出一个柜号，把东西放进去；取东西时，再算一次柜号，直接走过去。如果有两个人算出同一个柜号，就在这个柜子里叠着放，取的时候再核对名字。

`HashMap` 就是这样：key 是名字，value 是东西，柜子就是**桶**。

后文用到的词：

- **键值对**：一个 key 对应一个 value，通过 key 找 value。
- **桶**：HashMap 内部数组里的一个位置。
- **哈希码**：key 的 `hashCode()` 返回的整数。

### put：怎么存
`map.put(key, value)` 大致经过三步：

1. 用 key 的哈希码算出落在哪个桶；
2. 桶里还没有元素，直接放进去；
3. 桶里已有元素，就逐个用 `equals` 对比 key：找到相同的 key，就用新 value 覆盖旧值；没有相同的，就把这一对加到这个桶里。

### get：怎么取
`map.get(key)` 同样先算出桶，再在桶里用 `equals` 找到匹配的 key，返回对应的 value；找不到就返回 null。

所以 key 必须正确地实现 `hashCode` 和 `equals`：如果 key 的 hashCode 不稳定，存进去以后就可能找不到。String、Integer 这类常用的 key 已经实现好了。

### 同一个桶里怎么放
不同的 key 可能落在同一个桶里。JDK 8 起，桶里的元素先用链表连起来，数量变多时会转成红黑树，让查找不至于太慢。具体的转换阈值属于实现细节，了解就行。

### 其他特点
- key 不重复，value 可以重复；
- 允许一个 null key 和多个 null value；
- 不保证遍历顺序；
- 不是线程安全的，多线程要同时读写时，应使用 ConcurrentHashMap。

## 示例
```java
Map<String, Integer> stock = new HashMap<>();
stock.put("apple", 10);
stock.put("apple", 8);                 // 同一个 key，覆盖旧值
System.out.println(stock.get("apple")); // 8
System.out.println(stock.get("pear"));  // null
```

## 易错点
- 以为 HashMap 会按插入顺序遍历；它不保证顺序，需要顺序用 LinkedHashMap
- 用可变对象当 key，改了影响哈希码的字段，就再也取不到原来的值
- 多线程同时修改 HashMap，结果不可预期，应换成线程安全的容器
- 自定义类做 key 时只重写 equals 不重写 hashCode，会出现取不到值或重复

## 追问
### [f1] HashMap 怎么保证 key 不重复？
put 时先按哈希码找桶，再用 equals 对比桶里已有的 key。如果找到相等的 key，就覆盖它的 value，不会新增一条。

### [f2] HashMap 和 Hashtable 有什么区别？
Hashtable 是较老的实现，方法大多加了同步，不允许 null key 和 null value。HashMap 不是线程安全的，允许 null，日常更常用。要线程安全，通常选 ConcurrentHashMap。
