---
id: q_01M6XBG6DCKPVQD2WM230JJR9X
title: Java 集合框架有哪些常用接口？
type: concept
difficulty: easy
importance: 3
category: java
tags: [collections]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
常用的集合接口有三个：List 有序可重复，Set 不重复，Map 存键值对；常见实现类是 ArrayList、HashSet、HashMap。

## 要点
- [kp1|3] List：元素有顺序、可以重复，如 ArrayList、LinkedList
- [kp2|3] Set：元素不重复，如 HashSet、TreeSet
- [kp3|2] Map：键值对，键不重复，如 HashMap、TreeMap
- [kp4|2] List 和 Set 继承自 Collection，Map 是独立的接口
- [kp5] Queue 是另一类常用接口，用于排队，如 LinkedList、ArrayDeque

## 详解
### 先搞懂：三种收纳方式
- List 像排队的队伍：有先后，同一个人可以出现两次；
- Set 像来宾签到簿：一个人只记一次；
- Map 像通讯录：按名字（键）查号码（值）。

做项目时，查询结果列表用 List，去重用 Set，按 id 缓存数据用 Map。

后文术语：
- **接口**：规定集合能做什么，不规定怎么实现。
- **实现类**：真正干活的类，决定性能特点。

### List：有序、可重复
- `ArrayList`：底层是数组，按下标取元素快，中间插入删除要移动元素；
- `LinkedList`：底层是链表，头尾增删方便，按下标访问要从头走。

大多数场景默认用 ArrayList。

### Set：不重复
- `HashSet`：基于哈希，不保证顺序，查找快；
- `TreeSet`：按顺序排好；
- `LinkedHashSet`：保持插入顺序。

判断“是否重复”依赖元素的 equals 和 hashCode。

### Map：键值对
- `HashMap`：最常用，不保证顺序；
- `LinkedHashMap`：保持插入顺序；
- `TreeMap`：按键排序；
- `ConcurrentHashMap`：多线程场景使用。

键不能重复，重复放入会覆盖旧值。

### 接口关系
List、Set、Queue 继承自 Collection；Map 不继承 Collection，它是单独的一套。

## 示例
```java
List<String> list = new ArrayList<>();
Set<String> set = new HashSet<>();
Map<Long, String> map = new HashMap<>();
```

## 易错点
- 以为 Map 是 Collection 的子接口；它是独立的
- 以为 HashSet 保持插入顺序；它不保证顺序，要顺序用 LinkedHashSet
- 往 Set 放自定义对象却没重写 equals 和 hashCode；去重不会生效

## 追问
### [f1] ArrayList 和 LinkedList 怎么选？
大多数场景选 ArrayList：按下标访问快，内存紧凑。只有在头部或中间频繁增删且基本不按下标访问时才考虑 LinkedList。
