---
id: q_01M6XCEA5DGV5CXHMYA82VCVA2
title: TCP 慢启动是怎样让拥塞窗口增长的？
type: concept
difficulty: medium
importance: 2
category: network
tags: [congestion-control]
prerequisites: [q_01M6XCE9ASCYVZ8STJKX6PY98Q, q_01M6XCE9KQ01D93G5JDKPKN4EB, q_01M6XCE9WEYQAR2SGYTGZNK7QK]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
慢启动是连接刚建立时，cwnd 从较小值开始，每收到一个 ACK 就加 1 个 MSS，每过一个 RTT 窗口翻倍，增长到 ssthresh 为止。

## 要点
- [kp1|3] 连接刚建立时 cwnd 很小，先试探网络再加速
- [kp2|3] 每收到一个 ACK，cwnd 增加 1 个 MSS
- [kp3|2] 每过一个 RTT，cwnd 大约翻倍，是指数增长
- [kp4|2] cwnd 到达慢启动阈值 ssthresh 后，改为线性增长

## 详解
### 先搞懂：新开的水管先小水试压
装好新水管，不会一上来就开最大水，而是先放小水，没漏再逐步开大。

TCP 刚建立连接时，也不知道网络能承受多少，所以先发很少的数据试探，没问题再快速加量。

后文用到的术语：

- **cwnd**：拥塞窗口，发送方当前允许发出的量。
- **MSS**：一个报文段最多带的数据量。
- **RTT**：一个数据包发出去再收到确认的往返时间。
- **ssthresh**：慢启动阈值，决定什么时候从慢启动切换到拥塞避免。

### 慢启动怎么增长
1. 连接建立后，cwnd 从一个较小的值开始，比如 1 个 MSS。
2. 每收到一个 ACK，cwnd 加 1 个 MSS。
3. 一个 RTT 里，发出去多少个报文段，就会收到多少个 ACK。

### 为什么每个 RTT 翻倍
举例：cwnd 为 1，发 1 个报文段，收到 1 个 ACK，cwnd 变 2。下一轮发 2 个，收到 2 个 ACK，cwnd 变 4。再下一轮变 8。

| 轮次 | 发出报文段 | 收到 ACK | 轮末 cwnd |
|---|---|---|---|
| 第 1 轮 | 1 | 1 | 2 |
| 第 2 轮 | 2 | 2 | 4 |
| 第 3 轮 | 4 | 4 | 8 |

可见每轮翻倍，是指数增长。名字叫「慢」启动，是因为起点小，不是因为增长慢。

### 什么时候停止
慢启动不能无限翻倍，不然很快会把网络撑堵。所以设了一个阈值 ssthresh：

- cwnd 小于 ssthresh：继续慢启动，指数增长；
- cwnd 到达 ssthresh：改为拥塞避免，线性增长；
- 中途出现丢包：认为网络拥塞，减小窗口，调整 ssthresh。

### 进阶：初始窗口（基础薄弱可先跳过）
初始 cwnd 的大小随标准和系统实现而不同，现代系统一般不再从 1 个 MSS 开始。这不影响慢启动指数增长的基本逻辑。

## 易错点
- 以为慢启动增长得慢；它其实是指数增长，「慢」指起点小
- 以为 cwnd 每个 RTT 加 1；那是拥塞避免，慢启动是翻倍
- 以为慢启动会一直持续；到达 ssthresh 就结束

## 追问
### [f1] 慢启动和拥塞避免的区别是什么？
慢启动每个 RTT 翻倍，指数增长，速度快。拥塞避免每个 RTT 只加约 1 个 MSS，线性增长，更谨慎。二者以 ssthresh 为分界。
