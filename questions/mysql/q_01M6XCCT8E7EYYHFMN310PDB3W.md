---
id: q_01M6XCCT8E7EYYHFMN310PDB3W
title: MySQL 的事务隔离级别有哪几种？
type: concept
difficulty: easy
importance: 3
category: mysql
tags: [isolation-mvcc]
prerequisites: [q_01M6XCCSHSV6BBK72JGGX9R1NB]
appliesTo: ["MySQL InnoDB"]
references:
  - { title: "MySQL 8.4 手册：Transaction Isolation Levels（17.7.2.1）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html" }
  - { title: "MySQL 8.4 手册：Consistent Nonlocking Reads（17.7.2.3）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
隔离级别有读未提交、读已提交、可重复读、串行化四种，越往后隔离越强、并发越低；MySQL 默认是可重复读。

## 要点
- [kp1|3] 四种级别：读未提交、读已提交、可重复读、串行化
- [kp2|3] 级别越高，能避免的并发问题越多，并发性能越低
- [kp3|2] 读未提交会脏读；读已提交避免脏读，但有不可重复读
- [kp4|2] MySQL 默认可重复读，InnoDB 下它基本也避免了幻读
- [kp5] 串行化让事务排队执行，隔离最强

## 详解
### 先搞懂：几个人同时改同一张表会出什么乱子
想象你在查订单，同时别人在改同一个订单。你可能读到对方还没确认的数据，也可能前后两次查询结果不一样。隔离级别，就是规定「你能看到别人的多少改动」。

后文会用到的三个并发问题：

- **脏读**：读到别的事务还没提交的数据。
- **不可重复读**：同一事务里两次读同一行，结果不一样。
- **幻读**：同一事务里两次按相同条件查询，行数不一样。

### 四种级别对比：从宽松到严格
| 级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| 读未提交 | 可能 | 可能 | 可能 |
| 读已提交 | 避免 | 可能 | 可能 |
| 可重复读 | 避免 | 避免 | 标准定义下可能 |
| 串行化 | 避免 | 避免 | 避免 |

结论：普通业务用 MySQL 默认的可重复读即可；有些团队会改用读已提交，以减少加锁范围。

逐个看：

- 读未提交：能读到别人没提交的数据，最宽松，实际很少用。
- 读已提交：只读别人已经提交的数据，每次查询都能看到最新提交的结果。
- 可重复读：事务里反复读同一行，结果始终一样。
- 串行化：让事务排队，一个接一个执行，最安全，也最慢。

### MySQL 的特别之处
SQL 标准里，可重复读允许幻读。但 InnoDB 的可重复读通过 MVCC 和间隙锁，在大多数情况下也避免了幻读，所以比标准更强。

## 示例
```sql
-- 查看当前隔离级别（MySQL 8.0 写法）
SELECT @@transaction_isolation;

-- 只修改当前会话的隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

## 易错点
- 以为 MySQL 默认是读已提交；默认是可重复读，读已提交是 Oracle 等数据库的常见默认
- 以为级别越高越好；隔离越强，并发越低，要按业务取舍
- 以为可重复读在 InnoDB 里完全没有幻读；加锁的当前读等场景仍要小心

## 追问
### [f1] 读已提交和可重复读底层差在哪？
差在 MVCC 里读视图生成的时机。读已提交每次查询都生成新的读视图，可重复读只在事务第一次查询时生成并一直复用。
