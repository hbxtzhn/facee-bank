---
id: q_01M6XCD17XHEJG8HTX5SX4VRSY
title: bgrewriteaof 是怎么重写 AOF 文件的？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [rdb-aof, process]
prerequisites: [q_01M6XCD0Q3ZE619GDN2DV7NSX8, q_01M6XCD0ZB37G4R8HAKH506V14]
appliesTo: ["Redis >= 7.0 的 multi part AOF 部分"]
references:
  - { title: "Redis 文档：Redis persistence（RDB / AOF / Log rewriting / How durable is the append only file）", url: "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
bgrewriteaof 由子进程根据 fork 时的内存数据，在后台生成一份最少命令的新 AOF；重写期间的新写入也会被记录，最后保证新文件不缺数据。

## 要点
- [kp1|3] 重写由 fork 出的子进程在后台完成，主进程继续处理请求
- [kp2|3] 子进程按内存数据生成精简命令，不是读旧 AOF 文件
- [kp3|2] 重写期间主进程的新写命令也要保留，防止新文件丢数据
- [kp4] 7.0 之前靠重写缓冲区补齐增量，7.0 起改为多文件结构

## 详解
### 先搞懂：边搬家边收快递
你在整理旧账本、誊抄一份精简版（子进程重写）。誊抄期间，又有新的收支要记。如果只把精简版交上去，这期间新记的账就丢了。所以得另外把新账也记下来，等精简版完成后，把新账接在后面。

后文用到的词：
- **AOF 重写**：生成一份等效但更小的 AOF。
- **增量写入**：重写期间主进程继续收到的新写命令。

### 重写的基本过程
1. 执行 `bgrewriteaof`，或自动触发条件满足。
2. 主进程 fork 子进程，之后继续处理客户端请求。
3. 子进程遍历 fork 时刻的内存数据，为每个 key 生成还原命令，写入临时的新文件。
4. 子进程写完后，新旧文件切换，旧文件被删除。

### 重写期间的新写入怎么办
子进程只看得到 fork 时的数据，之后的修改它不知道。所以主进程要把这期间的新写命令也留住，重写完后补到新文件里，不然切换之后就会丢这一段数据。

- **7.0 之前**：主进程把新命令同时写进旧 AOF 和一个“重写缓冲区”。子进程结束后，主进程把缓冲区的内容追加到新文件，再切换。
- **7.0 起**：AOF 拆成多个文件：一个基础文件（重写产物）加若干增量文件。重写开始时，主进程就开一个新的增量文件记录后续写入，子进程只生成新的基础文件，最后更新清单文件把它们组合起来。

### 为什么这样设计
让子进程干重活，主进程不卡；用增量记录补上空档，保证不丢数据；最后一步切换文件很快，失败也不会破坏旧文件。

### 进阶：7.0 的文件长什么样（基础薄弱可先跳过）
7.0 起 AOF 文件放在 `appendonlydir` 目录里，包含基础文件、增量文件和一个清单文件，用清单文件来记录当前有效的文件。这样不再需要重写缓冲区，也避免了一次大的合并写入。

## 示例
```bash
redis-cli bgrewriteaof
redis-cli info persistence   # 查看 aof_rewrite_in_progress
```

## 易错点
- 以为重写是读旧 AOF 压缩；实际读的是内存里的当前数据
- 以为重写期间的新写入会丢；有增量记录保证补上
- 以为重写完全不阻塞；fork 时主进程也会短暂阻塞

## 追问
### [f1] 重写失败了旧 AOF 还能用吗？
能。新文件是单独生成的，只有成功才会替换旧文件，失败则保留旧文件继续使用。
