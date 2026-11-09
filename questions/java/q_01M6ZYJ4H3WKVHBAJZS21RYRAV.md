---
id: q_01M6ZYJ4H3WKVHBAJZS21RYRAV
title: String 对象能被修改吗？
type: concept
difficulty: easy
importance: 3
category: java
tags: [type-system, memory-area]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
不能。String 对象创建后内容就固定了，拼接、替换等操作都不是改原来的对象，而是生成一个新的 String。

## 要点
- [kp1|3] String 是不可变的，对象创建后内容不能改
- [kp2|3] concat、replace、substring 等方法都返回新的 String，原对象不变
- [kp3|2] 变量可以重新指向新对象，但那是改引用，不是改对象
- [kp4|2] 不可变让 String 天然线程安全，可以放心共享
- [kp5] 大量拼接会产生很多中间对象，应改用 StringBuilder

## 详解
### 先搞懂：刻在石头上的字
把 String 想成刻在石头上的字：想改成别的字，不能擦掉重刻，只能新刻一块石头。原来那块石头没变，还在那儿。

很多人写过 `s = s + "abc"`，觉得是在改 s。其实是新建了一个更长的字符串，再让变量 s 指向它。

后文术语：
- **不可变**：对象创建后，里面的内容不会再变。
- **引用**：变量里存的“指向对象的地址”。

### 看一个例子
```java
String s = "abc";
String t = s.replace("a", "x");
// s 仍然是 "abc"，t 是 "xbc"
```
`replace` 没有改动 s，而是返回了一个新字符串给 t。

### 改变的是引用，不是对象
`s = s + "d"` 执行后，变量 s 指向了新对象，原来的 "abc" 对象没有被改动，如果没人引用它了，就等垃圾回收。

### 为什么设计成不可变
- **线程安全**：内容不会变，多个线程共享一个字符串不会互相干扰；
- **可以放心当 key**：HashMap 的 key 如果会变，会找不到；String 不变，hash 值稳定；
- **安全**：文件路径、网络地址这类字符串不会被中途篡改；
- 也使字符串常量池可以复用相同内容的字符串。

### 代价
每次“修改”都产生新对象，频繁拼接会创建大量中间对象。这类场景用 StringBuilder，见相关题目。

## 易错点
- 以为 `s = s + "x"` 改的是原对象；其实是新建对象并换了引用
- 以为 final String s 才不可变；不可变是 String 类本身的特性，和变量是否 final 无关
- 调用 `s.toUpperCase()` 却不接收返回值；s 不会改变

## 追问
### [f1] 为什么字符串可以放心作为 HashMap 的 key？
因为它不可变，hash 值不会变，放进去之后一定能再用同样的 key 找回来。
