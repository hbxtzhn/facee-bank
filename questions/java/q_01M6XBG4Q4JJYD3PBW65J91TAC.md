---
id: q_01M6XBG4Q4JJYD3PBW65J91TAC
title: 什么是 Socket？
type: concept
difficulty: easy
importance: 1
category: java
tags: [socket, tcp-connection]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Socket 是网络通信中一端的连接端点，程序通过它建立 TCP 或 UDP 连接，在两台机器的进程之间收发数据。

## 要点
- [kp1|3] Socket 是两个进程通过网络通信时，各自持有的一端
- [kp2|3] 一个 TCP 连接由两端的 IP 和端口共同确定
- [kp3|2] Java 里服务端用 ServerSocket 监听，客户端用 Socket 连接
- [kp4|2] 操作系统里 Socket 对应一个文件描述符，读写像读写文件
- [kp5] Socket 本身不规定数据格式，格式由上层协议决定

## 详解
### 先搞懂：电话机的插口
两个人打电话，各自手里有一部电话机。电话机就是通话的“端点”：你对着它说话，对方的电话机收到。

Socket 就是网络通信里的这部电话机。你的程序往 Socket 里写数据，网络把它送到对方程序的 Socket，对方读出来。

后文术语：
- **IP 地址 + 端口**：IP 找到哪台机器，端口找到机器上哪个程序。
- **TCP / UDP**：两种传输方式，TCP 先建立连接、可靠有序；UDP 不建立连接。
- **文件描述符**：操作系统给每个打开的文件或连接编的一个整数号。

### 怎么建立连接（以 TCP 为例）
1. 服务端创建 ServerSocket，绑定端口，调用 `accept()` 等待；
2. 客户端创建 Socket，指定服务端的 IP 和端口，发起连接；
3. 连接建立后，服务端 accept 返回一个新的 Socket，代表和这个客户端的通道；
4. 双方通过 Socket 的输入流、输出流读写数据。

### 和文件描述符的关系
在 Linux 上，一个 Socket 就是一个文件描述符，读写它和读写文件的方式类似。所以一台服务器能同时开多少个连接，会受到进程能打开的文件描述符数量限制。

### 它能做什么
HTTP 请求、数据库连接、RPC 调用，底层都是基于 Socket 在传输。Socket 只负责传字节，传的是什么格式（HTTP、JSON 还是别的）由上层协议决定。

## 示例
```java
// 服务端
try (ServerSocket server = new ServerSocket(8080);
     Socket client = server.accept()) {
    InputStream in = client.getInputStream();
}

// 客户端
try (Socket socket = new Socket("127.0.0.1", 8080)) {
    socket.getOutputStream().write("hello".getBytes());
}
```

## 易错点
- 以为 Socket 就是 TCP；Socket 也可以用于 UDP
- 以为一个 Socket 只能用一次；连接未关闭时可以反复读写
- 忘记关闭 Socket；会泄漏文件描述符，最终无法接受新连接

## 追问
### [f1] ServerSocket 和 Socket 有什么区别？
ServerSocket 在服务端负责监听端口、接受新连接；Socket 代表一条已经建立的连接，双方用它读写数据。
