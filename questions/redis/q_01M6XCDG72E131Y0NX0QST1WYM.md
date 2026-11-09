---
id: q_01M6XCDG72E131Y0NX0QST1WYM
title: Redisson 为什么用 Lua 脚本完成加锁？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [distributed-lock, atomic-operation]
prerequisites: [q_01M6XCDF9HC7C3V6ZETW96XBY3, q_01M6ZYJV9DSFGKHTGJ4J6B3ZH6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
加锁要“判断有没有锁、写入、设过期时间”好几步，Lua 脚本能让它们在 Redis 里一次执行完，中间不被打断，所以不会出现半成功的锁。

## 要点
- [kp1|3] 加锁包含判断、写入、设过期时间多步，分开发有被插队的空隙
- [kp2|3] Lua 脚本在 Redis 里整体执行，期间不会有其他命令插入
- [kp3|2] 可重入逻辑要先判断是否同一线程再加一，一条命令做不到
- [kp4] 解锁也用脚本，先校验是自己的锁，再减次数或删除

## 详解
### 先搞懂：几步操作中间会被别人插进来
想象会议室的登记：先看登记簿上有没有人，没有就写上名字，再写时间。这是三个动作。如果你看完“没人”，还没来得及写，另一个人也看了，也是“没人”，两个人都写上了名字，就冲突了。

Redisson 的锁比简单的 SET NX 复杂：要支持重入，要写线程标识，还要设过期时间。这些步骤分开发，中间都有空隙。

后文用到的词：

- **原子**：一组操作要么整体完成，要么没发生，中间别人看不到半成品。
- **Lua 脚本**：Redis 内置的脚本，一次发给服务端执行。

### 不用脚本会出什么问题
假如用普通命令分步完成：

1. 先 `EXISTS` 判断锁是否存在；
2. 不存在就 `HSET` 写入线程标识；
3. 再 `PEXPIRE` 设置过期时间。

可能出现的问题：

- 第 1 步和第 2 步之间，别的客户端也完成了判断，两个都成功拿到锁。
- 第 2 步和第 3 步之间，客户端宕机，锁没有过期时间，永远不会释放。

### 脚本怎么解决
Redis 执行命令是单线程的，Lua 脚本被当成一个整体执行。脚本里的判断、写入、设置过期时间，在 Redis 看来是一件事，别的客户端的命令只能在它前后执行。

所以加锁要么成功（锁和过期时间都已经设好），要么失败（什么都没改），不会出现中间状态。

### 为什么不直接用 SET NX EX
`SET key value NX EX` 本身就是一条命令，能完成简单的互斥加过期。但 Redisson 要支持：

- **可重入**：同一线程再次加锁，要判断线程标识并把次数加一；
- **返回剩余时间**：失败时要告诉调用者锁还剩多久。

这些带条件判断的逻辑，一条命令写不出，只能用脚本。

### 使用脚本的代价
脚本执行期间 Redis 不处理别的命令，所以脚本必须短小。锁的脚本只有几条命令，不会成为问题。

## 示例
```lua
-- 简化的加锁脚本：不存在则创建，同线程则重入加一
if redis.call('exists', KEYS[1]) == 0 then
    redis.call('hset', KEYS[1], ARGV[2], 1)
    redis.call('pexpire', KEYS[1], ARGV[1])
    return nil
end
if redis.call('hexists', KEYS[1], ARGV[2]) == 1 then
    redis.call('hincrby', KEYS[1], ARGV[2], 1)
    redis.call('pexpire', KEYS[1], ARGV[1])
    return nil
end
return redis.call('pttl', KEYS[1])
```

## 易错点
- 以为 Lua 只是为了少发几次网络请求；核心是保证多步操作不被打断
- 以为分步命令加个 try-catch 就能保证一致；宕机或并发时依然会有空隙
- 以为脚本越复杂越好；脚本过长会阻塞 Redis

## 追问
### [f1] 如果脚本执行到一半 Redis 宕机，锁会怎样？
脚本整体按一条命令处理，要么执行完，要么没执行。具体是否持久化取决于 Redis 的持久化配置，所以故障后锁可能丢失。
