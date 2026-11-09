---
id: q_01M6ZYJM0EC7H97EWCA4CVPE3X
title: redo log 什么时候刷入磁盘？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [database-log, flush-to-disk]
prerequisites: [q_01M6XCC9C3ZNX81PD178JMN9JH]
appliesTo: ["MySQL >= 5.7，InnoDB"]
references:
  - { title: "MySQL 8.4 手册：InnoDB 启动选项与系统变量 innodb_flush_log_at_trx_commit", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit" }
  - { title: "MySQL 8.4 手册：Redo Log Buffer", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log-buffer.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
redo log 先写进内存中的 log buffer，再在事务提交、buffer 不够用和后台定时等时机刷到磁盘；提交时是否刷盘由 `innodb_flush_log_at_trx_commit` 控制。

## 要点
- [kp1|3] redo log 先写进内存的 log buffer，不是直接写磁盘
- [kp2|3] 提交时是否刷盘由 `innodb_flush_log_at_trx_commit` 决定，默认 1 每次都刷
- [kp3|2] log buffer 空间不足时，会把内容刷到磁盘
- [kp4|2] 后台线程大约每秒刷一次
- [kp5] 取值 0、2 提交更快，但宕机时可能丢最近一段时间的事务

## 详解
### 先搞懂：先放在桌上，攒一批再送去仓库
店员把施工单先放在桌上（log buffer），攒到一定量或到点了，再统一送去仓库归档（磁盘）。送去的时机，就是刷盘的时机。

放桌上很快，但如果这时停电，桌上的单子就没了；送到仓库更安全，但每次都跑一趟也慢。

后文用到的术语：

- **log buffer**：内存中的 redo log 缓冲区；
- **刷盘**：把 log buffer 中的内容写入磁盘并确保落实；
- **操作系统缓存**：写文件时，系统先放进自己的内存缓存，不一定马上到磁盘。

### 刷盘的几个时机
1. **log buffer 空间不足**：缓冲区大小有限，装不下大事务时，会提前把一部分写到磁盘。
2. **事务提交**：这是最重要的时机，由参数控制，见下节。
3. **后台线程定时**：有后台线程大约每秒把 log buffer 的内容刷盘一次。

### 提交时的三种策略：innodb_flush_log_at_trx_commit
- **1（默认）**：每次提交，都把 redo log 写入磁盘并确保落实。最安全，已提交的事务宕机后不丢。
- **0**：提交时什么也不做，由后台线程每秒刷盘。MySQL 进程崩溃就可能丢最近约一秒的事务。
- **2**：提交时写到操作系统缓存，由系统和后台刷到磁盘。MySQL 进程崩溃不丢，但操作系统宕机或断电可能丢最近的事务。

对数据可靠性要求高的业务，用默认值 1。

## 示例
```sql
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
SHOW VARIABLES LIKE 'innodb_log_buffer_size';
```

## 易错点
- 以为 redo log 一写就在磁盘上；它先在 log buffer，要刷盘才算落实
- 以为设成 0 或 2 只会让速度更快；代价是宕机时可能丢最近的已提交事务
- 以为事务提交一定会刷盘；是否刷盘取决于这个参数的取值

## 追问
### [f1] 为什么有的场景会把参数设成 2？
对丢最近一小段数据不敏感、更看重写入速度的场景可以考虑。但操作系统宕机时会丢数据，金融类业务不要这样用。

### [f2] 刷的是 redo log，还是数据页？
这里说的是 redo log。数据页由别的机制异步刷盘，两者不是一回事。
