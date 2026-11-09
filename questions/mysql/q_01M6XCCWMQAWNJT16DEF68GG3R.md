---
id: q_01M6XCCWMQAWNJT16DEF68GG3R
title: ReadView 怎么判断某个版本是否可见？
type: concept
difficulty: hard
importance: 3
category: mysql
tags: [isolation-mvcc]
prerequisites: [q_01M6XCCVTVRT0R8Z56R8VVY947, q_01M6XCCWCCW8JTV4FVVZXY5JF5]
appliesTo: ["MySQL InnoDB"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：InnoDB Multi-Versioning（行的事务 ID 与回滚指针、undo 重建旧版本）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html" }
  - { title: "MySQL 8.4 手册：Consistent Nonlocking Reads", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html" }
estimatedMinutes: 5
---

## 一句话
拿版本的事务 ID 和 ReadView 比：自己改的、读视图生成前已提交的可见；生成后才开始的、生成时还没提交的不可见。

## 要点
- [kp1|3] 版本的事务 ID 等于创建者自己的 ID，可见
- [kp2|3] 事务 ID 小于最小活跃 ID，说明已提交，可见
- [kp3|2] 事务 ID 大于等于下一个待分配 ID，说明生成后才开始，不可见
- [kp4|2] 介于两者之间，看是否在活跃列表里：在则不可见，不在则可见
- [kp5] 不可见就沿回滚指针找上一个版本，重复判断

## 详解
### 先搞懂：拿着照片对单子
银行下班前拍了一张照片，记着「此刻还有哪些柜员的业务没办完」。之后你要判断某张单子算不算数，只看经手柜员的编号：

- 编号比照片里最忙的最小编号还小：那些人早就办完了，算数。
- 编号在拍照之后才发的：当时还没来，不算数。
- 编号落在中间：要看他是不是照片里「还没办完」的那几个。

这就是 ReadView 判断可见性的思路。

后文会用到的术语：

- **事务 ID**：事务写数据时分配的递增编号，越大越晚。
- **活跃事务**：生成读视图时已开始、尚未提交的事务。
- **版本链**：一行数据的所有历史版本，通过回滚指针串起来。

### 四个关键值
ReadView 里有这几项：

- `creator_trx_id`：当前事务自己的 ID。
- `m_ids`：生成时的活跃事务 ID 列表。
- `min_trx_id`：`m_ids` 里最小的 ID。
- `max_trx_id`：生成时系统下一个要分配的事务 ID。

### 判断规则：对一个版本，按顺序问四句
设这个版本的事务 ID 为 `trx_id`：

1. `trx_id == creator_trx_id`：是自己改的，**可见**。
2. `trx_id < min_trx_id`：生成读视图时它就已经提交，**可见**。
3. `trx_id >= max_trx_id`：它是读视图生成之后才开始的事务，**不可见**。
4. `min_trx_id <= trx_id < max_trx_id`：看 `trx_id` 在不在 `m_ids` 里。在，说明生成时还没提交，**不可见**；不在，说明已提交，**可见**。

### 不可见怎么办
当前版本不可见，就顺着回滚指针去 undo log 找上一个版本，再用同样规则判断。一直找到可见的版本为止。如果整条链都不可见，这行对当前事务就等于不存在。

### 举个例子
某行当前值 30，事务 300 改的；上一个版本 20，事务 200 改的；更早是 10，事务 100 创建。事务 A 的读视图里 `m_ids = [200, 300]`，`min_trx_id = 200`，`max_trx_id = 301`。

- 版本 30：300 在活跃列表里，不可见。
- 版本 20：200 在活跃列表里，不可见。
- 版本 10：100 小于 200，可见。

所以 A 读到 10。

### 进阶：为什么两个级别结果不同（基础薄弱可先跳过）
规则是同一套，差别只在读视图什么时候生成。读已提交每次查询重新生成，`m_ids` 变了，刚提交的事务就变成可见。可重复读复用同一个，`m_ids` 不变，判断结果也不变。

## 易错点
- 以为只比较大小；中间区间必须再查活跃列表
- 以为事务 ID 小就一定已提交；小于最小活跃 ID 才能这么判断
- 忘了自己改的版本也要判可见；等于 `creator_trx_id` 时直接可见

## 追问
### [f1] 为什么中间区间的事务可能已提交？
事务 ID 是开始时分配的，不是提交时分配的。ID 较小的事务可能开始早但还没提交，ID 较大的反而可能先提交，所以必须查活跃列表。

### [f2] 版本链找到最后都不可见怎么办？
这行数据对当前事务相当于不存在，查询不会返回它。比如这行是读视图生成之后才被别的事务插入的。
