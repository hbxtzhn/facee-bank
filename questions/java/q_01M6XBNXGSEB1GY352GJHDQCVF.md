---
id: q_01M6XBNXGSEB1GY352GJHDQCVF
title: 什么是序列化和反序列化？
type: concept
difficulty: easy
importance: 2
category: java
tags: [serialization]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java SE 21 API：java.io.Serializable", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Serializable.html" }
estimatedMinutes: 2
---

## 一句话
序列化是把内存里的对象转成字节流，方便存文件、存数据库或在网络上传输；反序列化是把字节流还原成对象。

## 要点
- [kp1|3] 序列化：对象变成字节流（或文本），反序列化：字节流还原成对象
- [kp2|3] 目的是让对象能离开当前进程的内存：存储或传输
- [kp3|2] 常见方式有 Java 原生序列化、JSON、Protocol Buffers 等
- [kp4] 双方必须约定同一种格式，否则无法还原

## 详解
### 先搞懂：把家具拆开打包寄走
对象在内存里是一个有结构的整体，没法直接寄到另一台机器，也没法直接写进文件。就像要把一套组装好的书架寄给别人：先拆成零件装箱，这是序列化；对方收到后按说明书重新拼起来，这是反序列化。

做项目时到处都在用：接口返回 JSON、把对象缓存进 Redis、消息队列里发消息，背后都是序列化。

后文术语：
- **字节流**：一串字节，文件和网络都能直接处理。
- **格式**：打包的规则，双方要用同一套。

### 为什么需要它
内存里的对象只在当前进程里有意义。想让它存活得比进程更久（存盘），或者去另一台机器（网络调用），就得变成通用的字节形式。反过来，读出来时再还原成对象，程序才能继续用。

### 常见的序列化方式
- **Java 原生序列化**：用 ObjectOutputStream 和 ObjectInputStream 读写。类要实现 Serializable。只适用于 Java 程序之间。
- **JSON**：文本格式，可读性好，跨语言，Web 接口最常用，Java 里常用 Jackson 处理。
- **Protocol Buffers 等二进制格式**：体积小、速度快，需要事先定义数据结构，常用于 RPC。

选择时通常看：要不要跨语言、要不要人能读、对体积和速度的要求。

## 易错点
- 以为序列化只指 Java 原生那一种；JSON 转换同样是序列化
- 以为序列化后的数据任何程序都能读；双方必须使用同一种格式

## 追问
### [f1] 为什么接口常用 JSON 而不是 Java 原生序列化？
JSON 是文本，跨语言、可读、好调试；Java 原生序列化只能 Java 对端使用，对类结构变化也更敏感。
