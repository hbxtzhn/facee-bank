---
id: q_01M6XBGFKRNVJX1180XX4DZNDH
title: Java 有哪些类加载器？
type: concept
difficulty: easy
importance: 2
category: jvm
tags: [class-loading]
prerequisites: [q_01M6XBGETV46EJNC6JY9R5X884]
appliesTo: ["Java 8 为扩展类加载器；Java 9 起改为平台类加载器"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：java.lang.ClassLoader", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ClassLoader.html" }
  - { title: "JEP 261: Module System（Class loaders 一节：平台类加载器）", url: "https://openjdk.org/jeps/261" }
  - { title: "Oracle JDK 8 文档：Extension Mechanism Architecture", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/extensions/spec.html" }
---

## 一句话
Java 自带三种类加载器：启动类加载器加载 JDK 核心类，扩展（Java 9 起叫平台）类加载器加载扩展类，应用类加载器加载你自己写的代码；开发者还可以自定义类加载器。

## 要点
- [kp1|3] 启动类加载器（Bootstrap）：加载 JDK 核心类库，如 `java.lang.String`
- [kp2|3] 应用类加载器（Application）：加载 classpath 下你自己写的类和第三方库
- [kp3|2] 扩展类加载器（Java 8）在 Java 9 起改为平台类加载器（Platform）
- [kp4|2] 可以继承 ClassLoader 自定义类加载器，用来从网络、加密文件等地方加载类
- [kp5] 启动类加载器由 JVM 内部实现，在 Java 代码里表现为 `null`

## 详解
### 先搞懂：三个层级的图书管理员
想象一个图书馆有三个管理员：一个管最核心的馆藏（JDK 核心类），一个管扩展区的书（扩展类），一个管读者自己捐的书（你自己的代码）。要找一本书，各有各的负责区域。

后文用到的术语：
- **类加载器**：负责按类名找到并读入 .class 文件的组件。
- **classpath**：告诉 JVM 去哪里找你写的类的路径。
- **自定义类加载器**：开发者自己写的、继承 `ClassLoader` 的类加载器。

### 启动类加载器：负责 JDK 核心类
加载 `java.lang.String`、`java.util.List` 这类 JDK 核心类。它是 JVM 内部实现的，所以在 Java 代码里拿它的引用会得到 `null`。

### 扩展类加载器 / 平台类加载器
Java 8 里叫扩展类加载器，负责加载 JDK 的扩展目录里的类。Java 9 引入模块化后，改叫平台类加载器，加载一部分平台提供的模块。

### 应用类加载器：负责你写的代码
也叫系统类加载器，负责加载 classpath 下的类，包括你自己写的和引入的第三方 jar。平常 `Main.class.getClassLoader()` 得到的就是它。

### 自定义类加载器
继承 `ClassLoader` 重写相应方法，可以从别处加载类，比如网络、加密文件；也用于实现热部署、隔离不同模块。

## 示例
```java
System.out.println(String.class.getClassLoader());   // null：启动类加载器
System.out.println(Main.class.getClassLoader());     // 应用类加载器
System.out.println(Main.class.getClassLoader().getParent()); // Java 8 为扩展类加载器，Java 9+ 为平台类加载器
```

## 易错点
- 以为 `String.class.getClassLoader()` 会返回启动类加载器的对象；实际返回 `null`
- 以为 Java 9 之后仍然叫扩展类加载器；已改为平台类加载器
- 以为你写的类由启动类加载器加载；它由应用类加载器加载

## 追问
### [f1] 这几种类加载器是继承关系吗？
不是，它们之间是"父子"组合关系：应用类加载器的父加载器是扩展/平台类加载器，再往上是启动类加载器，这是靠字段引用，不是类继承。

### [f2] 为什么需要自定义类加载器？
为了从非常规来源加载类、实现热部署、或者在同一个程序里隔离不同版本的类，例如 Tomcat 隔离不同的 Web 应用。
