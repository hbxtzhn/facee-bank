---
id: q_01M6QN33W7DGDKRD07W2A60P8T
title: Redis 怎么给 key 设置过期时间？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [redis]
appliesTo: ["Redis >= 2.8", "EXPIRE 的 NX / XX / GT / LT 选项：Redis >= 7.0"]
related: [q_01M6QKTSDZJXVNP4HHXN7MW771]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Redis 文档：EXPIRE", url: "https://redis.io/docs/latest/commands/expire/" }
  - { title: "Redis 文档：TTL", url: "https://redis.io/docs/latest/commands/ttl/" }
  - { title: "Redis 文档：SET", url: "https://redis.io/docs/latest/commands/set/" }
reviewedAt: 2026-11-06
estimatedMinutes: 2
---

## 一句话
用 EXPIRE 给已有 key 设过期秒数，或写入时用 SET 的 EX 选项一步完成；用 TTL 查看剩余时间，用 PERSIST 取消过期。

## 要点
- [kp1|3] EXPIRE key 秒数 设置过期；SET key value EX 秒数 写入时一并设置
- [kp2|2] TTL 返回剩余秒数：-1 表示没设过期，-2 表示 key 不存在
- [kp3|2] 用 SET 覆盖整个值会清掉过期时间；INCR、HSET 等修改不会
- [kp4] 过期时间存成绝对时间戳，服务器时钟变化会影响它

## 详解
### 先搞懂：为什么要给 key 设过期时间
Redis 常被当作缓存使用，里面的数据只是数据库的「临时副本」，不需要永久保存。给 key 设过期时间，就像给便利贴写上「明天扔掉」：到期后 Redis 会自动删除它，不用业务代码自己清理。验证码、登录会话、接口缓存，都是这样用的。

后面会用到的几个词：

- **TTL**（Time To Live）：key 还能活多久，也是查询剩余时间的命令名。
- **持久 key**：没设过期时间的 key，会一直保留，直到被显式删除。

### 设置过期时间：两种写法
- 先写入、再设过期：`SET code:13800000000 123456`，然后 `EXPIRE code:13800000000 300`；
- 写入时一步完成：`SET code:13800000000 123456 EX 300`。

推荐第二种：两条命令之间如果程序崩溃，key 就会永远不过期；一条命令要么全部成功、要么都不生效。

要毫秒精度用 `PEXPIRE`；要指定「几点几分过期」用 `EXPIREAT`（Unix 时间戳）。

### 查看和取消
- `TTL key`：返回剩余秒数。`-1` 表示 key 存在但没设过期，`-2` 表示 key 不存在。
- `PERSIST key`：取消过期时间，让 key 变回持久 key。
- 对已经设过过期时间的 key 再执行一次 `EXPIRE`，会用新时间覆盖旧时间。常用来做「用户每次操作都续期」的会话。

### 哪些操作会让过期时间丢失
只有**删除或整体覆盖** key 的命令才会清掉过期时间，例如 `DEL`、`SET`、`GETSET` 以及各种 `*STORE` 命令。只是修改值、不替换整个值的命令不影响过期时间，例如 `INCR`、`LPUSH`、`HSET`。`RENAME` 会把过期时间一起带到新 key 名上。

### 进阶：条件选项与时钟（基础薄弱可先跳过）
- Redis 7.0 起，`EXPIRE` 支持条件选项：`NX` 只在没有过期时间时设置，`XX` 只在已有时设置，`GT` / `LT` 只在新时间更长 / 更短时设置。
- 过期时间以毫秒级 Unix 绝对时间戳保存。Redis 停机期间时间照样在走；把服务器时钟调快，key 也会提前过期。

## 示例
```bash
redis-cli SET code:13800000000 123456 EX 300   # 写入并设置 300 秒后过期
redis-cli TTL code:13800000000                 # 剩余秒数
redis-cli SET code:13800000000 654321          # 覆盖写入，过期时间被清掉
redis-cli TTL code:13800000000                 # 返回 -1
```

## 易错点
- 先 SET 再 EXPIRE 分两步写，中间失败会留下永不过期的 key
- 以为用 SET 改值后过期时间还在；SET 覆盖会清掉过期时间
- 以为 TTL 返回 -1 是 key 不存在；-1 是没设过期，-2 才是不存在

## 追问
### [f1] key 到了过期时间，会立刻从内存中消失吗？
不一定。Redis 用惰性删除和定期抽查来清理，过期 key 可能还会在内存里停留一段时间，但访问时会被当作不存在。详见相关题「Redis 过期 key 是怎么被删除的？」。

### [f2] EXPIRE 传入 0 或负数会怎样？
key 会被直接删除，效果和 DEL 一样，而不是走过期流程。
