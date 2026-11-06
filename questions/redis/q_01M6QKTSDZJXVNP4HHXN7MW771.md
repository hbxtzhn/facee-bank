---
id: q_01M6QKTSDZJXVNP4HHXN7MW771
title: Redis 过期 key 是怎么被删除的？
type: concept
difficulty: medium
importance: 3
category: redis
tags: [redis, memory]
prerequisites: [q_01M6QN33W7DGDKRD07W2A60P8T]
appliesTo: ["Redis >= 6.0"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Redis 源码 src/expire.c（activeExpireCycle）", url: "https://github.com/redis/redis/blob/unstable/src/expire.c" }
  - { title: "Redis 5.0 源码 src/expire.c（旧版随机抽样）", url: "https://github.com/redis/redis/blob/5.0/src/expire.c" }
  - { title: "redis.conf（hz、active-expire-effort、maxmemory-policy、lazyfree）", url: "https://github.com/redis/redis/blob/unstable/redis.conf" }
  - { title: "Redis 文档：Replication · How Redis replication deals with expires on keys", url: "https://redis.io/docs/latest/operate/oss_and_stack/management/replication/" }
reviewedAt: 2026-11-06
estimatedMinutes: 4
---

## 一句话
Redis 同时用惰性删除和定期删除：访问 key 时检查是否过期，后台再按周期抽查删除；两者都没清掉的，只能靠内存淘汰策略处理。

## 要点
- [kp1|3] 惰性删除：读写 key 前先检查是否过期，过期就删掉
- [kp2|3] 定期删除：serverCron 按 hz（默认 10）周期抽查过期字典
- [kp3|2] 每批抽查 20 个，过期比例超过 10% 就再抽一批
- [kp4|2] 单轮有时间上限，约占 CPU 时间的 25%
- [kp5] 从节点不主动删过期 key，等主节点传播 DEL

## 详解
### 先搞懂：key 过期了为什么不会马上消失
用 `EXPIRE key 60` 给 key 设过期时间，Redis 只是记下「什么时候到期」，到点那一刻并不会立刻去删。原因是 Redis 用一个主线程处理所有命令，如果要盯着成千上万个 key 准点删除，正常请求就没空处理了。

所以 Redis 用两种「不准时、但够用」的办法。可以类比冰箱里的食品：

- **惰性删除**：拿出来吃之前看一眼保质期，过期就扔；
- **定期删除**：每隔一会儿随手翻几样检查，过期的扔掉。

后面会用到的几个词：

- **过期字典**：Redis 专门记录「哪些 key 设了过期时间、几点到期」的一张表。检查过期只查这张表，不用翻全部数据。
- **serverCron**：Redis 内部的定时任务，周期性地做各种后台工作，清理过期 key 是其中之一。
- **hz**：serverCron 每秒执行几次，默认 10，即每 100 毫秒一次。

### 惰性删除：用到时再检查
任何命令读写一个 key 之前，Redis 都先查过期字典。已经过期的，当场删掉，然后按「这个 key 不存在」继续处理。

它几乎不额外花 CPU。问题是：过期后再也没人访问的 key，会一直占着内存。所以还需要定期删除。

### 定期删除：后台分批抽查
serverCron 每次执行时，会做这样一轮清理：

1. 从过期字典里取一批 key，默认 20 个；
2. 删掉其中已经过期的；
3. 如果这一批里过期的超过 10%（20 个里多于 2 个），说明过期 key 还多，再取一批；
4. 一轮花的时间有上限：默认配置下约 25 毫秒（每 100 毫秒周期的 25%），到点就停，下一轮从停下的位置接着查。

抽查而不是全查、设上限而不是查到底，是在「及时释放内存」和「不拖慢正常请求」之间取平衡。

### 两种都没删掉怎么办
两种方式都可能有漏网的过期 key。内存用到 `maxmemory` 上限后，由 `maxmemory-policy`（内存淘汰策略）决定删谁，例如 `volatile-lru` 会在设了过期时间的 key 中淘汰最久没用的。注意默认策略是 `noeviction`：什么都不删，新的写命令直接报错。

### 主从复制时谁来删
从节点不自己删过期 key，而是等主节点删除后同步过来的 `DEL` 命令，这样主从数据才一致。`DEL` 可能晚到，所以从节点在处理**只读命令**时会自己判断：已经过期的 key 直接返回不存在。

### 进阶：源码与版本细节（基础薄弱可先跳过）
- 惰性删除入口：`lookupKey` 中调用 `expireIfNeeded`。定期删除入口：`activeExpireCycle`。
- 除了 serverCron 中的「慢周期」，每次事件循环的 `beforeSleep` 还会跑「快周期」：单次不超过 1000 微秒，只在上次慢周期超时退出、或估算的残留过期比例偏高时运行。
- 版本差异：

| 行为 | Redis 5 及以前 | Redis 6.0 及以后 |
|---|---|---|
| 取 key 方式 | 随机抽样 | 沿游标顺序扫描 |
| 每批数量 | 20 | 20（随 effort 增加） |
| 继续下一批的阈值 | 超过 25% | 超过 10%（随 effort 降低） |
| 力度调节 | 无 | `active-expire-effort`，1–10，默认 1 |

调高 `active-expire-effort` 会增加每批数量和时间预算，代价是更多 CPU 和延迟。

## 示例
```bash
# 慢周期频率与清理力度
redis-cli CONFIG GET hz
redis-cli CONFIG GET active-expire-effort
# expired_keys：累计过期删除数；expired_stale_perc：估算的残留过期 key 比例
redis-cli INFO stats | grep -E 'expired_keys|expired_stale_perc|expired_time_cap_reached_count'
```

## 易错点
- 以为 key 到期的那一刻就会被删除；实际要等下一次访问或下一轮抽查
- 以为定期删除每次扫描所有带 TTL 的 key；实际每批只取 20 个，并且有时间上限
- 把「过期比例超过 25% 才继续」当成当前行为；这是 Redis 5 及以前的规则
- 把过期删除和内存淘汰混为一谈；淘汰在内存达到 maxmemory 时才触发，默认策略还不淘汰

## 追问
### [f1] 大量 key 在同一时刻过期，会有什么影响？
每一批的过期比例都会超过阈值，定期删除会连续执行，直到触到时间上限，导致 CPU 占用和请求延迟升高；对缓存来说还可能引发雪崩。常见做法是给 TTL 加一个随机偏移，把过期时间打散。

### [f2] 为什么不给每个 key 设一个定时器，到期立即删除？
每个 key 一个定时器，内存和调度开销都很大；而 Redis 的命令在主线程执行，大量定时器回调会挤占正常请求。惰性删除加定期抽查，是在内存占用和 CPU 之间的折中。

### [f3] 从节点上读一个已过期、但主节点还没删的 key，会返回什么？
只读命令会返回「不存在」，因为从节点用逻辑时钟判断它已过期。但这个 key 仍然占着从节点的内存，要等主节点传来 `DEL` 才会真正删除。

### [f4] 删除过期 key 会阻塞主线程吗？
默认会：`lazyfree-lazy-expire no`，过期删除和 `DEL` 一样同步释放内存，删除大 key 时可能造成卡顿。设为 `yes` 后改为后台线程释放，效果和 `UNLINK` 一样。
