---
id: q_01M6XCDT33PA2H5MMQZVK5NMB5
title: Kafka 事务消息保证什么，Exactly Once 的适用范围是什么？
type: concept
difficulty: medium
importance: 2
category: distributed
tags: [distributed-transaction, idempotency]
appliesTo: ["Kafka >= 0.11"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
Kafka 事务保证一次事务里的多条消息要么全部可见、要么全部不可见；它的 Exactly Once 只适用于从 Kafka 读、处理后再写回 Kafka。

## 要点
- [kp1|3] Kafka 事务保证多条消息原子写入，要么都成功要么都失败
- [kp2|3] Exactly Once 仅限从 Kafka 消费、处理、再写入 Kafka 的链路
- [kp3|2] 它解决的问题和 RocketMQ 事务消息不同，不管本地数据库
- [kp4|2] 幂等生产者防止重试造成的重复写入
- [kp5] 消费端要设置只读已提交的消息才能看到事务效果

## 详解
### 先搞懂：一次搬运里的多件货
想象一个加工车间：从 A 仓库取原料，加工成产品，放进 B 仓库，同时登记「A 仓库取到哪了」。

如果加工到一半断电，重启后可能出现两种坏结果：原料取了两次，产品重复入库；或者进度登记了，产品却没放进去，产品丢了。

Kafka 事务就是让「放产品」和「登记进度」成为一个整体：要么都做，要么都不做。后文术语：
- **原子性**：一组操作要么全成功，要么全失败。
- **偏移量（offset）**：消费者读到哪条消息的位置记录。
- **幂等**：同一操作重复执行，结果不变。
- **Exactly Once**：每条消息的处理效果只生效一次。

### Kafka 事务保证什么
生产者开启事务后，可以在一个事务里向多个分区、多个主题写入多条消息，然后统一提交或中止。

- 提交：这些消息对消费者全部可见；
- 中止：这些消息全部不可见。

这是**多条消息的原子性**，跟 RocketMQ 事务消息不同。后者解决「本地数据库事务和发消息一致」，而 Kafka 事务管的是 Kafka 内部的多条写入。

### Exactly Once 的真实范围
Kafka 的 Exactly Once 靠两样东西配合：

1. **幂等生产者**：给每条消息带上序号，Broker 发现重复的就丢弃，避免重试造成重复写入；
2. **事务**：把「写出结果消息」和「提交消费位置」放进同一个事务。

所以它覆盖的是这样一条链路：从 Kafka 消费消息，处理，再把结果写回 Kafka。这条链路上，每条输入消息对输出的影响恰好一次。

### 它不覆盖什么
- 消费后去写 MySQL、调用外部接口：这些操作不在 Kafka 事务里，重复处理时仍要业务自己做幂等；
- 「每条消息只会被消费一次」：消费者仍可能重复拉到同一条消息，只是结果不会重复写入。

### 消费端要怎么配
消费者要把隔离级别设为只读已提交，才看不到未提交或已中止的事务消息。默认是读所有消息，这时事务的原子性对它没有效果。

## 示例
```java
// 伪代码：消费、处理、写回同一个事务
producer.initTransactions();
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
    producer.beginTransaction();
    for (ConsumerRecord<String, String> r : records) {
        producer.send(new ProducerRecord<>("out-topic", r.key(), handle(r.value())));
    }
    // 把消费位置也放进事务里一起提交
    producer.sendOffsetsToTransaction(currentOffsets(records), consumer.groupMetadata());
    producer.commitTransaction();
}
```

## 易错点
- 以为开了事务，所有消息就恰好被消费一次；它只保证 Kafka 到 Kafka 链路的处理效果
- 以为 Exactly Once 能覆盖写数据库；写数据库要自己做幂等
- 消费者没设只读已提交，事务隔离不生效

## 追问
### [f1] 事务消息和幂等生产者是什么关系？
事务依赖幂等生产者。幂等只防止单个生产者会话内、单个分区的重复写入，事务在此基础上让多条写入成为一个整体。
