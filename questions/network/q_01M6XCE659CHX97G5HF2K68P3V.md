---
id: q_01M6XCE659CHX97G5HF2K68P3V
title: TCP 四次挥手的过程是怎样的？
type: concept
difficulty: medium
importance: 3
category: network
tags: [tcp-connection]
prerequisites: [q_01M6XCE557WMCEME04QM8VW38Y, q_01M6XCE5XAYN4X05YHT65N6HB2]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
主动方发 FIN，被动方回 ACK，被动方数据发完后再发 FIN，主动方回 ACK 并经 TIME_WAIT 等待后才真正关闭。

## 要点
- [kp1|3] 第一次：主动方发 FIN，进入 FIN_WAIT_1
- [kp2|3] 第二次：被动方回 ACK，进入 CLOSE_WAIT；主动方进入 FIN_WAIT_2
- [kp3|2] 第三次：被动方数据发完，发 FIN，进入 LAST_ACK
- [kp4|2] 第四次：主动方回 ACK，进入 TIME_WAIT，等待 2MSL 后关闭

## 详解
### 先搞懂：双方各说一次再见
两个人通话结束时：

1. 你说：「我说完了。」
2. 对方说：「好，知道了。」（但他可能还有话要说）
3. 对方说完后：「我也说完了。」
4. 你说：「好，再见。」

这就是四次挥手：每个方向各自告别一次。

后文的术语：

- **主动方**：先发起关闭的一方，可以是客户端，也可以是服务端。
- **被动方**：收到关闭请求的一方。
- **MSL**：报文在网络中最长的存活时间。
- **TIME_WAIT**：主动方最后一步之后的等待状态。

### 第一次挥手：主动方发 FIN
主动方发出 FIN 报文，表示自己不再发送数据，之后进入 FIN_WAIT_1 状态。

### 第二次挥手：被动方回 ACK
被动方收到 FIN，先回一个 ACK，告诉对方「我收到了」，然后进入 CLOSE_WAIT 状态。主动方收到这个 ACK，进入 FIN_WAIT_2 状态。

此时连接处于半关闭：主动方不再发送，但被动方还可以继续把没发完的数据发给主动方。

### 第三次挥手：被动方发 FIN
被动方的数据发送完毕，发出自己的 FIN，然后进入 LAST_ACK 状态，等待最后的确认。

### 第四次挥手：主动方回 ACK
主动方收到 FIN，回一个 ACK，进入 TIME_WAIT 状态。被动方收到这个 ACK 后，直接关闭。

### TIME_WAIT：为什么主动方还要等
主动方不会立刻关闭，会等待 2MSL（两倍的报文最大存活时间）后才进入关闭状态。原因有两个：

- 最后的 ACK 可能丢失。被动方收不到就会重传 FIN，主动方还在等待，就可以再次回 ACK。
- 让这条连接留在网络里的旧报文都消失，避免它们干扰之后复用同样四元组的新连接。

### 状态变化一览
| 步骤 | 主动方 | 被动方 |
|---|---|---|
| 发 FIN | FIN_WAIT_1 | |
| 回 ACK | FIN_WAIT_2 | CLOSE_WAIT |
| 发 FIN | | LAST_ACK |
| 回 ACK | TIME_WAIT，等 2MSL 后关闭 | 关闭 |

## 易错点
- 以为只有客户端能主动关闭；服务端也可以先发 FIN
- 以为主动方发完最后的 ACK 就立刻关闭；它要先经过 TIME_WAIT
- 以为第二次和第三次挥手一定能合并；被动方还有数据时，必须先回 ACK，后发 FIN

## 追问
### [f1] 服务器上出现大量 CLOSE_WAIT 说明什么？
说明对方已经发了 FIN，但本方程序没有调用关闭。通常是代码里没有正确关闭连接，比如漏掉 close，需要排查程序。
