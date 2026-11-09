---
id: q_01M6XCE7EH3N9S3MMN9B99AQ2P
title: TCP 连接的状态是怎样变化的（状态机）？
type: concept
difficulty: medium
importance: 2
category: network
tags: [tcp-connection]
prerequisites: [q_01M6XCE557WMCEME04QM8VW38Y, q_01M6XCE5D8116WBX8EXNZZGK6Z, q_01M6XCE659CHX97G5HF2K68P3V]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
TCP 连接用一个状态机描述：服务端从 CLOSED 到 LISTEN，握手后双方进入 ESTABLISHED，挥手时依次经过 FIN_WAIT、CLOSE_WAIT、LAST_ACK、TIME_WAIT 回到 CLOSED。

## 要点
- [kp1|3] 握手阶段：客户端 SYN_SENT，服务端 LISTEN 到 SYN_RCVD，最后双方 ESTABLISHED
- [kp2|3] 主动关闭方经过 FIN_WAIT_1、FIN_WAIT_2、TIME_WAIT，最后到 CLOSED
- [kp3|2] 被动关闭方经过 CLOSE_WAIT、LAST_ACK，收到最后的 ACK 后到 CLOSED
- [kp4] CLOSE_WAIT 堆积通常说明应用没有调用 close

## 详解
### 先搞懂：状态就是「现在聊到哪一步了」
打电话有几个阶段：拨号中、对方响铃、通话中、一方说要挂了、等对方也说再见、挂断。TCP 连接也有这样的阶段，每个阶段就是一个**状态**。收到什么报文，或应用做了什么操作，状态就切换到下一个。

后文用到的术语：

- **SYN**：请求建立连接的报文。
- **FIN**：请求关闭连接的报文。
- **主动关闭方**：先发 FIN 的一方。
- **被动关闭方**：收到对方 FIN 的一方。

### 建立连接：三次握手对应的状态
1. 服务端先调用监听，进入 **LISTEN**，等人来连。
2. 客户端发 SYN，进入 **SYN_SENT**。
3. 服务端收到 SYN，回 SYN 加 ACK，进入 **SYN_RCVD**。
4. 客户端收到后回 ACK，进入 **ESTABLISHED**，服务端收到这个 ACK 后也进入 ESTABLISHED。

此后双方就可以收发数据了。

### 关闭连接：四次挥手对应的状态
先发 FIN 的是主动关闭方：

1. 主动方发 FIN，进入 **FIN_WAIT_1**。
2. 被动方收到 FIN，回 ACK，进入 **CLOSE_WAIT**。主动方收到 ACK，进入 **FIN_WAIT_2**。
3. 被动方应用处理完后调用关闭，发 FIN，进入 **LAST_ACK**。
4. 主动方收到 FIN，回 ACK，进入 **TIME_WAIT**，等待一段时间后到 **CLOSED**。被动方收到 ACK 后直接到 CLOSED。

### 状态速查
| 状态 | 谁会处于 | 含义 |
|---|---|---|
| LISTEN | 服务端 | 等待连接请求 |
| SYN_SENT | 客户端 | 已发 SYN，等回应 |
| SYN_RCVD | 服务端 | 收到 SYN，已回应，等最后的 ACK |
| ESTABLISHED | 双方 | 连接已建立，可传数据 |
| FIN_WAIT_1 / 2 | 主动关闭方 | 已发 FIN，等确认或等对方的 FIN |
| CLOSE_WAIT | 被动关闭方 | 已收到 FIN，等应用关闭 |
| LAST_ACK | 被动关闭方 | 已发 FIN，等最后的 ACK |
| TIME_WAIT | 主动关闭方 | 等待一段时间再彻底关闭 |

### 排查时最常看的两个状态
- **大量 TIME_WAIT**：说明本机在大量主动关闭连接，多见于短连接场景。
- **大量 CLOSE_WAIT**：说明对方已经关了，本机应用却没有调用 close，通常是代码里没释放连接。

### 进阶：同时关闭等少见路径（基础薄弱可先跳过）
双方同时发 FIN 时，会经过 CLOSING 状态。收到带 ACK 的 FIN 时，可以从 FIN_WAIT_1 直接到 TIME_WAIT。这些是状态机里的少见分支。

## 易错点
- 以为 CLOSE_WAIT 是网络问题；实际是本机应用没有及时关闭连接
- 以为两端都会进入 TIME_WAIT；正常挥手只有主动关闭方会进入
- 以为握手完成客户端和服务端同时进入 ESTABLISHED；客户端先于服务端

## 追问
### [f1] 为什么会有 CLOSE_WAIT 这个中间状态？
因为 TCP 是双向的，对方说「我发完了」，不代表我也发完了。本机先回 ACK，等应用把剩下的数据处理完，再发自己的 FIN。

### [f2] 服务端收到 SYN 后，为什么进入 SYN_RCVD 而不是 ESTABLISHED？
因为它还没收到客户端的 ACK，不知道自己的 SYN 加 ACK 有没有送达。收到最后一个 ACK 后才进入 ESTABLISHED。
