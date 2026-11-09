---
id: q_01M6ZYJ47X0RJR8B95G9B5AQM6
title: 什么是泛型？
type: concept
difficulty: easy
importance: 2
category: java
tags: [type-system]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
泛型就是把类型当参数传进去，比如 `List<String>`，让编译器在编译时检查类型对不对，也不用手动强转。

## 要点
- [kp1|3] 泛型把操作的数据类型参数化，如 `List<String>` 里的 String
- [kp2|3] 编译器在编译期检查类型，放错类型直接编译报错
- [kp3|2] 取值时不用手动强转，省去 ClassCastException 的风险
- [kp4|2] Java 泛型是编译期的，运行时类型信息会被擦除
- [kp5] 泛型参数只能是引用类型，不能是 int 这样的基本类型

## 详解
### 先搞懂：贴了标签的收纳盒
没有泛型时，List 是一个什么都能装的箱子：往里放字符串、放数字都行，取出来是 Object，要自己强转。如果记错了里面是什么，强转就会在运行时出错。

泛型相当于在箱子上贴标签：“这是装字符串的箱子”。放别的东西，编译器当场拦下；取出来就是字符串，不用转。

后文术语：
- **类型参数**：尖括号里的类型，如 `List<String>` 中的 String。
- **类型擦除**：编译后泛型信息被去掉，运行时看不到。

### 没有泛型会怎样
```java
List list = new ArrayList();
list.add("abc");
list.add(123);
String s = (String) list.get(1); // 编译通过，运行时报 ClassCastException
```
错误要等到运行时才暴露。有了泛型，`List<String>` 放入 123 在编译阶段就报错。

### 泛型能用在哪里
- **泛型类**：`class Box<T>`，T 在使用时才确定；
- **泛型方法**：`<T> T first(List<T> list)`；
- **泛型接口**：如 `Comparable<T>`。

### 类型擦除是什么
Java 的泛型主要靠编译器工作：编译后，`List<String>` 和 `List<Integer>` 在运行时都是 List。所以运行时没法直接判断“这是装字符串的 List”，也不能 `new T()`。这是为了兼容泛型出现之前的老代码。

## 示例
```java
List<String> names = new ArrayList<>();
names.add("Tom");
// names.add(123);          // 编译错误
String first = names.get(0); // 不用强转
```

## 易错点
- 以为泛型在运行时仍然存在；实际编译后类型信息被擦除
- 想写 `List<int>`；泛型参数只能是引用类型，要用 `List<Integer>`
- 以为 `List<Object>` 是 `List<String>` 的父类型；二者没有继承关系

## 追问
### [f1] 泛型的好处是什么？
一是编译期就能发现类型错误，二是取值不用强转，代码更清晰安全。
