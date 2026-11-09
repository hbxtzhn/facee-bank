---
id: q_01M6ZYJKEHVRZX1GW646T1F4FK
title: 一条 UPDATE 语句在 InnoDB 里是怎么执行的？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [database-log, query-execution]
appliesTo: ["MySQL >= 5.7，InnoDB"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
执行器先让 InnoDB 取出那一行，改好值后再让引擎写入内存并记 redo log（prepare 状态），接着写 binlog，最后提交 redo log。

## 要点
- [kp1|3] 执行器先通过引擎取出要改的行，数据页不在内存就先从磁盘读入
- [kp2|3] 引擎把新值写入内存里的数据页，同时记 redo log，状态是 prepare
- [kp3|2] 执行器再写 binlog，随后调用引擎把 redo log 改成 commit
- [kp4|2] 数据页先改在内存，之后再异步刷回磁盘，不在提交时同步写
- [kp5] 修改前的旧值会记入 undo log，用于回滚

## 详解
### 先搞懂：改一条数据，不会立刻写磁盘
执行 `UPDATE t SET n = n + 1 WHERE id = 2` 时，数据库不会马上去改磁盘文件，因为磁盘读写慢。

可以把它想成店员记账。先在草稿上改（内存里的数据页）。同时在施工单上写好改了什么（redo log）。再向店长汇报（binlog）。最后两边确认。真正誊写到正式账本（刷盘）稍后再做。

后文用到的术语：

- **数据页**：InnoDB 读写数据的最小单位，一页里有多行数据；
- **内存里的数据页**：缓冲池中的数据页，改它不用立刻写磁盘；
- **prepare、commit**：redo log 的两种状态，先 prepare，最后 commit。

### 执行流程：按顺序走
1. **取行**：执行器通过引擎，按主键找到 `id = 2` 这一行。如果所在数据页已在内存，直接返回；否则先从磁盘读进内存。
2. **改值**：执行器拿到这一行，把值加 1，得到新的一行数据，再调用引擎接口写入。
3. **写内存和 redo log**：引擎把新数据更新到内存里的数据页，同时把这次修改记进 redo log，状态是 prepare。
4. **写 binlog**：执行器生成这次操作的 binlog，写入磁盘。
5. **提交**：执行器调用引擎的提交接口，引擎把刚才的 redo log 改为 commit 状态，更新完成。

### 为什么后面才刷数据页
修改先在内存里完成，并有 redo log 保底。即使此时宕机，重启后也能根据 redo log 把数据重做出来。真正把数据页写回磁盘，由后台线程在合适的时机完成。

### 两个 log 的写入顺序
redo log 分成 prepare 和 commit 两步，中间夹着 binlog，这样做是为了让两份日志保持一致，详见两阶段提交那一题。

## 易错点
- 以为 UPDATE 一执行完，数据就已经写进磁盘数据文件；实际上先改内存，数据页后刷盘
- 以为只写 redo log 就够了；还要写 binlog，两者提交时要保持一致
- 以为 redo log 是一次写完；它先写 prepare，写完 binlog 后才写 commit

## 追问
### [f1] 更新时数据页不在内存怎么办？
先从磁盘把对应的数据页读进内存缓冲池，再在内存中修改，所以第一次修改可能比较慢。

### [f2] 旧值存在哪里，方便回滚？
存在 undo log 里。事务回滚时，InnoDB 用 undo log 把数据恢复成修改前的样子。
