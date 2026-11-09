---
id: q_01M6XBG1MD93DNBDVEYTH9JTNY
title: Java IO 中的输入流和输出流是什么？
type: concept
difficulty: easy
importance: 1
category: java
tags: [io-stream]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Java IO 的流以程序为参照：把数据从外部读进程序的是输入流，把数据从程序写出到外部的是输出流。

## 要点
- [kp1|3] 输入流把数据读入程序，输出流把数据写出程序
- [kp2|3] 方向以程序自己为参照，不是以文件或网络为参照
- [kp3|2] 字节输入输出流的顶层是 InputStream 和 OutputStream
- [kp4|2] 字符输入输出流的顶层是 Reader 和 Writer
- [kp5] 流用完要关闭，推荐 try-with-resources

## 详解
### 先搞懂：数据像水一样“流”
做项目时，上传文件是把用户电脑里的文件读进服务器，导出报表是把服务器里的数据写成一个文件。这些都是数据在程序和外部（文件、网络、键盘、内存等）之间搬运。Java 把这种搬运抽象成“流”：数据像水一样，从一头流到另一头。

关键在“方向”。打个比方：程序是一个水池。

- 水从外面流进水池：输入流；
- 水从水池流出到外面：输出流。

后文用到的词：

- **数据源**：数据的来源，如文件、网络连接。
- **目的地**：数据的去处，如另一个文件、网络连接。

### 输入流：读
输入流用来读取数据，数据源在外面，程序是接收方。典型：读文件、读用户上传的内容、读网络请求体。

- 字节输入流：`InputStream`，如 `FileInputStream`；
- 字符输入流：`Reader`，如 `FileReader`。

### 输出流：写
输出流用来写出数据，目的地在外面，程序是发送方。典型：写文件、给浏览器返回响应内容。

- 字节输出流：`OutputStream`，如 `FileOutputStream`；
- 字符输出流：`Writer`，如 `FileWriter`。

### 方向怎么判断
记一个原则：站在程序的角度。看“数据是流进程序，还是流出程序”。比如把 A 文件复制到 B 文件，对程序来说，读 A 用输入流，写 B 用输出流。

### 方向以外的分类
流还可以按处理的数据单位分成字节流和字符流，按功能分成节点流和处理流，这些在其他题里单独讲。

## 示例
```java
try (var in = new java.io.FileInputStream("a.txt");       // 输入流：读入程序
     var out = new java.io.FileOutputStream("b.txt")) {   // 输出流：写出程序
    int b;
    while ((b = in.read()) != -1) {
        out.write(b);
    }
}
```

## 易错点
- 把方向看反，站在文件的角度判断；应该站在程序的角度
- 用完不关闭流，造成文件被占用或资源泄漏
- 以为一个流既能读又能写；普通的流方向是固定的，RandomAccessFile 是特例
- 把输入输出流和字节字符流混为一谈；一个是方向，一个是数据单位

## 追问
### [f1] 复制文件时，输入流和输出流分别是哪个？
读源文件用输入流（如 FileInputStream），写目标文件用输出流（如 FileOutputStream），中间在程序里一边读一边写。
