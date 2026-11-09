---
id: q_01M6XCDAQAJH13PEPZ5K2FSAHV
title: Redis 怎么给 key 设置过期时间？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [expiration]
appliesTo: ["SET 的 EX/PX 选项：Redis >= 2.6.12"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 EXPIRE 或 SET 时带 EX、PX 给 key 设置存活时间，到点后 key 自动失效；TTL 查剩余时间，PERSIST 取消过期。

## 要点
- [kp1|3] `EXPIRE key 秒数` 给已有 key 设置过期时间
- [kp2|3] `SET key value EX 秒数` 在写入的同时设置过期时间，是一条命令
- [kp3|2] `TTL` 返回剩余秒数，-1 表示没设过期，-2 表示 key 不存在
- [kp4] `PERSIST` 取消过期；用 SET 覆盖 key 也会清掉过期时间

## 详解
### 先搞懂：key 为什么要设置过期时间
发短信验证码时，你会把验证码存到 Redis。验证码五分钟内有效，之后就没用了。如果不设置过期时间，这些数据会一直占着内存。

可以把它想成超市的酸奶：每盒都有保质期，过了保质期会被下架，不用人一盒盒去清理。

后文用到几个词：

- **TTL**：Time To Live，key 还能活多久。
- **过期**：到了设定的时间点，key 不再能被读到。

### 设置过期时间的几种方式
- `EXPIRE key 60`：让 key 60 秒后过期，单位是秒。
- `PEXPIRE key 60000`：同样是 60 秒，但单位是毫秒。
- `EXPIREAT key 时间戳`：在指定的 Unix 时间点过期，单位是秒。
- `SET key value EX 60`：写入时顺便设置 60 秒过期。`PX` 则是毫秒。

写缓存和验证码时，推荐用 `SET … EX`。因为写值和设过期是一条命令，不会出现值写进去了、过期时间没设上的情况。

### 查看和取消
- `TTL key`：返回剩余秒数。key 存在但没设过期时返回 -1；key 不存在时返回 -2。
- `PERSIST key`：取消过期时间，key 变成永久有效。

## 示例
```bash
SET code:13800000000 "123456" EX 300   # 验证码 300 秒后过期
TTL code:13800000000                    # 查看剩余秒数
EXPIRE user:1 3600                      # 给已有 key 设置 1 小时过期
PERSIST user:1                          # 取消过期
```

## 易错点
- 先 SET 再 EXPIRE 当成原子操作；两条命令之间出问题，key 就会永不过期
- 用不带 EX 的 SET 覆盖已有 key，以为过期时间还在；实际过期时间被清除了
- 以为 TTL 返回 -1 是已过期；-1 是没设过期，-2 才是 key 不存在

## 追问
### [f1] key 过期之后是立刻从内存里删掉吗？
不一定。Redis 通过惰性删除和定期删除清理过期 key，所以过期的 key 可能短暂留在内存里，但读取时不会再返回它。
