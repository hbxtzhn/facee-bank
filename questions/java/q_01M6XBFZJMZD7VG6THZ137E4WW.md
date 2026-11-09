---
id: q_01M6XBFZJMZD7VG6THZ137E4WW
title: hashCode 方法是做什么的？
type: concept
difficulty: easy
importance: 2
category: java
tags: [object-methods, hash-table]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
hashCode 返回一个 int 整数，称为哈希码；HashMap、HashSet 等哈希集合用它快速决定对象放进哪个位置。

## 要点
- [kp1|3] hashCode 定义在 Object 里，返回一个 int
- [kp2|3] 哈希集合用哈希码决定对象放进哪个桶，查找时先看桶
- [kp3|2] 两个 equals 相等的对象，hashCode 必须相同
- [kp4|2] hashCode 相同的对象不一定 equals 相等，这叫哈希冲突
- [kp5] 同一个对象在字段不变时，多次调用 hashCode 结果一致

## 详解
### 先搞懂：图书馆先看分区，再找书
想象你去图书馆找一本书。如果书是乱放的，只能一本本翻。图书馆的做法是先给每本书算一个分区号：科技类放 A 区，小说放 B 区。找书时，先算出分区号，直接走到那个区，再在区里找。

`hashCode` 就是对象的“分区号”。HashMap、HashSet 这类集合存对象时，先用它算出放在哪个位置，取的时候同样先算，再到那个位置里找，不用从头翻到尾。

后文用到的词：

- **哈希码**：hashCode 返回的那个 int 整数。
- **桶**：哈希集合里一个个存放位置，同一个桶里可以放多个对象。
- **哈希冲突**：不同对象算出了同样的哈希码或落进同一个桶。

### hashCode：给对象一个整数
`hashCode()` 定义在 `Object` 里，每个类都有。默认实现通常和对象的身份有关，不同对象一般得到不同的值。`String`、`Integer` 等类重写了它，用内容算哈希码。

自己的类按业务字段重写 `equals` 时，也要按同样的字段重写 `hashCode`，可以用 `Objects.hash(字段...)`。

### 它和 equals 的约定
- 两个对象 `equals` 相等，它们的 `hashCode` 必须相同；
- 两个对象 `hashCode` 相同，不代表 `equals` 相等，因为不同对象也可能算出同一个号；
- 对象参与 equals 的字段没变时，多次调用 `hashCode` 要返回同一个值。

### 哈希集合怎么用它
放入时：先算哈希码，决定落进哪个桶。查找时：先算哈希码找到桶，再在桶里用 `equals` 一个个比对。所以哈希码越分散，每个桶里的对象越少，查找越快。

## 示例
```java
String a = "abc";
String b = new String("abc");
System.out.println(a.equals(b));                  // true
System.out.println(a.hashCode() == b.hashCode()); // true，equals 相等则 hashCode 必须相同
```

## 易错点
- 以为 hashCode 相同就是同一个对象；不同对象也可能算出相同值
- 以为 hashCode 就是对象的内存地址；它只是一个整数，不保证是地址
- 把会变的字段用来算 hashCode，对象放进集合后字段一改，就再也找不到它了
- 只重写 equals，没有重写 hashCode，放进 HashSet 时会重复

## 追问
### [f1] 为什么用哈希码，而不直接用 equals 逐个比较？
逐个比较要把所有元素翻一遍，元素越多越慢。先用哈希码定位到桶，只需要在那一个桶里比较，范围小得多。
