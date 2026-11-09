---
id: q_01M6XCD1XT65RZKZK06W1W01YF
title: AOF 的三种同步策略怎么选？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [rdb-aof, flush-to-disk]
prerequisites: [q_01M6XCD0Q3ZE619GDN2DV7NSX8, q_01M6ZYJRH9251PJD5G9GMN6P4P]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
大多数场景选默认的 everysec，每秒同步一次，最多丢约 1 秒；always 最安全但最慢，no 最快但可靠性最差。

## 要点
- [kp1|3] always：每条写命令都 fsync，几乎不丢数据，但吞吐最低
- [kp2|3] everysec：每秒 fsync 一次，是默认策略，宕机最多丢约 1 秒
- [kp3|2] no：Redis 不主动 fsync，何时落盘由操作系统决定
- [kp4] 配置项是 `appendfsync`，需要先开启 `appendonly yes`

## 详解
### 先搞懂：每笔都盖章，还是下班统一盖
店里收银，每收一笔就去银行存一次（always），最安全但跑断腿；每天下班存一次（everysec 类似按固定间隔），折中；完全不管，等银行收款车来取（no），最省事但钱放在店里时可能出事。三种策略就是在“安全”和“速度”之间取舍。

后文用到的词：
- **fsync**：要求操作系统把缓存里的数据写到磁盘。
- **宕机**：服务器断电、系统崩溃等意外停机。

### always：每条都同步
每执行一条写命令，就把它写入 AOF 文件并 fsync，成功后再返回给客户端。宕机时基本只会丢还没执行完的那一条。代价是每次写都要等磁盘，写入吞吐受磁盘速度限制。

### everysec：每秒同步一次
命令先写入文件，由后台线程每秒做一次 fsync。性能接近不开 AOF 的水平，宕机最多丢约 1 秒的数据。这是默认值，也是大多数业务的选择。

### no：交给操作系统
Redis 只负责把数据 write 给操作系统，不主动 fsync。什么时候落盘由操作系统决定，宕机时可能丢多久的数据不好估计，取决于系统策略。

### 方案对比：三种同步策略
| 策略 | 同步时机 | 宕机丢多少 | 性能 | 适合 |
|---|---|---|---|---|
| `always` | 每条写命令 | 几乎不丢 | 最低 | 数据不能丢，可接受低吞吐 |
| `everysec` | 每秒一次 | 最多约 1 秒 | 较好 | 大多数业务（默认） |
| `no` | 操作系统决定 | 不确定，可能较多 | 最好 | 数据可重建，追求速度 |

结论：默认用 everysec；金融类等不能丢数据的场景再考虑 always，并评估磁盘性能；数据能重建时才用 no。

## 示例
```conf
appendonly yes
appendfsync everysec
```

## 易错点
- 以为 everysec 一点不丢；最多约丢 1 秒的数据
- 以为 always 绝对不会丢；硬件缓存等因素下，仍取决于磁盘是否真正落盘
- 以为 `appendfsync` 单独配置就生效；还要开启 AOF

## 追问
### [f1] everysec 下磁盘很慢时会怎样？
后台 fsync 变慢时，主线程写文件可能被拖慢，极端情况下丢失的数据会超过 1 秒。所以磁盘性能也要监控。
