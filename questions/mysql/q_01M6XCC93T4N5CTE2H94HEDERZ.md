---
id: q_01M6XCC93T4N5CTE2H94HEDERZ
title: 为什么 binlog 和 redo log 要用两阶段提交？
type: concept
difficulty: hard
importance: 3
category: mysql
tags: [database-log, distributed-transaction]
prerequisites: [q_01M6XCC8EV6YCRMCP3358H90ST, q_01M6ZYJKEHVRZX1GW646T1F4FK]
appliesTo: ["MySQL >= 5.7，InnoDB"]
references:
  - { title: "MySQL 8.4 手册：The Binary Log（InnoDB 两阶段提交与崩溃恢复）", url: "https://dev.mysql.com/doc/refman/8.4/en/binary-log.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
redo log 和 binlog 是两份独立的日志，只写成功一份就宕机，会让主库数据和备份、从库不一致；两阶段提交让两份日志要么都有效，要么都无效。

## 要点
- [kp1|3] 两份日志各写各的，中间可能宕机，导致一份有、一份没有
- [kp2|3] 两阶段提交：先写 redo log（prepare），再写 binlog，最后 redo log 提交（commit）
- [kp3|2] 恢复时，prepare 状态的事务，要看 binlog 是否完整来决定提交还是回滚
- [kp4] 目的是让主库和用 binlog 恢复出的备份、从库保持一致

## 详解
### 先搞懂：同一笔账，两本账本要对得上
想象你改一笔账，需要同时在店里的施工单（redo log）和店长的账本（binlog）上登记。如果只写了一本，人就走了，两本账就对不上了。后面用店长的账本去恢复、或分店照着它做账，结果就和店里实际的账不一样。

数据库里就是这个问题。后文用到的术语：

- **crash-safe**：宕机重启后，已提交的数据不丢；
- **prepare、commit**：redo log 的两个状态；
- **两阶段提交**：把提交拆成「准备」和「确认」两步，确保两份日志一致。

### 如果不用两阶段：两种先后顺序都有问题
**先写 redo log，后写 binlog**：redo log 写完后宕机，binlog 还没写。重启后主库可以用 redo log 把这次修改恢复出来，但 binlog 里没有这条记录。之后用 binlog 做备份恢复，或者从库同步，这次修改就丢了，数据与主库不一致。

**先写 binlog，后写 redo log**：binlog 写完后宕机，redo log 还没写。重启后主库没有这次修改，但 binlog 里有。之后用 binlog 恢复或从库同步，会多出一次主库没有的修改，同样不一致。

### 两阶段提交怎么解决
1. 引擎写 redo log，状态是 prepare；
2. 执行器写 binlog；
3. 引擎把 redo log 改成 commit。

宕机后重启，对每个处于 prepare 状态的事务检查 binlog：

- binlog 完整：说明第 2 步已经完成，提交这个事务；
- binlog 不完整或没有：回滚这个事务。

这样无论在哪一步宕机，redo log 和 binlog 的结果都一致。

## 易错点
- 以为只要 redo log 写成功就万事大吉；binlog 缺失会影响备份恢复和从库
- 以为宕机后 prepare 状态的事务一律回滚；还要看 binlog 是否已完整写入
- 以为两阶段提交是为了让写入更快；它是为了保证一致，不是为了性能

## 追问
### [f1] 在 binlog 写入之前宕机，重启后怎么处理？
这时 redo log 是 prepare，binlog 没有这次记录，恢复时会回滚这个事务，数据回到修改前，两份日志保持一致。

### [f2] 在 redo log commit 之前、binlog 已写完时宕机呢？
binlog 已经完整，恢复时会提交这个事务，数据保留这次修改，从库和备份也有，同样一致。
