---
id: q_01M6XCC8PQVZ7ZQJ1Z1WDT0Y0S
title: binlog 和 redo log 有什么区别？
type: concept
difficulty: medium
importance: 3
category: mysql
tags: [database-log, replication]
prerequisites: [q_01M6XCC86NH3XC896A6W9QDAP7, q_01M6XCC8EV6YCRMCP3358H90ST]
appliesTo: ["MySQL >= 5.7，InnoDB"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
binlog 是 Server 层的逻辑日志，所有引擎都有，追加写，用于恢复和复制；redo log 是 InnoDB 的物理日志，循环写，用于崩溃恢复。

## 要点
- [kp1|3] 层次不同：binlog 属于 Server 层，redo log 只属于 InnoDB
- [kp2|3] 内容不同：binlog 记逻辑修改，redo log 记数据页上的物理修改
- [kp3|2] 写入方式不同：binlog 追加写、写满换文件，redo log 固定大小循环写
- [kp4|2] 时机不同：redo log 事务执行中不断写，binlog 在事务提交时写
- [kp5] 用途不同：binlog 用于恢复和复制，redo log 用于崩溃恢复

## 详解
### 先搞懂：两本账，各管各的事
想象一家商店有两本记录：

- 店长的账本（binlog）：用文字记「把 5 号商品库存减 1」，所有分店都能照着做；
- 仓库的施工单（redo log）：只有本仓库用，记「某个货架的某个位置改成了什么」，停电后靠它把货架恢复原样。

两本都在记「改了什么」，但记法、用途、所在位置都不一样。

后文用到的术语：

- **逻辑日志**：记录 SQL 语义层面的修改；
- **物理日志**：记录某个数据页上具体改了什么；
- **崩溃恢复**：服务异常退出后，把已提交的修改找回来。

### 方案对比：binlog 和 redo log
| 对比项 | binlog | redo log |
|---|---|---|
| 所属层次 | Server 层，所有引擎都有 | InnoDB 引擎层 |
| 记录内容 | 逻辑日志，记录修改操作 | 物理日志，记录数据页的修改 |
| 写入方式 | 追加写，写满切换新文件 | 固定大小，循环写，旧内容会被覆盖 |
| 写入时机 | 事务提交时写入 | 事务执行过程中持续写 |
| 主要用途 | 时间点恢复、主从复制 | 崩溃恢复 |

结论：两者缺一不可，崩溃恢复靠 redo log，备份恢复和复制靠 binlog；InnoDB 在提交事务时会让两者保持一致。

### 为什么 redo log 要循环写
redo log 的作用是崩溃恢复，已经把修改刷到数据文件里的那部分，就不再需要了，可以被覆盖。所以它是固定大小，写到末尾回到开头继续写。

### 为什么 binlog 不能替代 redo log
binlog 记录的是逻辑修改，没有记录哪些修改已经落到数据页上，难以直接用来做 InnoDB 的崩溃恢复。而 binlog 追加写、不会覆盖，适合保存完整的历史，用来做备份恢复。

## 易错点
- 以为 binlog 只有 InnoDB 才有；它是 Server 层的，MyISAM 也会记
- 以为 redo log 能无限保存历史；它循环写，旧内容会被覆盖
- 以为两本日志是各写各的；InnoDB 用两阶段提交，让两份日志在提交时保持一致

## 追问
### [f1] 只有 redo log，没有 binlog，行不行？
单机崩溃恢复可以。但没有 binlog 就做不了主从复制和基于 binlog 的时间点恢复。

### [f2] 为什么说 redo log 保证了 crash-safe？
修改先记 redo log，再慢慢刷到数据文件。宕机后，用 redo log 里已提交的记录重做一遍，已提交的数据就不会丢。
