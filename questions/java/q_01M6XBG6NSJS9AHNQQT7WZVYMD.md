---
id: q_01M6XBG6NSJS9AHNQQT7WZVYMD
title: Java 有哪些包装类？
type: concept
difficulty: easy
importance: 2
category: java
tags: [type-system]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Java 为 8 种基本类型各准备了一个包装类：Byte、Short、Integer、Long、Float、Double、Character、Boolean，让基本类型能当对象使用。

## 要点
- [kp1|3] 8 种基本类型都有对应的包装类，其中 int 对应 Integer，char 对应 Character
- [kp2|3] 集合、泛型只能放引用类型，所以需要包装类
- [kp3|2] 包装类可以为 null，基本类型不能
- [kp4] 包装类还提供实用方法，如 Integer.parseInt

## 详解
### 先搞懂：给零件装个外壳
基本类型（int、double 等）是最轻、最直接的数据，像散装零件，用起来快。但有些场合（比如往 List 里放数字）要求必须是“对象”，这时需要给零件套上外壳，这个外壳就是包装类。

后文术语：
- **基本类型**：int、long 这类，直接存值。
- **包装类**：把基本类型包成对象的类。

### 对应关系
| 基本类型 | 包装类 |
|---|---|
| byte | Byte |
| short | Short |
| int | Integer |
| long | Long |
| float | Float |
| double | Double |
| char | Character |
| boolean | Boolean |

注意 int 对应 Integer、char 对应 Character，这两个名字和基本类型不一样。

### 为什么需要包装类
- **泛型和集合只能放对象**：`List<Integer>` 可以，`List<int>` 不行；
- **可以表示“没有值”**：比如数据库某个数字列可能为空，用 Integer 的 null 表示；
- **有现成的工具方法**：如 `Integer.parseInt("123")`、`Integer.MAX_VALUE`。

### 使用时的注意
包装类是对象，比基本类型占用更多内存。数值计算密集的地方用基本类型更合适。

## 示例
```java
List<Integer> list = new ArrayList<>();
list.add(10);
int n = Integer.parseInt("123");
Integer maybeNull = null; // 基本类型 int 做不到
```

## 易错点
- 以为 int 的包装类叫 Int；它叫 Integer
- 用 == 比较两个包装类对象的值；比较的是引用，值要用 equals
- 把可能为 null 的包装类直接赋给基本类型；会抛 NullPointerException

## 追问
### [f1] 什么时候用包装类，什么时候用基本类型？
需要放进集合、泛型，或需要表示“没有值”时用包装类；普通的计算和局部变量用基本类型，更轻更快。
