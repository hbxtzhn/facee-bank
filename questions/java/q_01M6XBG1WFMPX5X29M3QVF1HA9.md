---
id: q_01M6XBG1WFMPX5X29M3QVF1HA9
title: 什么是字节流？
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
字节流以字节为单位读写数据，什么类型的数据都能处理，尤其适合图片、音频、视频等二进制数据，顶层类是 InputStream 和 OutputStream。

## 要点
- [kp1|3] 字节流一次处理一个字节，不关心内容含义
- [kp2|3] 顶层抽象类是 InputStream 和 OutputStream
- [kp3|2] 适合图片、音频、视频、压缩包等二进制数据
- [kp4|2] 常用实现类有 FileInputStream、FileOutputStream
- [kp5] 用字节流读文本，需要自己处理编码，容易乱码

## 详解
### 先搞懂：最原始的搬运方式
计算机里所有数据，最后都是一个个字节（byte）。做项目时，用户上传一张头像，服务器收到的是一串字节；下载文件，也是一串字节。字节流就是最原始的搬运方式：一个字节一个字节地往里读、往外写，不管这些字节代表图片还是文字。

打个比方：字节流像是搬运工，只管把一箱箱货搬走，不拆箱，不关心箱子里是什么。

后文用到的词：

- **字节**：计算机存储的基本单位，由 8 位二进制组成。
- **二进制数据**：不是文本的数据，如图片、音频、可执行文件。
- **编码**：字符和字节之间的转换规则，如 UTF-8。

### 顶层类
- `InputStream`：字节输入流的抽象父类，核心方法是 `read()`；
- `OutputStream`：字节输出流的抽象父类，核心方法是 `write()`。

常见子类：`FileInputStream`、`FileOutputStream` 读写文件，`ByteArrayInputStream` 读写内存里的字节数组。

### 适合什么场景
- 图片、音频、视频、压缩包、PDF 等二进制文件的复制和传输；
- 网络传输原始数据；
- 不确定内容是什么、只需要原样搬运的场景。

### 用来读文本会怎样
文本在文件里也是字节，但一个汉字在常用编码里可能占多个字节。字节流是一个字节一个字节地读，如果把一个汉字的字节拆开处理，就会得到乱码。所以处理文本更适合用字符流，由字符流负责字节和字符之间的转换。

### 读写时一次一个字节会很慢
一次读一个字节效率很低，实际使用时会配合一个字节数组一次读一批，或者用带缓冲的流包装一层。

## 示例
```java
try (var in = new java.io.FileInputStream("photo.jpg");
     var out = new java.io.FileOutputStream("copy.jpg")) {
    byte[] buf = new byte[4096];
    int n;
    while ((n = in.read(buf)) != -1) {
        out.write(buf, 0, n); // 只写入实际读到的 n 个字节
    }
}
```

## 易错点
- 用字节流逐个读取中文文本，再强转成 char 输出，得到乱码
- 读到数组后写出时，不管读了多少，整个数组全写，会多写垃圾数据
- 忘了关闭流
- 以为字节流只能处理二进制；它也能读文本，只是编码要自己处理

## 追问
### [f1] 字节流和字符流怎么选？
文本数据用字符流，更方便也不容易乱码。图片、音频等二进制数据只能用字节流。不确定时用字节流，它最通用。
