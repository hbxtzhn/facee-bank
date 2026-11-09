---
id: q_01M6XBNY2WYZRP10MDHTSKR4N8
title: 反射的原理是什么？
type: concept
difficulty: medium
importance: 2
category: java
tags: [reflection, class-loading]
prerequisites: [q_01M6XBG49186RD6CSF88AV1WET, q_01M6XBGETV46EJNC6JY9R5X884]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java SE 21 API：java.lang.Class（类说明与 getDeclaredMethods、forName）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Class.html" }
  - { title: "JVMS SE 17 §2.5.4 Method Area、§2.5.5 Run-Time Constant Pool", url: "https://docs.oracle.com/javase/specs/jvms/se17/html/jvms-2.html" }
estimatedMinutes: 3
---

## 一句话
类被加载后，JVM 会保存这个类的结构信息，并生成一个 Class 对象；反射就是通过这个 Class 对象把这些信息读出来，再去创建对象、调用方法。

## 要点
- [kp1|3] 反射的信息来源是类加载：.class 文件的结构被读入 JVM
- [kp2|3] 每个类加载后都有一个 Class 对象，是反射的入口
- [kp3|2] 类的字段、方法、构造器等元数据保存在方法区（元空间）
- [kp4|2] Method.invoke 等调用最终由 JVM 去执行对应的方法
- [kp5] 一个类在同一个类加载器下只有一个 Class 对象

## 详解
### 先搞懂：先有说明书，才能按说明书办事
假设你要操作一台没见过的机器。要先拿到说明书（有哪些按钮、各自做什么），才能按它操作。

Java 里，编译后的 .class 文件就像说明书的原稿。程序运行起来，JVM 把它读进内存，整理成类的“说明书”并保留着。反射就是去翻这本说明书，再据此操作。

后文术语：
- **类加载**：JVM 把 .class 文件读进内存、整理成可用的类的过程。
- **方法区**：JVM 里存放类信息的内存区域，保存类的结构、方法、常量等。
- **Class 对象**：类的信息在堆里的“门面”，反射从它开始。

### 第一步：类加载把信息放进内存
Java 程序分两个阶段：编译和运行。编译得到字节码文件（.class）；运行时，JVM 在需要某个类时加载它。它读取字节码，把类的结构信息（类名、父类、字段、方法、构造器等）存到方法区，并生成一个对应的 Class 对象。

### 第二步：通过 Class 对象读取信息
我们写的 `Class.forName("...")`、`User.class` 拿到的就是这个 Class 对象。调用 `getDeclaredMethods()` 等方法，其实就是让它把方法区里保存的结构信息整理后返回。

### 第三步：基于信息执行操作
- 创建对象：通过构造器的 `newInstance` 在堆里分配对象；
- 调用方法：`Method.invoke` 让 JVM 去执行对应的方法；
- 读写字段：`Field.get/set` 直接访问对象里对应的数据。

### 为什么反射比直接调用慢
直接调用在编译时就确定了调用目标；反射在运行时才去查找，还要做访问权限检查、参数装箱等额外工作。具体慢多少取决于 JDK 版本和场景，不要笼统下结论，关键路径上通常缓存查找结果。

### 进阶：Class 对象和类加载器（基础薄弱可先跳过）
Class 对象的唯一性是相对于类加载器而言的。同一个 .class 文件被两个不同的类加载器加载，会得到两个不同的 Class 对象，它们互相不兼容。这也是某些热部署、容器隔离场景出现类型转换失败的原因。

## 示例
```java
Class<?> c1 = Class.forName("java.lang.String");
Class<?> c2 = String.class;
System.out.println(c1 == c2); // true：同一个类加载器下只有一个 Class 对象
```

## 易错点
- 以为反射是直接读 .class 文件；实际读的是类加载后保存在 JVM 里的信息
- 以为 Class 对象是我们 new 出来的；它由 JVM 在类加载时创建

## 追问
### [f1] 为什么说 Class 对象是反射的入口？
反射要操作的字段、方法、构造器信息都挂在 Class 对象下，拿不到它就无从读取类的结构。
