---
id: q_01M6ZYJZ6XBT6A646KZ4SZND2V
title: RocketMQ 的事务消息是怎么工作的？
type: concept
difficulty: medium
importance: 2
category: distributed
tags: [distributed-transaction, mq-selection]
prerequisites: [q_01M6XCDSNTMRSCVNMW2SVPXVEG]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
RocketMQ 先发一条消费者看不到的半消息，执行本地事务后再提交或回滚；如果通知丢了，Broker 会回头问生产者事务结果。

## 要点
- [kp1|3] 半消息发到 Broker 的特殊队列，消费者暂时看不到
- [kp2|3] 本地事务成功就提交消息，失败就回滚消息
- [kp3|2] 提交或回滚的通知丢失时，Broker 定时回查生产者
- [kp4|2] 可以看作 2PC 的变种，但保证的是最终一致
- [kp5] 核心价值：解决本地事务成功但消息没发出的问题

## 详解
### 先搞懂：先占座，再确认
想象你去电影院订票。你先让售票员给你留一个座位（还没出票），然后你去付款。付款成功就回来说「确认」，座位变成你的；付款失败就说「取消」，座位放回去。

要是你付完款忘了回来说「确认」，售票员过一会儿会打电话问你：「你那笔付款成功了吗？」再决定座位给不给你。

RocketMQ 事务消息就是这个流程。后文术语：
- **半消息**：已经存进 Broker，但消费者暂时看不到的消息，相当于「留座」。
- **本地事务**：生产者自己服务内数据库的事务。
- **回查**：Broker 主动问生产者本地事务的状态。

### 完整流程
1. **发半消息**：生产者把消息发给 Broker，Broker 存起来但不让消费者看到；
2. **执行本地事务**：半消息发送成功后，生产者执行本地事务，比如写订单；
3. **提交或回滚**：生产者根据本地事务的结果通知 Broker；
   - 本地事务成功，通知提交，消息变为可见，消费者可以消费；
   - 本地事务失败，通知回滚，Broker 丢弃这条半消息；
4. **回查兜底**：如果第 3 步的通知没送达，或者本地事务状态暂时未知，Broker 会定时回调生产者的回查接口。生产者告诉它事务到底成功没有，Broker 再据此提交或回滚。

### 为什么要这样设计
最麻烦的情况是「本地事务成功了，消息没发出去」。如果先执行本地事务、再发消息，发消息失败就会丢通知。如果先发消息、再执行本地事务，事务失败就会发出错误通知。

先发半消息能确认 Broker 已经收到，再执行本地事务；最后用提交加回查把结果传达到。这样两边最终一定一致。

### 生产者要实现什么
生产者要实现两个逻辑：

- 执行本地事务，并返回提交、回滚或未知；
- 回查逻辑：根据业务数据判断事务是否成功，比如按订单号查订单。

## 示例
```java
// 伪代码：RocketMQ 事务监听器
public class OrderTxListener implements TransactionListener {
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        try {
            orderService.createOrder(arg);           // 本地事务
            return LocalTransactionState.COMMIT_MESSAGE;
        } catch (Exception e) {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 回查：按业务键查订单是否已存在
        return orderService.exists(msg.getKeys())
                ? LocalTransactionState.COMMIT_MESSAGE
                : LocalTransactionState.ROLLBACK_MESSAGE;
    }
}
```

## 易错点
- 以为事务消息能保证下游也执行成功；它只保证上游事务和消息一致
- 回查逻辑只看内存状态，服务重启后查不到，会误判回滚
- 以为消息提交后只会被消费一次；仍可能重复投递，消费端要幂等

## 追问
### [f1] 回查会一直重试吗？
不会无限回查。回查有次数限制，超过后 Broker 会按回滚处理，具体次数和间隔以所用版本的配置为准。

### [f2] 本地事务执行到一半服务宕机会怎样？
重启后 Broker 回查，生产者根据数据库里的业务数据判断：数据已提交就返回提交，没有就返回回滚。
