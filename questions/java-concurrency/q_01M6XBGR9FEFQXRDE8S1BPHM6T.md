---
id: q_01M6XBGR9FEFQXRDE8S1BPHM6T
title: 什么是管道输入/输出流，用在什么场景？
type: concept
difficulty: easy
importance: 1
category: java-concurrency
tags: [thread-basics, io-stream]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
管道输入输出流是在同一个 JVM 里让两个线程通过内存传数据的流：一个线程往管道写，另一个线程从管道读，分字节（Piped*Stream）和字符（Piped*）两类。

## 要点
- [kp1|3] 管道流用内存做传输介质，用于线程之间传数据，不是文件或网络
- [kp2|3] 共四个类：PipedOutputStream、PipedInputStream、PipedWriter、PipedReader
- [kp3|2] 前两个面向字节，后两个面向字符
- [kp4|2] 输出端要和输入端 connect 连接起来，两端放在不同线程里使用
- [kp5] 现代项目更常用 BlockingQueue 传递数据

## 详解
### 先搞懂：像一根水管连起两个线程
文件流是把数据写到磁盘，网络流是发到别的机器。但有时候两个线程只是想在同一个程序里传数据，比如一个线程生成数据，另一个线程处理。

管道流就像一根水管：A 线程往水管里倒水（写），B 线程在另一头接水（读），中间的存储介质是内存。

后文用到的几个词：
- **字节流**：以字节为单位读写，适合任意二进制数据。
- **字符流**：以字符为单位读写，适合文本。

### 四个类怎么分
| 类 | 面向 | 角色 |
|---|---|---|
| PipedOutputStream | 字节 | 写入端 |
| PipedInputStream | 字节 | 读取端 |
| PipedWriter | 字符 | 写入端 |
| PipedReader | 字符 | 读取端 |

传二进制数据用字节那一对，传文本用字符那一对。

### 使用步骤
1. 创建写入端和读取端对象；
2. 调用 `connect` 把它们连接起来（也可以在构造时直接传入对方）；
3. 一个线程往写入端写数据，另一个线程从读取端读数据。

管道内部有缓冲区。读不到数据时，读取线程会阻塞等待；缓冲区满时，写入线程也会阻塞。

### 什么时候用
管道流适合少量的、简单的线程间数据传递。它只能在同一个 JVM 内使用，一对写入端和读取端只能点对点。需要多个生产者或多个消费者时，通常改用 `BlockingQueue`。

## 示例
```java
PipedWriter writer = new PipedWriter();
PipedReader reader = new PipedReader();
writer.connect(reader);

Thread producer = new Thread(() -> {
    try { writer.write("hello"); writer.close(); }
    catch (IOException e) { e.printStackTrace(); }
});
Thread consumer = new Thread(() -> {
    try {
        int ch;
        while ((ch = reader.read()) != -1) System.out.print((char) ch);
    } catch (IOException e) { e.printStackTrace(); }
});
producer.start();
consumer.start();
```

## 易错点
- 没有 connect 就使用；会抛 IOException，提示管道未连接
- 在同一个线程里既写又读；缓冲区满或读空时会把自己卡死
- 以为管道流可以跨进程或跨机器；它只在同一个 JVM 里有效

## 追问
### [f1] 管道流和 BlockingQueue 怎么选？
管道流传的是字节或字符流，适合已经按流方式处理数据的场景。传对象、需要多个生产者消费者时，用 BlockingQueue 更方便，也更常见。
