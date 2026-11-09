---
id: q_01M6XBG2TF3PCTTV6QN12CTWG1
title: BIO、NIO、AIO 有什么区别？
type: concept
difficulty: medium
importance: 3
category: java
tags: [io-multiplexing, io-stream]
prerequisites: [q_01M6XCFWPGHQWTXE0J8FY9ZRNP]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java SE 21 API：java.nio.channels 包说明（Selector 多路复用、异步通道）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/package-summary.html" }
  - { title: "Java SE 21 API：java.nio.channels.AsynchronousChannelGroup（Since 1.7）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/AsynchronousChannelGroup.html" }
---

## 一句话
BIO 是阻塞式，一个连接占一个线程；NIO 是非阻塞加多路复用，一个线程能管很多连接；AIO 是异步，由系统完成读写后再通知程序。

## 要点
- [kp1|3] BIO 的读写会阻塞线程，通常一个连接要一个线程
- [kp2|3] NIO 用 Selector 在一个线程里监控多个 Channel 的事件，线程不必干等
- [kp3|2] AIO 由操作系统完成读写，完成后通过回调通知程序
- [kp4|2] BIO 适合连接少、逻辑简单的场景，NIO 适合连接多的场景
- [kp5] NIO 的核心组件是 Channel、Buffer、Selector

## 详解
### 先搞懂：餐厅怎么服务客人
做服务器时，每来一个客人（客户端连接），就要有人服务。三种 IO 模型相当于三种服务方式：

- BIO：每桌客人配一个专属服务员，服务员站在桌边等客人点菜。客人没开口，服务员就干等着，什么也不做；
- NIO：一个服务员负责很多桌，不站着等，而是不停巡视，哪桌举手就去哪桌；
- AIO：客人点完单后，服务员就去忙别的，厨房做好之后主动来通知。

后文用到的词：

- **阻塞**：线程发起读写后一直等着，没完成就不能做别的事。
- **非阻塞**：发起读写后立即返回，数据没准备好就先去干别的。
- **多路复用**：用一个线程同时监控很多连接，哪个就绪处理哪个。
- **异步**：读写由系统在后台完成，完成后再通知程序。

### BIO：阻塞，一连接一线程
线程执行读写时被阻塞，没有数据就一直等。为了同时服务多个客人，只能一个连接开一个线程。连接少时没问题，连接一多，线程数暴涨，开销很大。

### NIO：非阻塞加多路复用
NIO 的三个核心组件：

- `Channel`：通道，双向，数据读写的通路；
- `Buffer`：缓冲区，数据先读进或写入缓冲区；
- `Selector`：选择器，一个线程用它监控多个通道上的事件（可读、可写、有新连接），有事件才处理。

所以线程不必为每个连接守着，少量线程就能管理很多连接。适合连接数多的场景，如聊天服务器、网关。

### AIO：异步，完成后通知
程序发起读写后立刻返回，由操作系统完成实际 IO，完成后通过回调或 Future 通知程序。线程既不阻塞，也不用自己轮询。AIO 在 Java 7 引入，但实际使用比 NIO 少，主流网络框架如 Netty 基于 NIO。

### 方案对比：三种 IO 模型
| 模型 | 读写方式 | 线程使用 | 适合场景 | 编程复杂度 |
|---|---|---|---|---|
| BIO | 同步阻塞 | 一个连接一个线程 | 连接少、逻辑简单 | 低 |
| NIO | 同步非阻塞加多路复用 | 少量线程管理多个连接 | 连接多 | 较高 |
| AIO | 异步 | 系统完成读写后回调 | 连接多、操作耗时的场景 | 较高 |

结论：连接少且简单用 BIO；连接多的网络服务默认选 NIO，直接用或用 Netty 等框架封装；AIO 用得相对少，不是首选。

## 示例
```java
// NIO：一个线程用 Selector 监控多个连接
Selector selector = Selector.open();
ServerSocketChannel server = ServerSocketChannel.open();
server.bind(new InetSocketAddress(8080));
server.configureBlocking(false);              // 非阻塞
server.register(selector, SelectionKey.OP_ACCEPT);
while (true) {
    selector.select();                         // 等待有事件的通道
    // 遍历 selector.selectedKeys() 处理各个事件
}
```

## 易错点
- 把“非阻塞”和“异步”当成一回事；NIO 仍需自己去读写，AIO 才是系统做完再通知
- 以为 NIO 一定比 BIO 快；连接少时优势不明显
- 以为 NIO 完全没有阻塞；Selector 的 select 本身会等待事件
- 以为 Netty 是 AIO；它主要基于 NIO

## 追问
### [f1] 同步和异步、阻塞和非阻塞有什么区别？
阻塞和非阻塞说的是线程发起调用后是否被卡住。同步和异步说的是结果由谁取：同步需要自己等或自己去取，异步是由系统完成后通知你。

### [f2] NIO 里的 Selector 起什么作用？
它让一个线程同时监控多个通道的事件，有事件才处理，避免为每个连接单独开线程。
