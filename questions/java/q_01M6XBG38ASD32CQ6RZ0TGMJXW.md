---
id: q_01M6XBG38ASD32CQ6RZ0TGMJXW
title: Java Stream 是什么，怎么用？
type: concept
difficulty: easy
importance: 2
category: java
tags: [collections]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Stream 是 Java 8 起提供的、对集合做链式加工的工具：中间操作（filter、map）接着返回新的流，终端操作（collect、forEach）触发执行并给出结果。

## 要点
- [kp1|3] 流水线由数据源、若干中间操作、一个终端操作组成
- [kp2|3] 中间操作返回新的 Stream，没有终端操作时不会真正执行
- [kp3|2] 终端操作（collect、forEach、count 等）触发计算并产生结果
- [kp4] Stream 不存储数据，也不修改原集合
- [kp5] 一个 Stream 只能消费一次，用过再用会抛异常

## 详解
### 先搞懂：像工厂流水线
假设有一份订单列表，要“挑出已付款的，取出金额，加起来”。传统写法要写 for 循环、if 判断、累加变量。

Stream 的写法像流水线：原料（集合）进来，依次经过“筛选”“取金额”两道工序，最后在出口“汇总”。每道工序只管自己那一步，读起来就是需求本身。

后文术语：
- **数据源**：流水线的原料，通常是集合或数组。
- **中间操作**：中间的加工工序，做完仍然是流，可以接着加工。
- **终端操作**：最后一步，拿出结果，流水线到此结束。

### 中间操作：返回新的流，而且是懒的
常见的中间操作有 `filter`（按条件筛选）、`map`（把每个元素转成另一个值）、`sorted`（排序）、`distinct`（去重）、`limit`（只取前几个）。

它们都返回一个新的 Stream，所以能一直往后接。但要注意它们是“懒”的：只写中间操作而不写终端操作，什么都不会执行。

### 终端操作：触发执行，给出结果
终端操作才会真正开始处理数据：

- `collect`：收集成 List、Set、Map 等；
- `forEach`：对每个元素做一件事；
- `count`、`sum`（数值流）：统计；
- `anyMatch`、`findFirst`：判断或取一个元素。

终端操作执行完，这个流就用完了，不能再使用。

### 不改原集合
Stream 只读取数据源，不会往原集合里增删元素。结果通过 `collect` 得到一个新的集合。

## 示例
```java
List<Order> orders = ...;
List<String> names = orders.stream()
        .filter(o -> o.isPaid())      // 中间操作：筛选
        .map(Order::getUserName)      // 中间操作：取字段
        .distinct()                   // 中间操作：去重
        .collect(Collectors.toList()); // 终端操作：收集结果
```

## 易错点
- 以为写了 filter、map 就会执行；没有终端操作时整条流水线什么都不做
- 对同一个 Stream 对象调用两次终端操作；第二次会抛 IllegalStateException
- 以为 Stream 会修改原集合；它不会，结果是新的

## 追问
### [f1] Stream 和 for 循环有什么区别？
Stream 以声明式描述“做什么”，代码更短、更易组合；for 循环自己控制“怎么做”，更直观，也方便调试。选哪个看可读性，不是越用 Stream 越好。
