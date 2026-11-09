---
id: q_01M6XCDSDY9G7764Q5E74HCHMK
title: TCC 的 Try、Confirm、Cancel 分别做什么？
type: concept
difficulty: medium
importance: 3
category: distributed
tags: [distributed-transaction]
prerequisites: [q_01M6XCDRMZ8V5W89D8ZQXWMSYS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
Try 先预占资源，所有 Try 都成功后 Confirm 真正执行业务，任何一个 Try 失败就 Cancel 释放预占；代价是每个业务都要写三个方法。

## 要点
- [kp1|3] Try：检查并预留资源，不做最终扣减
- [kp2|3] Confirm：所有 Try 成功后，把预留的资源真正使用掉
- [kp3|2] Cancel：任一 Try 失败时，释放预留的资源
- [kp4|2] Confirm 和 Cancel 必须幂等，因为可能被重试
- [kp5] TCC 在业务层实现，能处理数据库之外的操作，但侵入性强

## 详解
### 先搞懂：订酒店和机票
你要订一趟旅行，需要同时订机票和酒店。靠谱的订法是：

1. 先分别向两家「占座」：机票留一个座位，酒店留一间房，但还没付钱；
2. 两家都占到了，再分别「确认付款」；
3. 只要有一家没占到，就把另一家的占座取消。

TCC 就是把这个过程写进代码。后文术语：
- **预占**：把资源标记为「被这笔事务占用」，别人不能再用，但还没真正消耗。
- **补偿**：把已经做的事用反向操作抵消掉。
- **幂等**：同一操作做多次，结果和做一次一样。

### Try：先占住，不真正扣
Try 阶段检查业务是否可行，并预留资源。以扣库存为例：

- 检查可用库存够不够；
- 把库存拆成「可用」减少、「冻结」增加；
- 此时库存没有真正卖出，只是被占住了。

扣钱同理：先冻结金额，而不是直接扣掉。

### Confirm 与 Cancel：根据结果二选一
所有参与方的 Try 都成功后，协调者通知大家 **Confirm**：把冻结的库存真正扣除、把冻结的金额真正划走。

只要有一个 Try 失败，协调者通知已经 Try 成功的各方 **Cancel**：把冻结的库存还回可用，把冻结的金额解冻。

由于这两步前面已经决定了结果，必须最终执行成功，通常配合重试，所以必须幂等。

### TCC 的特点
- **在业务层实现**：不依赖数据库的分布式事务支持，所以可以覆盖上传图片、调用外部接口等数据库之外的操作。
- **不长期锁数据库**：Try 只是改状态，不像 2PC 那样一直占着数据库锁。
- **业务侵入性强**：每个业务都要拆成三个方法，开发和测试成本高。

## 示例
```java
// 伪代码：库存服务的 TCC 接口
public interface StockTcc {
    // Try：冻结库存
    boolean tryReserve(String txId, long skuId, int qty);

    // Confirm：真正扣减冻结的库存（幂等）
    boolean confirm(String txId);

    // Cancel：释放冻结的库存（幂等）
    boolean cancel(String txId);
}
```

## 易错点
- 以为 Try 就是真正执行业务；Try 只预留，不做最终扣减
- 以为 Cancel 失败可以忽略；不释放预留，资源会一直被占住
- Confirm 和 Cancel 没做幂等，重试时重复扣减或重复释放

## 追问
### [f1] TCC 和 2PC 最大的区别是什么？
2PC 在数据库层面，由数据库保持锁；TCC 在业务层面，由业务代码预占和补偿。TCC 灵活但要改业务，2PC 基本不用改业务但阻塞严重。
