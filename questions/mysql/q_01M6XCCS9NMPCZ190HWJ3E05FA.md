---
id: q_01M6XCCS9NMPCZ190HWJ3E05FA
title: 线上出现死锁时怎么排查？
type: scenario
difficulty: medium
importance: 2
category: mysql
tags: [deadlock]
prerequisites: [q_01M6XCCPYKTRM16GFCJCWH4PJ2, q_01M6XCCS1G6X0HHKE230XEBNE0]
references:
  - { title: "MySQL 8.4 手册：How to Minimize and Handle Deadlocks（17.7.5.3）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html" }
  - { title: "MySQL 8.4 手册：Deadlocks in InnoDB（17.7.5）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
先用 `SHOW ENGINE INNODB STATUS` 看最近一次死锁日志，找出涉及的 SQL 和锁，分析加锁原因，再复现并按调整加锁顺序、加索引等办法修复。

## 要点
- [kp1|3] `SHOW ENGINE INNODB STATUS` 里有最近一次死锁的详细记录
- [kp2|3] 日志里看两个事务各自持有什么锁、在等什么锁
- [kp3|2] 找到涉及的 SQL，分析它们为什么会加这些锁
- [kp4] 打开 innodb_print_all_deadlocks 可以把每次死锁写入错误日志
- [kp5] 能复现的话在测试库模拟，验证修复方案

## 详解
### 先搞懂：出了事故，先看现场记录
线上某天突然报「Deadlock found」，一部分请求失败。这时的目标是弄清楚：哪两个事务互相卡住了、各拿了什么锁、各自在执行什么 SQL。

类比：路口发生了堵车，要调监控录像，看是哪几辆车在什么位置互相挡住了路。InnoDB 的死锁日志就是这份录像。

后文会用到这几个词：

- **死锁日志**：InnoDB 记录最近一次死锁详细情况的文本。
- **牺牲者**：被回滚的那个事务，日志里会标明。
- **加锁分析**：根据 SQL、索引和隔离级别，推断每条语句会加哪些锁。

### 步骤一：拿到死锁日志
执行 `SHOW ENGINE INNODB STATUS`，在输出里找 `LATEST DETECTED DEADLOCK` 这一段。它只保留**最近一次**死锁。

如果死锁偶发、容易被覆盖，可以开启 `innodb_print_all_deadlocks`，让每一次死锁都写进 MySQL 错误日志，便于事后回查。

### 步骤二：读懂日志
日志里一般包含：

1. 两个事务（通常叫 TRANSACTION 1、2）各自正在执行的 SQL；
2. 每个事务**持有**哪些锁（HOLDS THE LOCK(S)）；
3. 每个事务**在等待**哪个锁（WAITING FOR THIS LOCK TO BE GRANTED）；
4. 最后说明回滚了哪个事务（WE ROLL BACK TRANSACTION）。

对着看：事务 1 持有的锁，正是事务 2 在等的；事务 2 持有的，正是事务 1 在等的，这就是等待环。

### 步骤三：分析加锁
- 找出这些 SQL 在代码里的位置；
- 看它们用了哪个索引、什么隔离级别、是等值还是范围；
- 推断各自会加记录锁、间隙锁还是临键锁；
- 判断为什么两个事务会交叉：是顺序不同，还是间隙锁加插入。

### 步骤四：复现并修复
在测试环境按照日志里的顺序，用两个会话手动模拟，确认能复现。常见的修复办法：

- 统一加锁顺序；
- 给查询加合适的索引，缩小锁定范围；
- 拆分、缩短事务；
- 业务允许时降低隔离级别，减少间隙锁；
- 应用层对死锁错误增加重试。

### 补充：看正在发生的锁等待
MySQL 8.0 可以查 `performance_schema.data_locks` 和 `data_lock_waits`，看当前谁持有锁、谁在等。适合排查「现在卡住」的情况，而死锁日志适合排查「已经发生过」的死锁。

## 示例
```sql
-- 查看最近一次死锁
SHOW ENGINE INNODB STATUS;

-- 把所有死锁记录到错误日志
SET GLOBAL innodb_print_all_deadlocks = ON;
```

## 易错点
- 只看被回滚的那条 SQL；死锁是两边共同造成的，要看双方
- 只靠死锁日志猜原因，不去分析代码和索引
- 以为状态输出里保留了所有历史死锁；它只保留最近一次

## 追问
### [f1] 死锁日志里只有 SQL 片段，怎么定位业务代码？
用 SQL 里的表名、条件和事务的执行信息，到代码里搜对应语句，再还原它们所在的事务和调用顺序。

### [f2] 怎么避免同类死锁再次发生？
在修复后用两个会话重放原来的执行顺序，确认不再死锁。同时在应用里对死锁错误做重试，作为兜底。
