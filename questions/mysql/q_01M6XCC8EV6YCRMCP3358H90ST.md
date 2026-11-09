---
id: q_01M6XCC8EV6YCRMCP3358H90ST
title: binlog 是什么，有什么用？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [database-log, replication]
appliesTo: ["binlog 默认开关：MySQL 5.7 及以前关闭，8.0 起开启"]
references:
  - { title: "MySQL 8.0 手册：The Binary Log", url: "https://dev.mysql.com/doc/refman/8.0/en/binary-log.html" }
  - { title: "MySQL 8.4 手册：The Binary Log", url: "https://dev.mysql.com/doc/refman/8.4/en/binary-log.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
binlog 是 MySQL Server 层记录数据修改的日志，用来把数据恢复到某个时间点，以及让从库同步主库的数据。

## 要点
- [kp1|3] binlog 记录数据的修改操作，属于逻辑日志，由 Server 层写入
- [kp2|3] 用途一：基于备份加 binlog，恢复到某个时间点
- [kp3|2] 用途二：从库读取主库 binlog 并重放，实现主从复制
- [kp4] 5.7 及以前默认没开，要在配置文件里启用；8.0 起默认开启

## 详解
### 先搞懂：binlog 就像一本账本的修改记录
想象一本账本，每次改账都在另一个本子上记「把某账户加了 100」。这个本子有两个用处：

- 账本丢了，用上个月的备份，再照着本子一条条重做，就能恢复到出事前；
- 分店照着总店的本子重做，就能和总店的账一致。

binlog 就是这个记录本，它记的是「做了什么修改」，而不是某个磁盘位置上的变化，所以叫逻辑日志。

后文用到的术语：

- **主库、从库**：写入数据的库和跟着它同步的库；
- **时间点恢复**：先还原备份，再按顺序重放 binlog，直到指定的时间。

### 它记什么
所有引擎的数据修改操作（增、删、改，以及建表等 DDL）都会记进 binlog，查询语句不记。它有几种记录格式，如 `ROW` 记录每一行的变化，`STATEMENT` 记录 SQL 原文。

### 两个用途
1. **数据恢复**：误删数据后，先还原最近一次备份，再重放备份之后的 binlog，可以恢复到指定时间点。
2. **主从复制**：主库把修改写进 binlog；从库读取它，在自己这里重放一遍，两边数据就保持同步。

### 怎么开启
MySQL 5.7 及以前默认没有启用，需要在配置文件里设置 `log_bin`。8.0 起默认已开启。

## 示例
```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW BINARY LOGS;
```

## 易错点
- 以为 binlog 只记 InnoDB 的数据；它在 Server 层，所有引擎的修改都会记
- 以为 binlog 是物理日志；它是逻辑日志，记录的是修改操作
- 以为 binlog 能代替备份；它只是备份之后的增量记录，恢复需要先有备份

## 追问
### [f1] binlog 和 redo log 的最大区别是什么？
binlog 在 Server 层，所有引擎都有，记逻辑修改，用于恢复和复制。redo log 只属于 InnoDB，记页的物理修改，用于崩溃恢复。

### [f2] 怎么在 binlog 里找一次误操作？
可以用 `mysqlbinlog` 工具查看日志内容，按时间或位置范围找到误操作，再恢复到它之前的状态。
