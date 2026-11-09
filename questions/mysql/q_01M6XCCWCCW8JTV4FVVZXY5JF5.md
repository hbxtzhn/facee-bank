---
id: q_01M6XCCWCCW8JTV4FVVZXY5JF5
title: ReadView 是什么，包含哪些信息？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [isolation-mvcc]
prerequisites: [q_01M6XCCVTVRT0R8Z56R8VVY947]
appliesTo: ["MySQL InnoDB"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Consistent Nonlocking Reads", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html" }
  - { title: "MySQL 8.4 手册：InnoDB Multi-Versioning", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html" }
estimatedMinutes: 4
---

## 一句话
ReadView 是 InnoDB 做一致性读时生成的快照，记录当时还没提交的活跃事务列表、最小和最大事务 ID，用来判断某个版本能不能看。

## 要点
- [kp1|3] ReadView 是普通查询时生成的快照信息，用来判断版本可见性
- [kp2|3] 含活跃事务 ID 列表、其中最小的 ID、下一个将分配的 ID
- [kp3|2] 还记录创建这个读视图的事务自己的 ID
- [kp4|2] 读已提交每次查询生成新的，可重复读只在第一次生成
- [kp5] 只有读已提交和可重复读两个级别用它

## 详解
### 先搞懂：拍一张「当时谁还在忙」的照片
银行下班前拍一张照片，记下「此刻哪些柜员还有业务没办完」。之后你拿着照片判断：凡是照片里没在忙的人办完的单子，都算数；照片里还在忙的人，或者拍照之后才来的人办的单子，一律不算。

ReadView 就是这张照片。

后文会用到的术语：

- **活跃事务**：已经开始、但还没提交的事务。
- **事务 ID**：事务写数据时分配的递增编号，编号越大越晚开始。
- **一致性读**：普通查询读到一个固定时间点的数据，不受之后改动影响。

### ReadView 里有什么
一个 ReadView 通常包含四项信息：

- `m_ids`：生成时所有活跃事务的 ID 列表。
- `min_trx_id`：活跃事务中最小的 ID。
- `max_trx_id`：生成时，系统下一个要分配的事务 ID。
- `creator_trx_id`：创建这个读视图的事务自己的 ID。

### 它怎么用
每行数据的版本都带有修改它的事务 ID。拿这个 ID 和 ReadView 里的信息比较：

- 事务已经提交的版本，可以看。
- 事务还没提交、或在生成读视图之后才开始的版本，看不了。
- 自己改的版本，当然看得到。

具体比较规则是另一道题的内容。

### 什么时候生成
这决定了两个隔离级别的差别：

- 读已提交：每次执行查询，都重新生成一个 ReadView。别人刚提交的改动，下一次查询就能看到。
- 可重复读：事务第一次查询时生成，之后一直复用。

### 进阶：读视图和锁无关（基础薄弱可先跳过）
ReadView 只管快照读。`UPDATE`、`SELECT ... FOR UPDATE` 这类当前读，不看 ReadView，而是读最新数据并加锁。

## 易错点
- 以为 ReadView 是事先拷贝了一份数据；它只是一份事务 ID 的信息，数据靠版本链还原
- 以为可重复读每次查询都生成新的 ReadView；它只在第一次生成
- 以为 `max_trx_id` 是活跃事务里最大的 ID；它是系统下一个要分配的 ID

## 追问
### [f1] 事务开启后，ReadView 马上生成吗？
不一定。可重复读下，是事务里第一次执行普通查询时才生成，而不是 `START TRANSACTION` 时。

### [f2] ReadView 里为什么要记 creator_trx_id？
为了让事务能看到自己做的修改。自己改的版本，事务 ID 等于 `creator_trx_id`，直接判定可见。
