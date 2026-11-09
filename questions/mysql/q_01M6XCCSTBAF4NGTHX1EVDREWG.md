---
id: q_01M6XCCSTBAF4NGTHX1EVDREWG
title: undo log 是什么，用来做什么？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [database-log, isolation-mvcc]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
undo log 记录数据被修改之前的旧值，事务回滚时按它恢复；它同时也是 MVCC 读取历史版本的基础。

## 要点
- [kp1|3] undo log 记录修改前的旧数据，用来回滚事务
- [kp2|3] 它保证了事务的原子性：失败时能恢复到修改前
- [kp3|2] MVCC 靠 undo log 串起的历史版本，实现一致性读
- [kp4] 不再有事务需要的旧版本，会被后台清理
- [kp5] undo log 和记录重做的 redo log 作用不同

## 详解
### 先搞懂：改之前先留一份底
你在文档里改一段话，编辑器会保存修改前的版本，这样「撤销」时才能恢复。undo log 就是数据库的「撤销记录」。

后文会用到这几个词：

- **回滚**：撤销事务里已经做过的修改。
- **旧值**：数据被改之前的内容。
- **MVCC**：多版本并发控制，让读操作不用加锁就能读到某个时间点的数据。

### 做了什么：修改前先记旧值
事务修改数据时，InnoDB 先把修改前的内容记到 undo log 里，再改数据本身。

- 更新一行：记下旧的列值；
- 插入一行：记下「怎么删掉它」；
- 删除一行：记下「怎么把它恢复」。

### 用途一：回滚
事务中途失败，或者主动执行 `ROLLBACK`，InnoDB 按 undo log 里的内容，把修改一步步反向撤销，数据恢复到事务开始前，保证了**原子性**。

事务顺利提交时，这些记录不会马上删除，而是在不再被需要时由后台清理。

### 用途二：MVCC 读取历史版本
同一行数据被多次修改后，每个旧版本通过 undo log 串成一条链，最新记录里有指针指向上一个版本。

一个事务做普通读时，如果最新版本对自己不可见，就顺着这条链往回找，直到找到自己可以看到的版本。这样读操作不需要加锁，也不会被写操作阻塞。

### 什么时候清理
只要还有事务可能读到某个旧版本，对应的 undo log 就要保留。长时间不提交的事务，会让大量旧版本无法清理，占用空间。所以要避免长事务。

### 和 redo log 的区别
- undo log：记录旧值，用于**回滚**和 **MVCC**；
- redo log：记录修改后的内容，用于崩溃后**恢复已提交的数据**，保证持久性。

## 示例
```sql
START TRANSACTION;
UPDATE account SET balance = balance - 100 WHERE id = 1;
-- 此时 InnoDB 已把旧的 balance 记入 undo log
ROLLBACK;   -- 按 undo log 把 balance 恢复为原值
```

## 易错点
- 以为事务提交后 undo log 立刻删除；还要看有没有别的事务需要旧版本
- 以为 undo log 和 redo log 作用相同；一个负责回滚和多版本，一个负责崩溃恢复
- 长事务不管，导致旧版本越积越多

## 追问
### [f1] undo log 和 redo log 的区别？
undo log 记录修改前的旧值，用来回滚和 MVCC；redo log 记录修改后的内容，在崩溃重启时重放，保证已提交的事务不丢。

### [f2] 为什么长事务不好？
长事务让它开始之后产生的旧版本都不能清理，undo 空间不断增长，也会拖慢查询，因为要沿着更长的版本链找可见版本。
