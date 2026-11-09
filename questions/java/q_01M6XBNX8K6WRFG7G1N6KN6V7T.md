---
id: q_01M6XBNX8K6WRFG7G1N6KN6V7T
title: NIO 的 Selector 是怎么监控多个连接的？
type: concept
difficulty: medium
importance: 2
category: java
tags: [io-multiplexing, socket]
prerequisites: [q_01M6XCFWPGHQWTXE0J8FY9ZRNP]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java SE 21 API：java.nio.channels.Selector", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/Selector.html" }
  - { title: "Java SE 21 API：java.nio.channels.SelectableChannel（register 与非阻塞模式）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/SelectableChannel.html" }
  - { title: "OpenJDK 源码：sun/nio/ch/DefaultSelectorProvider.java（Linux 默认 EPollSelectorProvider）", url: "https://github.com/openjdk/jdk/blob/master/src/java.base/linux/classes/sun/nio/ch/DefaultSelectorProvider.java" }
---

## 一句话
Selector 让一个线程把很多连接都登记到自己名下，由操作系统告诉它哪些连接有数据可处理，线程只处理这些就绪的连接，不用给每个连接配一个线程。

## 要点
- [kp1|3] 多个 Channel 通过 register 注册到同一个 Selector，并声明关心的事件
- [kp2|3] select() 返回就绪通道数，selectedKeys() 取出就绪的那批 key 逐个处理
- [kp3|2] Channel 必须设为非阻塞模式才能注册到 Selector
- [kp4|2] Linux 下 Selector 底层通常基于 epoll，由内核登记并通知就绪连接
- [kp5] 处理完 selectedKeys 里的 key 后要手动移除，否则下次还会再看到

## 详解
### 先搞懂：一个前台接待几百位访客
传统 BIO 做法像是每来一位访客就派一个专员全程陪着，访客不说话，专员就干等。连接一多，专员（线程）就不够用了。

NIO 的做法是只设一个前台：每位访客到了先登记，并留话说“我有事会举手”。前台不用挨个去问，只要等有人举手，再去接待举手的人。这个前台就是 Selector，访客就是 Channel。

后文用到的术语：
- **Channel**：通道，代表一条网络连接（如 SocketChannel）。
- **Selector**：选择器，负责盯着一批 Channel，看哪些就绪。
- **SelectionKey**：登记凭证，记录“哪个通道、关心什么事件”。
- **就绪**：这个事件现在可以做而且不会卡住，比如连接上有数据可读。

### 注册：先说清楚关心什么事件
流程分三步：

1. 创建 Selector，再把 Channel 设为非阻塞（`configureBlocking(false)`），否则注册时会抛异常；
2. 调用 `channel.register(selector, 事件)` 登记。常见事件有四种：OP_ACCEPT（有新连接）、OP_CONNECT（连接完成）、OP_READ（可读）、OP_WRITE（可写）；
3. 登记后拿到一个 SelectionKey，代表这次登记。

### 轮询：select 之后只处理就绪的
线程进入一个循环：

1. 调用 `selector.select()`，没有任何就绪事件时线程会在这里等待；
2. 返回后，从 `selector.selectedKeys()` 拿到就绪的 key 集合；
3. 逐个判断是哪种事件：新连接就 accept 并把新通道也注册进来；可读就读数据；
4. 处理完把这个 key 从集合里移除。

所以线程不会把时间浪费在没数据的连接上，一个线程能照看很多连接。

### 为什么这样能省线程
BIO 里线程阻塞在某一条连接的读上，别的连接来了数据也没法管。NIO 里线程阻塞在 select 上，只要有任何一个连接就绪就会被唤醒。线程数不再跟连接数成正比，适合连接多、但每条连接大部分时间空闲的场景。

### 进阶：底层怎么知道谁就绪（基础薄弱可先跳过）
Selector 的实现依赖操作系统。Linux 上通常用 epoll。连接对应的文件描述符（操作系统用来标识一个打开的连接或文件的整数编号）会登记在内核里。内核发现有数据到达就记下，select 时直接取出就绪的那批，不需要每次把全部连接重新扫一遍。其他系统会用 kqueue、select 等机制，实现不同。实际项目里常用 Netty 封装这套流程，省去自己处理这些细节。

## 示例
```java
Selector selector = Selector.open();
ServerSocketChannel server = ServerSocketChannel.open();
server.bind(new InetSocketAddress(8080));
server.configureBlocking(false);
server.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // 没有就绪事件时在这里等待
    Iterator<SelectionKey> it = selector.selectedKeys().iterator();
    while (it.hasNext()) {
        SelectionKey key = it.next();
        it.remove(); // 处理完必须移除
        if (key.isAcceptable()) {
            SocketChannel ch = server.accept();
            ch.configureBlocking(false);
            ch.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            SocketChannel ch = (SocketChannel) key.channel();
            ByteBuffer buf = ByteBuffer.allocate(1024);
            if (ch.read(buf) < 0) ch.close();
        }
    }
}
```

## 易错点
- 以为 Selector 会自己清理 selectedKeys；实际要手动移除，否则同一个 key 会被重复处理
- 在处理就绪事件时做耗时操作；这会拖住整个循环，别的连接得不到处理
- 以为 NIO 一定比 BIO 快；连接很少时，BIO 写法更简单，差别不大

## 追问
### [f1] 为什么 Channel 必须是非阻塞模式才能注册？
阻塞模式下读写会让线程卡住等待，这和“线程只处理已就绪通道”的目标冲突，所以 JDK 规定阻塞模式的通道注册会抛 IllegalBlockingModeException。

### [f2] Selector 和 epoll 是什么关系？
Selector 是 Java 的统一接口，Linux 上它的底层实现通常是 epoll；换到别的系统，会用该系统自己的多路复用机制。
