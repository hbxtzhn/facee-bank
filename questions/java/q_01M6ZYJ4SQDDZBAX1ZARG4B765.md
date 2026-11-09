---
id: q_01M6ZYJ4SQDDZBAX1ZARG4B765
title: 为什么要用 StringBuilder 拼接字符串？
type: concept
difficulty: easy
importance: 2
category: java
tags: [type-system]
prerequisites: [q_01M6ZYJ4H3WKVHBAJZS21RYRAV]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
String 不可变，每拼一次就产生一个新对象；StringBuilder 是可变的，append 直接在同一个对象上追加，所以大量拼接时更省。

## 要点
- [kp1|3] StringBuilder 内部是可变的字符序列，append 在原对象上追加
- [kp2|3] 用 String 在循环里拼接，每轮都会生成新的中间字符串
- [kp3|2] 拼完用 toString() 得到最终的 String
- [kp4|2] StringBuilder 不是线程安全的，多线程共享要另想办法
- [kp5] 少量、一次性的拼接，直接用 + 就够了

## 详解
### 先搞懂：每次都换新纸，还是在同一张纸上接着写
String 拼接像每加一个字都重新抄一张新纸，旧纸扔掉；StringBuilder 像在同一张纸上接着写。写得越多，前者浪费的纸越多。

场景很常见：循环里拼 SQL、拼日志、拼一大段文字。

后文术语：
- **中间对象**：拼接过程中产生、最后没人用的临时字符串。
- **append**：StringBuilder 在末尾追加内容的方法。

### String 拼接为什么浪费
```java
String s = "";
for (int i = 0; i < 1000; i++) {
    s = s + i;  // 每轮都新建一个字符串，并复制旧内容
}
```
每一轮都要创建新对象、把已有内容复制过去，拼得越长，复制的内容越多，循环次数一大就明显变慢，还会产生大量垃圾对象。

### StringBuilder 怎么做
StringBuilder 内部维护一个可以变化的字符序列，`append` 直接在末尾加，不够位置时才扩容。整个拼接过程基本只有这一个对象，最后调一次 `toString()` 生成 String。

### 什么时候不必用
简单的几个字符串用 `+` 拼成一句话，不在循环里，代码更简洁，没必要改。编译器也会对这类写法做优化，不用刻意规避。

### 线程安全
StringBuilder 的方法没有加同步，多个线程同时 append 同一个对象可能出错。大多数拼接都是方法内的局部变量，不涉及共享，所以通常没问题；确实要多线程共享，见 StringBuffer 相关题目。

## 示例
```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i).append(',');
}
String result = sb.toString();
```

## 易错点
- 以为任何时候 StringBuilder 都比 + 好；少量拼接差别不大，简洁更重要
- 把同一个 StringBuilder 给多个线程同时用
- 忘了 toString()；StringBuilder 不是 String，不能直接当字符串使用

## 追问
### [f1] StringBuilder 和 StringBuffer 选哪个？
方法内部局部使用，选 StringBuilder；StringBuffer 的方法加了同步，多线程共享时才考虑，但这种场景也往往有更清晰的写法。
