---
id: q_01M6XCD2F6PKVYDCZ7CMD9JVW3
title: Redis 重启时怎么恢复数据？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [rdb-aof]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
把 RDB 或 AOF 文件放到 Redis 数据目录，再启动 redis-server 就能恢复；开启了 AOF 就优先加载 AOF，否则加载 RDB。

## 要点
- [kp1|3] 恢复方法：把持久化文件放进数据目录，启动 redis-server
- [kp2|3] 开启 AOF 且有 AOF 文件，优先加载 AOF
- [kp3|2] AOF 关闭或没有 AOF 文件，加载 RDB
- [kp4] 想用 AOF 恢复，配置里要先开启 `appendonly yes`

## 详解
### 先搞懂：重启后到哪里找存档
游戏重启后，会先找最新的存档读取。Redis 也是：启动时去数据目录找持久化文件，找到就读进内存，数据就回来了。

后文用到的词：
- **数据目录**：配置项 `dir` 指定的目录，持久化文件默认放在这里。
- **加载**：启动时把文件内容读入内存。

### 恢复步骤
1. 停止 Redis（如果在运行）。
2. 把 RDB 文件（默认 dump.rdb）或 AOF 文件，放到配置里 `dir` 指定的数据目录。
3. 如果要用 AOF 恢复，在配置里开启 `appendonly yes`。
4. 启动 redis-server，它会自动加载文件。
5. 加载完成后 Redis 启动成功，可以用 `DBSIZE` 或查几个 key 来检查数据是否回来。

### 启动时选哪个文件
- AOF 已开启并且存在 AOF 文件：加载 AOF；
- AOF 没开，或没有 AOF 文件：加载 RDB。

原因是 AOF 通常比 RDB 保存的数据更完整，所以两者都在时以 AOF 为准。

### 常见坑
- **AOF 开关没开**：只放了 AOF 文件但没配置 `appendonly yes`，Redis 会去加载 RDB，数据看起来不对。
- **目录和文件名不对**：文件要放在 `dir` 指定的目录，并和配置的文件名一致。
- **文件损坏**：加载时报错，可以用 `redis-check-aof` 或 `redis-check-rdb` 检查和修复，先备份原文件。

## 示例
```bash
cp dump.rdb /var/lib/redis/dump.rdb
redis-server /etc/redis/redis.conf
redis-cli dbsize
```

## 易错点
- 以为 AOF 文件存在就一定用它；AOF 开关没开时不会加载
- 以为需要执行专门的“恢复命令”；放好文件、启动服务即可
- 以为两个文件会合并加载；只会选其中一个

## 追问
### [f1] 如何用 RDB 恢复，但机器上还留着 AOF 文件？
把配置里的 `appendonly` 设为 no 再启动，Redis 就会加载 RDB。若保持开启，会优先加载 AOF。
