---
id: q_01M6XCDKCQJCTDMRE9FM63EQ26
title: 集群节点握手是怎么完成的？
type: concept
difficulty: medium
importance: 1
category: redis
tags: [consensus]
prerequisites: [q_01M6XCDJYKBAEPZKJ9RGXH8599, q_01M6ZYJX0375CC2JW1VEMSFRKQ]
appliesTo: ["Redis >= 3.0"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
节点握手就是让两个集群模式的节点互相认识：对其中一个执行 `CLUSTER MEET`，它们交换几轮消息，之后靠 Gossip 认识所有其他节点。

## 要点
- [kp1|3] 握手由客户端对某个节点执行 `cluster meet ip port` 发起
- [kp2|3] 发起方发 MEET，对方回 PONG，双方互相记下对方
- [kp3|2] 其余节点靠 PING、PONG 里捎带的信息逐步互相认识
- [kp4|2] 新节点只需要 meet 集群里任意一个节点即可
- [kp5] 握手只是组成集群，还没分槽，集群暂时不能服务

## 详解
### 先搞懂：新同学进群，要先加一个好友
好比新同学进了班级微信群：他只要加上班里任意一个同学，群里的人慢慢就都认识他了，不用挨个去加。

Redis 集群的握手也是这样。先说几个词：

- **集群模式节点**：配置里打开了 `cluster-enabled yes` 的实例，普通实例不能握手。
- **集群通信端口**：节点之间专用的端口，和对客户端提供服务的端口不是同一个。
- **Gossip**：节点互相随机交换状态的方式，上一题讲过。

### 握手第一步：客户端发起，两个节点互相确认
假设节点 A 要认识节点 B：

1. 客户端连上 A，执行 `CLUSTER MEET B的ip B的端口`；
2. A 在自己的记录里先给 B 建一条“握手中”的条目，然后向 B 发 MEET 消息；
3. B 收到后，把 A 记到自己的节点列表里，并回复 PONG；
4. A 收到 PONG，知道 B 确实在线，随后向 B 发 PING；B 收到后，握手完成。

之后 A 和 B 就像普通节点一样，定期互相发 PING 和 PONG。

### 握手第二步：靠 Gossip 认识所有人
现在再让 C 去 meet A。A 和 C 握手成功后，A 发给 B 的 PING 里会捎上“我认识 C”。B 收到后发现是个陌生节点，就会主动去和 C 建立连接并握手。

所以 N 个节点不需要两两 meet，每个新节点只 meet 任意一个已经在集群里的节点，剩下的靠 Gossip 自动补全。

### 握手完成之后
此时节点已经组成了集群，但还没有给任何节点分配槽。槽没分完之前，集群不会对外正常提供读写服务。下一步要分配槽，或者给节点配置主从关系。

## 示例
```bash
# 让 7000 认识 7001，再让 7002 也加进来
redis-cli -p 7000 cluster meet 127.0.0.1 7001
redis-cli -p 7000 cluster meet 127.0.0.1 7002
# 稍等片刻，在任意节点上都能看到全部节点
redis-cli -p 7001 cluster nodes
```

## 易错点
- 以为每对节点都要手动 meet 一遍；只需要连到集群里任意一个节点
- 以为 meet 成功集群就能用了；还要分配完槽，集群才能正常服务
- 对没开启集群模式的实例执行 meet，会报错

## 追问
### [f1] 握手时如果 meet 了一个不存在的地址会怎样？
A 会给它建一条握手中的记录，但一直收不到 PONG。握手超时后，这条记录会被清掉，不会成为集群的正式成员。
