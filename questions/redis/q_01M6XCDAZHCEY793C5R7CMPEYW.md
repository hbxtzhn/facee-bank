---
id: q_01M6XCDAZHCEY793C5R7CMPEYW
title: Redis 内存满了会发生什么？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [replacement-policy]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
内存达到 maxmemory 上限后，Redis 会按淘汰策略删 key 腾空间；默认的 noeviction 不删，直接拒绝会占内存的写命令。

## 要点
- [kp1|3] `maxmemory` 设置 Redis 能用的内存上限，达到后触发淘汰
- [kp2|3] 默认策略 noeviction：不淘汰，新增数据的写命令返回错误
- [kp3|2] 其他策略会按规则删除 key 腾出空间，再继续处理写入
- [kp4] 读命令和删除命令在 noeviction 下仍然可用

## 详解
### 先搞懂：内存是有限的
你把 Redis 当缓存用，每天都写入新数据。服务器内存是固定的，写着写着就满了。

可以想成一个衣柜：塞满之后，要么拒绝买新衣服，要么先扔几件旧的。Redis 把这两个选择都提供了，靠淘汰策略决定怎么选。

后文用到几个词：

- **maxmemory**：配置项，限制 Redis 最多用多少内存。
- **淘汰策略**：内存满了之后，怎么选要删的 key。

### 没设 maxmemory 会怎样
在 64 位系统上，`maxmemory` 默认是 0，表示不限制。Redis 会一直用内存，直到被操作系统杀掉，或者触发系统换页，性能急剧下降。所以生产环境一般都要设置上限。

### 设了 maxmemory，满了之后
每次处理命令前，Redis 会检查内存是否超限。超了就按 `maxmemory-policy` 配置的策略处理：

- **noeviction**（默认）：不删任何 key。会让内存增加的写命令，比如 `SET`，会返回 OOM 错误；`GET` 和 `DEL` 这类命令仍可正常执行。
- **其他策略**：先按规则淘汰一批 key，腾出空间再执行写命令。比如 `allkeys-lru` 淘汰最久没用的 key。

### 怎么选
- 当缓存用：通常选 `allkeys-lru` 或 `allkeys-lfu`，旧数据自动让位给新数据。
- 当数据库用，不能丢数据：保持 `noeviction`，让应用收到错误后自己处理，并及时扩容。

具体策略见“Redis 有哪几种淘汰策略”那道题。

## 示例
```bash
# 限制最多使用 100MB，内存满后淘汰最近最少使用的 key
CONFIG SET maxmemory 100mb
CONFIG SET maxmemory-policy allkeys-lru
```

## 易错点
- 以为内存满了 Redis 会自动删旧数据；默认策略是不删，直接报错
- 以为不设 maxmemory 也安全；没有上限时可能把整台机器内存吃光
- 以为 noeviction 下所有命令都失败；读和删除仍然可用

## 追问
### [f1] 内存满了，业务写入报 OOM 错误，怎么办？
先确认是缓存还是主存储。缓存可改成 `allkeys-lru`；主存储则应扩容或清理数据，并排查大 key 等占用内存的原因。
