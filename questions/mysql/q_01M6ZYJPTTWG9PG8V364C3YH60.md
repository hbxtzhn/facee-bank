---
id: q_01M6ZYJPTTWG9PG8V364C3YH60
title: MySQL 是怎么保证事务的四个特性的？
type: concept
difficulty: medium
importance: 3
category: mysql
tags: [transaction-basics, database-log]
prerequisites: [q_01M6XCCSHSV6BBK72JGGX9R1NB, q_01M6XCCSTBAF4NGTHX1EVDREWG]
appliesTo: ["MySQL InnoDB"]
references:
  - { title: "MySQL 8.4 手册：Redo Log", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html" }
  - { title: "MySQL 8.4 手册：Undo Logs", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html" }
  - { title: "MySQL 8.4 手册：InnoDB Recovery", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
InnoDB 用 undo log 保证原子性，redo log 保证持久性，锁加 MVCC 保证隔离性；一致性靠前三者再加业务约束共同保证。

## 要点
- [kp1|3] 原子性：undo log 记录修改前的旧值，事务回滚时按它还原
- [kp2|3] 持久性：提交前先把 redo log 写入磁盘，宕机重启后可重做
- [kp3|2] 隔离性：写写冲突靠锁，读写并发靠 MVCC 读历史版本
- [kp4|2] 一致性是目标，由前三个特性加业务规则共同保证
- [kp5] undo log 还是 MVCC 版本链的数据来源

## 详解
### 先搞懂：转账为什么不会出错
你做过转账：A 扣 100，B 加 100。这两步要么都成功，要么都不发生。

可以把事务想成银行柜员办业务。办之前先抄一份旧账本，方便撤销。办的时候先记流水，防止停电丢单。同一时间一个账户只让一个柜员动手，避免互相干扰。

后文会用到的术语：

- **事务**：一组要么全做、要么全不做的操作。
- **undo log（回滚日志）**：记录改动之前的旧值，用来撤销。
- **redo log（重做日志）**：记录改动之后的结果，用来在宕机后重放。
- **MVCC（多版本并发控制）**：读数据时读旧版本快照，不用等写操作。

### 原子性：靠 undo log 撤销
事务修改一行数据前，InnoDB 先把旧值写进 undo log。

事务中途失败，或者你主动执行 `ROLLBACK`，InnoDB 就按 undo log 把数据一步步改回去。事务提交后，这些旧值不会立刻删掉。因为别的事务可能还要读旧版本，等没人用了才会清理。

### 持久性：靠 redo log 重做
InnoDB 修改数据时，先改内存里的数据页，再把改动记入 redo log。数据页不会马上写盘。

提交时只要保证 redo log 已落盘，事务就算持久了。就算此时宕机，重启后也能用 redo log 把改动重做出来。先写日志、后写数据页的做法叫 WAL（预写日志）。

为什么不直接写数据页？因为数据页散落在磁盘各处，随机写慢；redo log 是顺序追加，写起来快。

### 隔离性：锁加 MVCC
多个事务同时跑时，InnoDB 分两种情况处理：

- **写和写冲突**：加锁。一个事务改某一行时，别的事务想改同一行就得等。
- **读和写并发**：普通查询读 MVCC 的历史版本快照，不加锁，也就不用等写操作。

能看到多新的数据，由隔离级别决定。

### 一致性：不是单靠数据库
一致性指事务前后数据都符合规则，比如转账前后总金额不变。

数据库保证了前三个特性，再加上主键、唯一、外键等约束，一致性才有基础。但「转账总额不变」这种业务规则，要由你的代码写对。

### 进阶：redo 和 undo 的关系（基础薄弱可先跳过）
- 宕机恢复时先应用 redo log，再回滚没提交的事务。
- 与 redo log 不同，binlog 是 MySQL 服务层的日志，主要用于主从复制和数据恢复。

## 易错点
- 以为 redo log 和 undo log 作用相同；前者重放已做的改动，后者撤销未提交的改动
- 以为提交时数据页必须已写盘；实际只要 redo log 落盘即可
- 以为数据库能单独保证一致性；业务规则仍要由代码保证

## 追问
### [f1] 为什么提交时不直接把数据页写盘？
数据页散落在磁盘各处，随机写慢，而且一次提交可能只改了页中很小一部分。redo log 是顺序追加，写得快，足够在宕机后恢复数据。

### [f2] redo log 和 binlog 有什么区别？
redo log 是 InnoDB 引擎层的日志，用于宕机恢复。binlog 是 MySQL 服务层的日志，所有引擎都有，主要用于主从复制和按时间点恢复。
