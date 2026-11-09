---
id: q_01M6XCEAZMT01VYX1Q6VSNN4JT
title: 快速恢复阶段 cwnd 是怎样变化的？
type: concept
difficulty: medium
importance: 1
category: network
tags: [congestion-control, reliable-transmission]
prerequisites: [q_01M6XCE9ASCYVZ8STJKX6PY98Q, q_01M6XCE9KQ01D93G5JDKPKN4EB, q_01M6XCEAPVG8TT2223AYV2GZVW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
快速恢复在 3 个重复 ACK 后开始：cwnd 设为 ssthresh 加 3，之后每收到一个重复 ACK 加 1，收到新数据的 ACK 就回到 ssthresh，转入拥塞避免。

## 要点
- [kp1|3] 进入快速恢复时，cwnd 设为 ssthresh 加 3 个 MSS
- [kp2|3] 之后每收到一个重复 ACK，cwnd 再加 1 个 MSS
- [kp3|2] 收到新数据的 ACK 后，cwnd 回到 ssthresh，进入拥塞避免
- [kp4] 快速恢复不回到慢启动，因为重复 ACK 说明网络仍能送包

## 详解
### 先搞懂：路没堵死，只是少了一辆车
你开车队去旅行，有一辆车掉队了，其他车还在正常往前走。你不用让整个车队停下重新出发，只要回头接一下掉队的车，同时保持稍低的速度前进就行。

快速恢复就是这个思路：丢了一个包，但后面的包还能到，网络没有堵死，所以只降速、不重头来。

后文用到的术语：

- **重复 ACK**：确认号相同的多个 ACK，表示某段数据没到。
- **快速重传**：收到 3 个重复 ACK 后，立刻重发丢失的报文段。
- **ssthresh**：慢启动阈值，进入快速恢复前已更新。
- **cwnd**：拥塞窗口。

### 进入快速恢复之前
收到 3 个重复 ACK 后，发送方先做快速重传的处理：cwnd 减半，ssthresh 设为减半后的值。然后进入快速恢复。

### 快速恢复里 cwnd 怎么变
1. 进入时：cwnd = ssthresh + 3。加 3 是因为已经收到了 3 个重复 ACK，每个都说明有一个报文段离开了网络。
2. 重传丢失的那个报文段。
3. 之后每再收到一个重复 ACK，cwnd 加 1，因为又有一个报文段离开了网络，可以再发一个。
4. 收到新数据的 ACK，说明丢失的数据补上了，cwnd 回到 ssthresh，进入拥塞避免。

### 举例
| 事件 | ssthresh | cwnd |
|---|---|---|
| 进入前，cwnd 减半 | 10 | 10 |
| 进入快速恢复 | 10 | 13 |
| 再收到 2 个重复 ACK | 10 | 15 |
| 收到新数据的 ACK | 10 | 10 |

表里的数字只是示意，单位是 MSS。

### 为什么这样设计
重复 ACK 说明后面的数据到达了接收方，网络还是通的。如果这时像超时那样退回到很小的窗口，就太浪费了。

快速恢复让发送方保持较高的发送量，既补发了丢包，又没有让传输速度跌到谷底。

### 进阶：不同实现有差异（基础薄弱可先跳过）
上面是经典的 Reno 做法。后来的 NewReno 等改进，在一次丢多个包时恢复得更好，细节也有所不同。

## 易错点
- 以为快速恢复回到慢启动；实际 cwnd 从 ssthresh 附近继续
- 以为加 3 是随便取的；它对应已收到的 3 个重复 ACK
- 以为快速恢复结束后 cwnd 仍是 ssthresh 加 3；收到新 ACK 后回到 ssthresh

## 追问
### [f1] 快速恢复和慢启动重启，哪个更激进？
慢启动重启更保守：cwnd 降到很小，再指数增长。快速恢复只是减半，适用于网络仍通畅的轻度丢包。
