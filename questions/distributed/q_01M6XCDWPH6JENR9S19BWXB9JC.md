---
id: q_01M6XCDWPH6JENR9S19BWXB9JC
title: Kafka 的 KRaft 模式解决了什么问题？
type: concept
difficulty: medium
importance: 1
category: distributed
tags: [mq-selection, consensus]
appliesTo: ["Kafka >= 3.3"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
KRaft 让 Kafka 用自带的 Raft 协议管理元数据，不再依赖 ZooKeeper，部署运维更简单，元数据的扩展性也更好。

## 要点
- [kp1|3] KRaft 用 Kafka 内置的 Raft 管理集群元数据
- [kp2|3] 不再需要单独部署和维护 ZooKeeper 集群
- [kp3|2] 元数据存在 Kafka 自己的日志里，恢复和扩展更好
- [kp4|2] Kafka 4.0 起只支持 KRaft，不再支持 ZooKeeper
- [kp5] Raft 是一种共识算法，用多数派达成一致

## 详解
### 先搞懂：一个集群要有「总账本」
Kafka 集群里有很多台机器，必须有个地方记录：有哪些 Topic、每个分区的主副本在哪台机器、哪些机器还活着。这些信息叫**元数据**。

早期 Kafka 把这本「总账本」放在另一个独立系统 ZooKeeper 里。就像一家公司，业务在自己的办公楼，账本却放在隔壁另一家公司，两边都得维护。

KRaft 的做法是：账本也由 Kafka 自己保管，少了一个外部依赖。后文术语：
- **元数据**：描述集群自身状态的数据，如主题、分区、副本位置。
- **ZooKeeper**：一个独立的协调服务，早期 Kafka 用它存元数据。
- **Raft**：一种共识算法，多个节点通过多数派投票保持一致。
- **控制器**：集群里负责管理元数据和选主的节点。

### 旧方式有什么麻烦
- **运维复杂**：要额外部署、监控和升级一套 ZooKeeper 集群，出问题要两边排查；
- **元数据扩展受限**：控制器要从 ZooKeeper 加载大量元数据，分区数很大时，故障切换和启动都比较慢；
- **两套系统要保持一致**：元数据更新要同时在两处协调，设计复杂。

### KRaft 怎么解决
- **内置 Raft**：一部分节点充当控制器，它们用 Raft 协议在彼此间复制元数据，多数节点同意才算生效；
- **元数据存成日志**：元数据像普通消息一样存在 Kafka 自己的日志里，其他节点从日志中读取并更新，故障切换时不用重新全量加载；
- **部署更简单**：只需要部署 Kafka 本身。

### 方案对比：ZooKeeper 模式与 KRaft 模式
| 模式 | 元数据存放 | 部署组件 | 扩展性 | 状态 |
|---|---|---|---|---|
| ZooKeeper 模式 | 外部 ZooKeeper | Kafka 加 ZooKeeper | 分区多时切换较慢 | 4.0 起不再支持 |
| KRaft 模式 | Kafka 内部日志 | 只有 Kafka | 更好 | 当前方式 |

结论：新集群直接用 KRaft；仍在使用 ZooKeeper 模式的旧集群，升级到 4.0 之前需要先迁移。

## 易错点
- 以为 KRaft 改变了消息存储方式；它改的是元数据管理，消息的读写流程不变
- 以为 KRaft 不需要多个节点；为了容错，控制器也要多节点部署
- 以为 ZooKeeper 模式在新版本还能一直用；4.0 起已经移除

## 追问
### [f1] Raft 为什么要求多数派？
多数派意味着任意两次投票至少有一个节点重叠，不会出现两个互相冲突的结果。因此即使少数节点宕机，剩下的多数仍能继续工作。
