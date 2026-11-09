---
id: q_01M6XCEADZVJ8DFQ9WC4B9VY3S
title: 拥塞避免阶段 cwnd 为什么线性增长？
type: concept
difficulty: medium
importance: 2
category: network
tags: [congestion-control]
prerequisites: [q_01M6XCE9ASCYVZ8STJKX6PY98Q, q_01M6XCE9KQ01D93G5JDKPKN4EB]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
cwnd 到达 ssthresh 后，每个 RTT 只增加约 1 个 MSS，是线性增长，这样小步试探网络，避免一下子增加太多又引起拥塞。

## 要点
- [kp1|3] cwnd 达到 ssthresh 后，从慢启动转入拥塞避免
- [kp2|3] 拥塞避免中每个 RTT，cwnd 增加约 1 个 MSS
- [kp3|2] 每收到一个 ACK，cwnd 只增加 1/cwnd 个 MSS
- [kp4] 线性增长是为了小步试探，避免一下子冲到拥塞点

## 详解
### 先搞懂：快到极限时改成小步走
你往一个水桶里倒水，不知道桶多大。前面一直是一杯一杯加倍倒，倒到怀疑快满了，就改成每次只加一小勺。这样即使满了，溢出的也很少。

拥塞避免就是这个思路：已经接近网络可能的极限，就放慢加速。

后文用到的术语：

- **cwnd**：拥塞窗口，发送方允许发出的量。
- **ssthresh**：慢启动阈值，是慢启动和拥塞避免的分界。
- **RTT**：数据包一次往返的时间。

### 怎么增长
进入拥塞避免后，每收到一个 ACK，cwnd 只增加 1/cwnd 个 MSS。一个 RTT 内大约会收到 cwnd 个 ACK，累加起来，cwnd 在这一个 RTT 里增加约 1 个 MSS。

### 举例
| 轮次 | cwnd（MSS） |
|---|---|
| 阈值处 | 8 |
| 第 1 个 RTT 后 | 9 |
| 第 2 个 RTT 后 | 10 |
| 第 3 个 RTT 后 | 11 |

每轮只加 1，是线性增长。表里的数字只是示意。

### 为什么要线性增长
cwnd 达到 ssthresh，说明接近之前出现过拥塞的位置。如果这里还继续翻倍，下一轮就会发出远超网络承受的数据，很容易丢包。

线性增长的好处是慢慢逼近网络容量，一旦发现丢包，已经发出去的多余数据也不多。

### 两个阶段对比
| 阶段 | 增长方式 | 每个 RTT 的变化 | 适用时机 |
|---|---|---|---|
| 慢启动 | 指数 | 翻倍 | cwnd 小于 ssthresh |
| 拥塞避免 | 线性 | 加约 1 个 MSS | cwnd 到达 ssthresh 之后 |

结论：先指数快速探测，再线性小心试探，兼顾速度和稳定。

### 进阶：ssthresh 的初值（基础薄弱可先跳过）
ssthresh 的初始值各实现不同，有的会设得很大，让慢启动一直持续到第一次丢包。出现拥塞后，ssthresh 会按丢包情况重新调整。

## 易错点
- 以为拥塞避免是 cwnd 不再增长；它仍在增长，只是变成线性
- 以为每个 ACK 加 1 个 MSS；那是慢启动，拥塞避免是 1/cwnd 个
- 以为 ssthresh 是固定值；出现拥塞后会重新设置

## 追问
### [f1] 拥塞避免阶段出现丢包会怎样？
会调整 ssthresh 和 cwnd。超时丢包时通常把 cwnd 重置为很小，重新慢启动；收到多个重复 ACK 时，则走快速重传和快速恢复，窗口下降得没那么多。
