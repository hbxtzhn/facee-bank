---
id: q_01M6XCC86NH3XC896A6W9QDAP7
title: MySQL 有哪些日志，各自记录什么？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [database-log]
appliesTo: ["binlog 默认开关：MySQL 5.7 及以前关闭，8.0 起开启"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
MySQL 常见的日志有错误日志、慢查询日志、一般查询日志、binlog 和 redo log，分别记录运行问题、慢 SQL、全部语句、数据修改和页的物理修改。

## 要点
- [kp1|3] 错误日志记录启动、运行、停止过程中的问题
- [kp2|3] 慢查询日志记录超过 `long_query_time` 的 SQL，默认关闭
- [kp3|2] 一般查询日志记录收到的所有语句，量大，默认关闭
- [kp4|2] binlog 记录数据修改，用于恢复和主从复制；redo log 是 InnoDB 的崩溃恢复日志
- [kp5] 排查慢 SQL 时，先打开慢查询日志

## 详解
### 先搞懂：日志就像各种记录本
一家店里有好几本记录本：出问题时记的事故本、专门记办得太慢的业务的登记本、把所有来访者都记下来的流水本、记录每次改账的账本。

MySQL 的日志也是这样，每种日志有自己的用途。

后文用到的术语：

- **慢 SQL**：执行时间超过设定阈值的语句；
- **主从复制**：从库读取主库的日志，让两边数据保持一致；
- **崩溃恢复**：服务异常重启后，把数据恢复到一致的状态。

### 各个日志记录什么
- **错误日志**：记录 MySQL 启动、运行、停止时的错误和警告，服务起不来时先看它。
- **慢查询日志**：记录执行时间超过 `long_query_time` 的 SQL。这个阈值默认是 10 秒，可以调整。默认没有打开，要用 `slow_query_log` 开启。它是找慢 SQL 的主要依据。
- **一般查询日志**：记录客户端的连接和收到的每条语句。量很大，默认关闭，一般只在调试时临时打开。
- **binlog**（二进制日志）：记录对数据的修改，可以把数据恢复到某个时间点，也用于主从复制。5.7 及以前默认关闭，8.0 起默认开启。
- **redo log**：InnoDB 引擎自己的日志，记录数据页做了什么修改，用于崩溃后恢复。

### 开关怎么看
可以用 `SHOW VARIABLES LIKE '...'` 查看对应的参数当前值。

## 示例
```sql
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;
```

## 易错点
- 以为慢查询日志默认就是开着的；默认是关闭的
- 长期开着一般查询日志；它记录所有语句，文件会增长很快，也有性能开销
- 以为 binlog 和 redo log 是同一份日志；一个在 Server 层，一个在 InnoDB 引擎层

## 追问
### [f1] 慢查询日志怎么帮助优化？
开启后，超过阈值的 SQL 会被记录下来。拿这些 SQL 用 `EXPLAIN` 分析执行计划，看有没有走索引，再针对性优化。

### [f2] 还有哪些日志？
还有 undo log，记录修改前的旧值，用于事务回滚和多版本读；以及从库使用的 relay log，保存从主库接收到的 binlog 内容。
