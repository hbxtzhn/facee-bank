---
id: q_01M6XCDRXFWD20QE7S5AR21G9G
title: TCC 的 Confirm 和 Cancel 为什么要幂等？
type: concept
difficulty: medium
importance: 2
category: distributed
tags: [distributed-transaction, idempotency]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Confirm 和 Cancel 在超时、网络重试时可能被多次调用，而且到这一步只能继续往前走，所以重复执行的结果必须和执行一次完全相同。

## 要点
- [kp1|3] 网络超时后协调者会重试，Confirm 和 Cancel 可能被调用多次
- [kp2|3] 到 Confirm 或 Cancel 阶段已无退路，必须最终执行成功
- [kp3|2] 幂等指同一操作执行一次和多次，结果一样
- [kp4|2] 常用状态判断：已经确认或取消过，就直接返回成功
- [kp5] Cancel 还要处理没收到 Try 就先收到 Cancel 的情况

## 详解
### 先搞懂：转账重复点了两次
想象你给朋友转 100 元，点了一下转账，页面卡住了，你又点了一下。如果系统每点一次都扣一次，你就被扣了 200 元。

好的系统会认出「这是同一笔转账」，第二次直接返回成功，不再扣钱。这种「做一次和做很多次效果一样」的性质，叫**幂等**。

后文术语：
- **TCC**：Try 预占资源，Confirm 真正执行，Cancel 释放预占的资源。
- **协调者**：驱动各方依次执行 Try、Confirm、Cancel 的角色。
- **幂等**：同一个操作重复执行，结果不变。
- **悬挂与空回滚**：Cancel 先于 Try 到达，或 Try 在 Cancel 之后才到达。

### 为什么会被重复调用
协调者发出 Confirm 后，没收到回应。它不知道对方是没收到、已处理但回应丢了，还是处理一半宕机了。

协调者唯一安全的做法是再发一次。因此参与方会多次收到同一个 Confirm 或 Cancel。这在分布式环境里无法避免。

### 为什么没有退路
TCC 里所有 Try 都成功后，才会进入 Confirm 阶段。这时资源已经预留好，决定也已经做出。

- Confirm 阶段只能继续重试直到成功，不能改成回滚；
- Cancel 阶段同理，只能继续重试直到资源释放。

既然要反复重试直到成功，就必须保证重试不会造成副作用，所以要幂等。

### 怎么实现幂等
常见做法是给每个全局事务记录一个状态：

1. 收到 Confirm 时，先查状态；如果已经是已确认，直接返回成功；
2. 如果是预占状态，执行业务，并把状态改成已确认；
3. 状态判断和业务修改放在同一个本地事务里，避免并发时重复扣减。

Cancel 同理。另外，如果 Cancel 先到而 Try 还没到，要记录一条「已取消」，让后来的 Try 直接拒绝，否则预占的资源永远没人释放。

## 示例
```java
// 伪代码：Confirm 幂等
@Transactional
public boolean confirm(String txId) {
    TccRecord r = recordMapper.selectForUpdate(txId);
    if (r == null) return true;            // 没有记录，无需处理
    if (r.getStatus() == CONFIRMED) return true; // 已确认，直接成功
    deductReserved(r);                     // 把预占的资源真正扣掉
    r.setStatus(CONFIRMED);
    recordMapper.update(r);
    return true;
}
```

## 易错点
- 以为只有 Try 需要考虑重复；Confirm 和 Cancel 才是最常被重试的
- 幂等判断和业务修改不在同一事务，并发时仍会重复执行
- 忽略 Cancel 先于 Try 到达的情况，导致资源被永久预占

## 追问
### [f1] Try 需要幂等吗？
也需要，重复的 Try 不应该重复预占资源。不过 Try 失败还有 Cancel 兜底，而 Confirm 和 Cancel 没有退路，所以它们的幂等要求更严格。
