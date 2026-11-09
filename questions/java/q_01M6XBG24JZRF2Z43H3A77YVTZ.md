---
id: q_01M6XBG24JZRF2Z43H3A77YVTZ
title: 什么是字符流？
type: concept
difficulty: easy
importance: 2
category: java
tags: [io-stream]
prerequisites: [q_01M6XBG1MD93DNBDVEYTH9JTNY]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
字符流以字符为单位读写文本，内部帮你处理字节和字符之间的编码转换，适合文本文件，顶层类是 Reader 和 Writer。

## 要点
- [kp1|3] 字符流以字符为单位读写，用来处理文本
- [kp2|3] 它在字节和字符之间做编码转换
- [kp3|2] 顶层抽象类是 Reader 和 Writer
- [kp4|2] 常用 FileReader、FileWriter、BufferedReader、InputStreamReader
- [kp5] 指定字符集可以避免乱码，如 UTF-8

## 详解
### 先搞懂：文字不是单个字节
做项目时，读一个配置文件，或者把日志写到文本文件里，处理的都是“文字”。文字在文件里最终也是字节，但一个汉字常常对应多个字节，具体几个，取决于编码规则（UTF-8、GBK 等）。

打个比方：字节流是搬运工，只管搬箱子；字符流则像是一位翻译，一边搬一边按照规则把字节“翻译”成文字，或者把文字“翻译”回字节。

后文用到的词：

- **字符**：一个文字单位，比如一个汉字、一个字母。
- **编码**：字符和字节之间的转换规则。
- **字符集**：具体使用哪套规则，如 UTF-8。

### 顶层类
- `Reader`：字符输入流的抽象父类，核心方法是 `read()`，读到的是字符；
- `Writer`：字符输出流的抽象父类，核心方法是 `write()`，写入的是字符或字符串。

常见子类：`FileReader`、`FileWriter` 读写文本文件，`BufferedReader` 带缓冲且可以按行读取，`InputStreamReader` 把字节流转换成字符流。

### 编码是怎么处理的
字符流读取时，先从底层读字节，再按字符集解码成字符；写出时反过来。如果文件的编码和你指定或默认的编码对不上，就会乱码。所以对文本文件，建议显式指定字符集，不要依赖平台默认值，比如 `new InputStreamReader(in, StandardCharsets.UTF_8)`。

### 适合与不适合
- 适合：txt、csv、json、日志、配置文件等文本；
- 不适合：图片、音频、视频等二进制文件，用字符流读它们会被当成文字解码，内容会损坏。

### 按行读取
`BufferedReader.readLine()` 可以一次读一整行，处理日志和配置很方便，也比一次一个字符更高效。

## 示例
```java
try (var reader = new java.io.BufferedReader(new java.io.InputStreamReader(
        new java.io.FileInputStream("a.txt"), java.nio.charset.StandardCharsets.UTF_8))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

## 易错点
- 用字符流复制图片，文件被破坏，二进制数据要用字节流
- 不指定字符集，在不同机器上读同一个文件，结果乱码
- 以为字符流不需要关闭；它底层也占用着文件资源，同样要关闭
- 把 char 当成“一个汉字就一个字节”，字符和字节的数量并不对应

## 追问
### [f1] 字符流和字节流是什么关系？
字符流底层仍然靠字节流读写数据，只是多了编码转换这一层。InputStreamReader 就是把字节流转换成字符流的桥梁。
