---
id: q_01M6XCCXYYZYAGXZTVQ1XNYSHB
title: Redis 怎么用原子递增实现计数器？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [redis-data-types, atomic-operation]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `INCR` 或 `INCRBY` 让 key 里的数字原子加一或加指定值，并发请求也不会丢计数，适合点赞数和访问量。

## 要点
- [kp1|3] `INCR key` 把 key 的整数值加一，返回加完后的值
- [kp2|3] `INCRBY key n` 加指定整数，`DECR` 系列是减
- [kp3|2] 单个命令是原子的，并发下不会丢计数
- [kp4|2] key 不存在时当作 0 开始加；值不是整数会报错
- [kp5] 可配合 `EXPIRE` 做限流、按天统计

## 详解
### 先搞懂：为什么不能「先读再写」
做点赞功能，最容易想到的是：读出当前点赞数，加一，再写回去。

两个人同时点赞时，两个请求都读到 100，各自加一后都写 101。本来该是 102，结果丢了一次。这是并发下常见的「丢失更新」。

`INCR` 把「读、加一、写」做成一个不可拆开的命令，就不会丢。

后文会用到的术语：

- **原子**：一个操作要么完整执行，要么不执行，不会被别的操作插进来。
- **计数器**：用一个数字记录次数。

### INCR 怎么用
- `INCR key`：加一。
- `INCRBY key n`：加 n。
- `DECR key`、`DECRBY key n`：减一、减 n。

key 不存在时，Redis 当它是 0，所以第一次 `INCR` 返回 1。如果 key 里存的不是整数，命令会报错。

### 为什么是原子的
Redis 用一个线程按顺序执行命令，每个命令执行时不会被别的命令打断。所以多个客户端同时发 `INCR`，会排队依次执行，每次都在上一次的结果上加一。

### 常见用法
- 点赞数、文章阅读量、接口调用次数。
- 限流：以用户和时间窗口拼成 key，每次请求 `INCR`，超过上限就拒绝，同时给 key 设过期时间。
- 全局自增 ID。

## 示例
```bash
INCR article:100:likes             # 第一次返回 1
INCRBY article:100:likes 5         # 加 5
EXPIRE rate:user:7:minute 60       # 限流用的 key 设置 60 秒过期
```

## 易错点
- 以为要先 `GET` 再 `SET`；这样并发下会丢计数，直接用 `INCR`
- 以为 `INCR` 能处理小数；小数用 `INCRBYFLOAT`
- 只 `INCR` 不设过期；用于限流的 key 要配合过期时间，否则一直保留

## 追问
### [f1] 限流时 INCR 和 EXPIRE 分开执行有什么风险？
`INCR` 之后程序崩溃，`EXPIRE` 没执行，key 就永不过期。可以在第一次 `INCR` 返回 1 时设置过期，或用 Lua 脚本把两步合成一个原子操作。
