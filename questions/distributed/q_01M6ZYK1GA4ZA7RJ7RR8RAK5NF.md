---
id: q_01M6ZYK1GA4ZA7RJ7RR8RAK5NF
title: Pulsar 的存算分离架构是什么？
type: concept
difficulty: medium
importance: 1
category: distributed
tags: [mq-selection]
prerequisites: [q_01M6ZYK0BW09AZ3GKG7W6GGM35]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Pulsar 把处理请求的 Broker 和存数据的 BookKeeper 分成两层，Broker 不存数据所以可以随意扩缩容，存储层单独扩展。

## 要点
- [kp1|3] Broker 是无状态的，只负责收发消息，不在本地保存消息数据
- [kp2|3] 消息持久化在 BookKeeper 集群里，存储节点叫 Bookie
- [kp3|2] 两层可以各自独立扩容，Broker 挂了，Topic 可迁到别的 Broker
- [kp4] 支持多租户和分层存储，旧数据可以转存到便宜的存储

## 详解
### 先搞懂：店员和仓库分开
想象一家快递网点：前台负责收件、分拣，仓库负责放包裹。如果前台自己带着包裹，前台一出事，包裹也跟着受影响。

Pulsar 的做法是把前台和仓库分开。前台人手不够，多招几个前台；仓库不够，只扩仓库。

后文用到的几个词：
- **Broker**：前台，处理生产者和消费者的请求。
- **BookKeeper**：仓库，专门存消息日志的分布式存储。
- **Bookie**：BookKeeper 里的一个存储节点。
- **存算分离**：计算（处理请求）和存储（保存数据）分开部署。

### Broker 无状态：挂了很快能换人
Broker 不在本地保存消息。所以某个 Broker 宕机后，它负责的 Topic 可以由别的 Broker 接手。数据本来就在 BookKeeper 里，不用搬。

对比一下，Kafka 的分区数据存在 Broker 本地磁盘上，扩容或换机器时要搬数据。

### BookKeeper：消息写到多个存储节点
消息写入时，会同时写到多个 Bookie，达到要求的份数才算成功。这样某个存储节点坏了，数据还在别处。

### 分层存储与多租户
- **分层存储**：近期热数据放在 BookKeeper，较老的数据可以转存到对象存储这类更便宜的地方。
- **多租户**：用租户、命名空间来隔离不同业务，方便权限和配额管理。
- Pulsar 还支持跨地域复制，适合多机房部署。

### 方案对比：和 Kafka 的架构区别
| 维度 | Pulsar | Kafka |
|---|---|---|
| 数据存在哪 | BookKeeper 存储层 | Broker 本地磁盘 |
| Broker 是否有状态 | 无状态 | 有状态 |
| 扩容方式 | 计算和存储分别扩 | Broker 一起扩，要搬数据 |
| 运维组件 | 组件更多 | 组件相对少 |

结论：需要多租户、海量 Topic、灵活扩缩容时可考虑 Pulsar。团队运维力量有限时，组件少的方案更容易管。

## 易错点
- 以为无状态就是不需要存储；数据只是放在 BookKeeper 层
- 以为存算分离一定更快；它的好处是弹性和隔离，组件多了运维更复杂
- 以为 Broker 完全没有内存缓存；它会缓存数据，只是不当作最终存储

## 追问
### [f1] 存算分离的代价是什么？
需要部署和运维更多组件，消息要经过 Broker 再到 BookKeeper，链路更长，排查问题也更复杂。
