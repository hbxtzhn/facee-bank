---
id: q_01M6ZYJ3NBBMZCG4P25Y13SD6D
title: 什么是处理流（包装流）？
type: concept
difficulty: easy
importance: 1
category: java
tags: [io-stream]
prerequisites: [q_01M6XBG2D2278751ZPNC7HJ204]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
处理流（包装流）是套在已有的流外面、给它增加功能的流，比如加缓冲的 BufferedInputStream，它自己不直接连数据源。

## 要点
- [kp1|3] 处理流包装在已有的流外面，构造时传入另一个流
- [kp2|3] 它为底层流增加功能，如缓冲、转换、按行读取
- [kp3|2] 常见的有 BufferedReader、InputStreamReader、ObjectOutputStream
- [kp4|2] 关闭外层的处理流，会连带关闭它包装的底层流
- [kp5] 可以层层包装，每层增加一种功能

## 详解
### 先搞懂：给水管加装过滤器
接着上一题的比方：节点流是直接插进水井的那根水管，只管把水抽上来。你想让水更干净，就在管子外面加一个过滤器；想要更大水量，再加一个水泵。这些外加的设备，就是处理流。

处理流自己不连水井，它只加工经过它的水。

后文用到的词：

- **节点流**：直接连着数据源或目的地的流。
- **缓冲**：先把数据攒在内存里，凑够一批再一起读写。
- **装饰**：一种设计方式，在不改动原对象的前提下，给它增加功能。

### 常见的处理流及其功能
- **缓冲流**：`BufferedInputStream`、`BufferedOutputStream`、`BufferedReader`、`BufferedWriter`。减少直接读写文件的次数，更快；`BufferedReader` 还能 `readLine()` 按行读；
- **转换流**：`InputStreamReader`、`OutputStreamWriter`。把字节流转换成字符流，并可以指定字符集；
- **对象流**：`ObjectInputStream`、`ObjectOutputStream`。读写 Java 对象，用于序列化；
- **数据流**：`DataInputStream`、`DataOutputStream`。按基本类型读写数据。

### 怎么使用
创建时，把一个已有的流作为参数传进去：

`new BufferedReader(new FileReader("a.txt"))`

里层 `FileReader` 是节点流，外层 `BufferedReader` 是处理流。数据读取时先经过外层，由它去向里层要数据。可以包装多层，每层增加一种功能。

### 关闭的规则
关闭最外层的处理流，会自动关闭它包装的内层流，所以只需关闭最外层。使用 try-with-resources 声明资源，更不容易漏。

### 这个设计的好处
功能可以像搭积木一样自由组合：同样的节点流，可以按需包上缓冲、转换、对象读写，而不用为每种组合写一个新类。

## 示例
```java
try (var reader = new java.io.BufferedReader(          // 处理流：加缓冲，可按行读
        new java.io.FileReader("a.txt"))) {            // 节点流：直接连文件
    System.out.println(reader.readLine());
}
```

## 易错点
- 只创建了处理流，却不给它传底层流；处理流自己不能直接读写文件
- 同时关闭内外两层，其实只关最外层就可以
- 缓冲输出流写完后没有 flush 或 close，数据可能还留在缓冲里没有写出
- 以为包上缓冲流内容就一定变了；缓冲只改变读写的方式，不改变数据

## 追问
### [f1] 为什么要加缓冲流？
没有缓冲时，每次读写都直接和文件或网络打交道，次数一多就很慢。缓冲流先把数据攒在内存里，凑够一批再读写，减少了直接交互的次数。
