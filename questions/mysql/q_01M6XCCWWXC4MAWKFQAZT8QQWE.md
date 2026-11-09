---
id: q_01M6XCCWWXC4MAWKFQAZT8QQWE
title: 可重复读和读已提交的 ReadView 有什么区别？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [isolation-mvcc]
prerequisites: [q_01M6XCCT8E7EYYHFMN310PDB3W, q_01M6XCCV1JZHEPW18YP6YB2ETH, q_01M6XCCVTVRT0R8Z56R8VVY947]
appliesTo: ["MySQL InnoDB"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Consistent Nonlocking Reads（快照时机与 DML）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html" }
  - { title: "MySQL 8.4 手册：Transaction Isolation Levels（REPEATABLE READ / READ COMMITTED）", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html" }
estimatedMinutes: 3
---

## 一句话
读已提交每次查询都生成新的 ReadView，所以能看到别人刚提交的改动；可重复读只在事务第一次查询时生成并一直复用。

## 要点
- [kp1|3] 读已提交：每次执行普通查询前，都重新生成 ReadView
- [kp2|3] 可重复读：事务第一次普通查询时生成，直到事务结束
- [kp3|2] 因此读已提交会不可重复读，可重复读不会
- [kp4|2] 判断可见性的规则相同，差别只在读视图何时生成
- [kp5] 两者都不对当前读生效，当前读读最新数据并加锁

## 详解
### 先搞懂：每次都拍新照片，还是只拍一张
你在看一份实时变化的订单列表：

- 每次刷新都重新拍一张照片：你每次看到的都是最新的，但前后两次可能不一样。
- 第一次看的时候拍一张照，之后一直对着这张照片看：不管别人怎么改，你看到的一直是同一个样子。

前一种是读已提交，后一种是可重复读。

后文会用到的术语：

- **ReadView（读视图）**：一份记录「生成时有哪些事务还没提交」的快照信息，用来判断版本能不能看。
- **快照读**：普通 `SELECT`，通过读视图读历史版本。
- **提交**：确认事务的修改，从此对别人可见。

### 读已提交：每次查询重新生成
事务里每执行一次普通查询，InnoDB 都会生成一个新的读视图。

举例：事务 A 先查某行是 100；这时事务 B 把它改成 200 并提交；A 再查时重新生成读视图，B 已经提交，所以 A 读到 200。

结果就是同一事务里前后两次读到的值不同，也就是不可重复读。

### 可重复读：只生成一次
事务里第一次执行普通查询时生成读视图，之后复用，直到事务结束。

同样的例子：A 第一次查是 100，B 后来改成 200 并提交。A 再查时，读视图还是第一次生成的那个，B 在里面被记为「当时还没提交」，不可见。A 沿着版本链找到旧版本，仍然读到 100。

### 方案对比：两个级别的读视图
| 级别 | 读视图何时生成 | 能否看到别人新提交的数据 | 不可重复读 |
|---|---|---|---|
| 读已提交 | 每次普通查询 | 能 | 会出现 |
| 可重复读 | 事务第一次普通查询 | 不能 | 避免 |

结论：想让事务里前后读到的结果一致，用可重复读；想读到最新已提交的数据，用读已提交。

### 进阶：生成时机的细节（基础薄弱可先跳过）
- 可重复读是「第一次普通查询」才生成，不是 `START TRANSACTION` 的时候；用 `START TRANSACTION WITH CONSISTENT SNAPSHOT` 可以立刻生成。
- 自己事务里改的数据，自己始终看得到，不受读视图影响。
- 当前读和更新语句读的是最新数据，所以可重复读下，更新后再查，可能看到别人已提交的修改。

## 易错点
- 以为可重复读在 `START TRANSACTION` 时就生成读视图；默认是第一次普通查询时才生成
- 以为读已提交不用读视图；它同样用，只是每次重新生成
- 以为可重复读下所有读都读旧数据；当前读读的是最新数据

## 追问
### [f1] 可重复读下，别人提交后我更新同一行会怎样？
更新是当前读，读的是最新已提交的值。更新后这一行成了自己改的版本，自己再查就能看到，即使它是别人提交之后的值。
