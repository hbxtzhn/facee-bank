---
id: q_01M6ZYJQZP25XSHJ9113H7W05Q
title: RDB 的 bgsave 是怎么在后台生成快照的？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [rdb-aof, process]
prerequisites: [q_01M6XCCZGCKXXDHDXDG74RXCVD, q_01M6XCCZS9XZ69NDV5RERDGZYH]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Redis 文档：Redis persistence（Snapshotting 与 fork）", url: "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/" }
  - { title: "Redis 文档：BGSAVE", url: "https://redis.io/docs/latest/commands/bgsave/" }
  - { title: "Redis 文档：Redis administration（透明大页、最多 2 倍内存）", url: "https://redis.io/docs/latest/operate/oss_and_stack/management/admin/" }
estimatedMinutes: 3
---

## 一句话
bgsave 先 fork 出一个子进程，子进程拿着 fork 那一刻的数据遍历并写入 RDB 文件，父进程继续处理读写请求，互不阻塞。

## 要点
- [kp1|3] bgsave 靠 fork 子进程生成快照，主进程不用自己写文件
- [kp2|3] 子进程看到的是 fork 那一刻的数据，之后的修改不会进入这次快照
- [kp3|2] 父子进程先共享内存，父进程改某块数据时才复制那一块
- [kp4] fork 本身会短暂阻塞主进程，数据量越大阻塞越久
- [kp5] 先写临时文件，写完再替换旧的 dump.rdb

## 详解
### 先搞懂：拍照时别让人乱动
给一屋子人拍合影，要的是“某一瞬间”的样子。如果一边拍一边有人走动，照片就乱了。

bgsave 的办法是先把这一瞬间“定格”。也就是 fork 出子进程，它看到的数据固定不变。然后子进程慢慢冲洗照片，也就是写文件。与此同时，屋里的人（客户端请求）照常活动。

后文用到的词：
- **fork**：复制出一个内容相同的子进程。
- **写时复制**：父子共用内存，谁要修改某一块，才把这一块复制出来。

### bgsave 的执行过程
1. 客户端发送 `bgsave`，或者自动触发条件满足。
2. 如果已经有子进程在做 RDB 或 AOF 重写，就不会重复启动。
3. 主进程调用 fork 创建子进程。fork 的这一小段时间，主进程是被阻塞的。
4. fork 完成后，主进程立刻回去处理客户端请求。
5. 子进程遍历内存里的数据，写入一个临时 RDB 文件。
6. 写完后，用临时文件替换旧的 dump.rdb，子进程退出。

### 为什么快照是一致的
子进程拿到的是 fork 那一刻的数据视图。之后主进程再修改数据，操作系统会把被改的那一块内存复制一份给主进程，子进程看到的还是旧的。所以快照里不会出现“一半新一半旧”的情况。

### 它有什么代价
- **fork 阻塞**：fork 要复制内存的页表（记录内存地址映射的表），实例越大越慢，期间主进程不能处理请求。
- **内存增长**：快照期间写得越多，被复制的内存页越多，占用内存会上涨。最坏情况下可能接近翻倍，所以要给机器留足内存。
- **磁盘压力**：子进程大量写磁盘，可能影响同机其他服务。

### 进阶：要不要关透明大页（基础薄弱可先跳过）
Linux 的透明大页会让内存页变大，写时复制一次复制的内容更多，延迟会变差。Redis 官方建议关闭透明大页。

## 示例
```bash
redis-cli bgsave
# 返回 Background saving started
redis-cli info persistence   # 查看 rdb_bgsave_in_progress 等状态
```

## 易错点
- 以为 bgsave 完全不阻塞；fork 那一刻主进程会短暂卡住
- 以为快照里包含 bgsave 期间的写入；那些修改只在主进程里，要等下一次快照
- 以为 fork 会立刻把内存整个复制一遍；实际是写时复制，只复制被修改的部分

## 追问
### [f1] bgsave 期间 Redis 宕机，数据会怎样？
新快照还没写完，旧的 dump.rdb 不会被替换，所以文件不会损坏。但从上次快照到宕机之间的修改会丢失。
