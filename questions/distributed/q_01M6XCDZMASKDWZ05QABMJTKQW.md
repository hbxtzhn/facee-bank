---
id: q_01M6XCDZMASKDWZ05QABMJTKQW
title: RabbitMQ 的 Exchange 有哪几种路由模型？
type: concept
difficulty: medium
importance: 2
category: distributed
tags: [message-model, mq-selection]
prerequisites: [q_01M6XCDZC4SE4EMESBBXTJ7G76]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
RabbitMQ 内置四种 Exchange：direct 按路由键精确匹配，fanout 广播给所有绑定队列，topic 按通配符匹配，headers 按消息头属性匹配。

## 要点
- [kp1|3] direct：路由键和绑定键完全相同才投递
- [kp2|3] fanout：忽略路由键，投给所有绑定的队列
- [kp3|2] topic：绑定键支持通配符，`*` 匹配一个词，`#` 匹配多个词
- [kp4|2] headers：按消息头里的键值对匹配，不看路由键
- [kp5] 这套路由比 JMS 的队列加主题更细

## 详解
### 先搞懂：邮局分拣的四种规则
生产者把信交给邮局的分拣员（Exchange），分拣员再按规则投进不同信箱（Queue）。规则不同，分拣方式也不同。

后文用到的几个词：
- **路由键**：生产者发消息时带的一个标签。
- **绑定键**：队列绑定到 Exchange 时设定的匹配规则。
- **绑定**：把队列和 Exchange 连起来。

### direct：对暗号才投递
消息的路由键和队列的绑定键完全一样，才会送进该队列。适合按类型精确分发，比如日志级别 error 只进错误队列。

### fanout：广播给所有人
不管路由键是什么，所有绑定到它的队列都收到一份。适合通知广播。

### topic：通配符匹配
路由键由点分隔的几个词组成，比如 `order.pay.success`。绑定键可以用 `*` 匹配恰好一个词，`#` 匹配零个或多个词。例如绑定键 `order.#` 能接收所有订单相关消息。

### headers：看消息头
不看路由键，而是比较消息头里的键值对是否满足绑定要求。灵活，但实际项目里用得较少。

### 方案对比：怎么选
| 类型 | 匹配方式 | 典型场景 |
|---|---|---|
| direct | 精确匹配 | 按类型分发 |
| fanout | 无条件广播 | 通知所有系统 |
| topic | 通配符匹配 | 按层级分类订阅 |
| headers | 消息头匹配 | 条件复杂的特殊场景 |

结论：大多数场景用 direct、fanout、topic 就够了，headers 很少用。

## 易错点
- 以为 fanout 会看路由键；它完全忽略路由键
- 把 `*` 和 `#` 搞混；`*` 只匹配一个词，`#` 匹配多个
- 以为生产者直接发队列；其实都是先发给 Exchange，不指定名字时用的是默认交换机

## 追问
### [f1] 消息发到 Exchange 但没匹配到队列会怎样？
默认情况下消息会被丢弃。可以设置强制投递标记，让不可路由的消息退回给生产者，或配置备用交换机兜底。

### [f2] topic 和 direct 怎么选？
只需要精确匹配用 direct；需要按层级、前缀灵活订阅时用 topic。
