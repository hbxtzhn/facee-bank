---
id: q_01M6XCDZC4SE4EMESBBXTJ7G76
title: 什么是 AMQP 协议？
type: concept
difficulty: easy
importance: 1
category: distributed
tags: [message-model, mq-selection]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
AMQP 是跨语言、跨平台的二进制消息协议，它规定消息通过 Exchange 按绑定规则路由到 Queue，RabbitMQ 是它的典型实现。

## 要点
- [kp1|3] AMQP 是线路层协议，规定了数据在网络上怎么传
- [kp2|3] 消息先到 Exchange，再按绑定规则进入 Queue
- [kp3|2] 协议是二进制的、跨语言，不同语言客户端可以互通
- [kp4] RabbitMQ 是最典型的实现，路由比 JMS 更细

## 详解
### 先搞懂：协议是双方说话的语法
两个人要沟通，得说同一种语言。AMQP 就是消息中间件的一套通用语言，规定消息怎么编码、怎么发、怎么确认。只要都遵守，Java 客户端和 Python 客户端都能和同一个 Broker 对话。

后文用到的几个词：
- **线路层协议**：规定字节在网络上怎么排列的协议。
- **Exchange**：交换机，接收消息并决定送到哪些队列。
- **Queue**：队列，存消息等消费者来取。
- **绑定**：Exchange 和 Queue 之间的路由规则。

### 路由模型：先到交换机，再到队列
生产者不直接往队列发，而是把消息发给 Exchange，并带上一个路由键。Exchange 根据绑定规则决定送进哪些队列。消费者只和队列打交道。

这样生产者和队列之间多了一层，规则可以灵活调整。

### 和 JMS 的区别
| 维度 | AMQP | JMS |
|---|---|---|
| 层次 | 线路层协议 | Java API 规范 |
| 跨语言 | 可以 | 主要是 Java |
| 路由 | Exchange 路由，较细 | 队列和主题两种模型 |

结论：需要跨语言、复杂路由，选 AMQP 体系的 RabbitMQ；纯 Java 项目且习惯 JMS 接口也可以用 JMS。

## 易错点
- 以为 AMQP 是一个软件；它是协议，RabbitMQ 才是软件
- 以为所有消息队列都支持 AMQP；Kafka 有自己的协议
- 以为生产者直接发队列；AMQP 里是先发 Exchange

## 追问
### [f1] AMQP 和 JMS 能一起用吗？
有些中间件两种都支持，但它们定位不同：JMS 是 Java 代码层的接口，AMQP 是网络上的数据格式。
