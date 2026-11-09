---
id: q_01M6XCD7M0V1VRPJCFSB1451Z1
title: canal 是怎么通过 binlog 更新缓存的？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [cache-consistency, database-log]
prerequisites: [q_01M6XCC8EV6YCRMCP3358H90ST, q_01M6ZYJTQVAQ7HWT9GS31BX2VC]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
canal 伪装成 MySQL 的从库去读取 binlog，解析出数据变更后再更新缓存，业务代码完全不用改。

## 要点
- [kp1|3] canal 模拟 MySQL 从库，向主库请求 binlog
- [kp2|3] binlog 记录了数据库的所有增删改，canal 解析成变更事件
- [kp3|2] 拿到变更事件后，由下游程序更新或删除 Redis 缓存
- [kp4|2] 对业务代码无侵入，也不会漏掉任何一次数据库修改
- [kp5] 缓存是异步更新的，只保证最终一致

## 详解
### 先搞懂：不用你汇报，我直接看监控
想知道办公室的东西谁动过，一种办法是每个同事动完都来汇报一声，但总有人忘。另一种办法是在办公室装一个监控，谁动了都被记录，你不需要同事配合。

canal 就是这个监控。业务代码改数据库，不用管缓存，canal 在后面盯着数据库的变化，发现变化就去更新缓存。

后文用到的术语：

- **binlog**：MySQL 的二进制日志，记录所有数据变更。
- **主从复制**：从库读取主库的 binlog，并重放，保持数据一致。
- **canal**：阿里开源的组件，用来订阅 MySQL 的 binlog。

### canal 怎么工作
1. canal 向 MySQL 主库发送请求，假装自己是一个从库。
2. MySQL 主库就像对待普通从库一样，把 binlog 推送给 canal。
3. canal 解析 binlog，得到哪张表、哪一行、改成了什么。
4. canal 把变更事件交给下游。下游可以是自己写的程序，也可以先发到消息队列。
5. 下游程序根据变更事件，删除或更新 Redis 里对应的缓存。

### 为什么这个方案很好用
- **无侵入**：业务代码只管写数据库。
- **不漏**：只要数据库变了，binlog 就有记录，不会像手动发消息那样可能忘记。
- **解耦**：缓存更新逻辑独立成一个服务。

### 需要注意的地方
- 缓存更新是异步的，数据库改完到缓存更新之间有延迟。
- 要开启 MySQL 的 binlog，格式需要是 ROW，才能拿到每行的具体变化。
- canal 本身要部署和维护，需要考虑它宕机后从上次位点继续读取。
- 消费端要处理重复和顺序问题，保证幂等。

## 易错点
- 以为 canal 是业务代码里的一个工具类；它是独立运行的服务
- 以为 canal 能保证实时强一致；它是异步订阅，有延迟
- 忘记开启 binlog，或者格式不对；canal 就拿不到行级变化

## 追问
### [f1] canal 会给 MySQL 带来很大压力吗？
它和一个普通从库类似，只是读取 binlog，压力主要是 binlog 的发送。对库的影响通常有限，但从库数量很多时，也要留意主库的网络负载。

### [f2] canal 和用 MQ 在业务里发消息哪个好？
canal 无侵入、不漏变更，适合对一致性要求较高的场景，但需要额外部署。MQ 简单直接，但依赖业务代码主动发送。
