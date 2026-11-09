---
id: q_01M6XCDJYKBAEPZKJ9RGXH8599
title: Redis 集群至少要几个节点，怎么开启集群模式？
type: concept
difficulty: easy
importance: 1
category: redis
tags: [sharding]
appliesTo: ["Redis >= 3.0"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
每个节点配置 `cluster-enabled yes` 开启集群模式；一个带高可用的集群至少要 6 个节点，也就是 3 个主节点各带 1 个从节点。

## 要点
- [kp1|3] 每个节点的配置文件里加 `cluster-enabled yes`
- [kp2|3] 集群至少 3 个主节点，才能完成多数派的选举
- [kp3|2] 每个主节点配 1 个从节点，所以高可用集群最少 6 个节点
- [kp4|2] 节点启动后，用 `redis-cli --cluster create` 组建集群
- [kp5] 节点之间还需要开放集群总线端口，默认是服务端口加 10000

## 详解
### 先搞懂：三家店，各配一个替补
一个有故障保护的连锁店，至少要三家主店：这样一家出问题，另外两家还占多数，可以做决定选新店长。每家主店再配一个替补，所以最少 6 个人。

后文用到的词：

- **集群模式**：节点启动时按集群方式运行，而不是普通单机。
- **集群总线**：节点之间互相通信用的端口。

### 为什么至少 3 个主节点
故障判定和选举都要超过半数的主节点同意。只有 1 个或 2 个主节点，一旦坏一个就凑不成多数。所以最小的可用集群是 3 个主节点。

### 为什么常说 6 个节点
只有 3 个主节点、没有从节点，其中一个主节点挂了，它负责的槽没人接管，集群就不可用。每个主节点配 1 个从节点，才能实现自动故障转移，因此是 3 主 3 从共 6 个节点。

### 怎么开启集群模式
每个节点的 `redis.conf` 里至少要有：

- `cluster-enabled yes`：开启集群模式；
- `cluster-config-file`：节点保存集群状态的文件，由 Redis 自己维护；
- `cluster-node-timeout`：判定节点失联的超时时间。

### 组建集群
6 个节点都启动之后，用命令把它们连成集群，并给每个主节点配 1 个从节点。命令会自动分配槽、分配主从。

## 示例
```bash
# redis.conf（每个节点，端口不同）
# port 7000
# cluster-enabled yes
# cluster-config-file nodes-7000.conf
# cluster-node-timeout 5000

# 6 个节点启动后，组建集群：3 主，每主 1 从
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

## 易错点
- 以为 3 个节点就是完整高可用集群；没有从节点，主节点故障无法替换
- 只改 cluster-enabled 就以为集群建好了；还要执行创建命令分配槽
- 防火墙只开服务端口；集群总线端口也要放行
- 把 `cluster-config-file` 当成要手动编辑的配置；它由 Redis 自己维护

## 追问
### [f1] 集群创建完，怎么检查状态？
用 `redis-cli --cluster check` 检查槽覆盖和节点状态，或用 `CLUSTER INFO` 查看集群是否正常。`cluster_state:ok` 表示所有槽都有节点负责。
