---
id: q_01M6XCDESJ0KFX8CB1H2SQ69BG
title: 怎么用 SET NX 实现一个最简单的分布式锁？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [distributed-lock, atomic-operation]
prerequisites: [q_01M6XCDEHJ08YAQ25K5T37V0GY]
appliesTo: ["Redis >= 2.6.12"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `SET key value NX EX 秒数` 一条命令加锁：key 不存在才设置成功，同时设好过期时间；释放时先确认锁是自己的，再删除。

## 要点
- [kp1|3] NX 表示 key 不存在才设置，设置成功就是抢到锁
- [kp2|3] EX 在同一条命令里设过期时间，避免宕机后锁永不释放
- [kp3|2] value 存本线程独有的标识，释放时校验是自己的锁才删
- [kp4] 不要先 SETNX 再 EXPIRE 分两步，中间宕机会留下永久锁

## 详解
### 先搞懂：像在门上挂一块“有人”牌子
去公共会议室，门上有个牌子。牌子不在，你就挂上自己的名字，进去开会；牌子在，说明有人，你得等。开完会，把自己的牌子取下来。

Redis 里这块牌子就是一个 key。挂牌子就是创建这个 key，取牌子就是删除它。

后文用到的词：

- **NX**：Not eXists，key 不存在时才执行设置。
- **EX**：给 key 设置多少秒后自动过期。
- **加锁成功**：`SET` 返回 OK；失败返回 nil。

### 加锁：一条命令同时做两件事
命令格式是：

```bash
SET lock:order:1001 8f3a-uuid NX EX 30
```

含义是：`lock:order:1001` 这个 key 不存在时，才把它设为 `8f3a-uuid`，并且 30 秒后自动过期。

Redis 执行命令是一条一条来的，所以多个客户端同时抢，只有一个会返回 OK。

为什么要把设置和过期放在一条命令里？早期的做法是先 `SETNX` 再 `EXPIRE`，两条命令之间如果服务宕机，key 已经存在却没有过期时间，锁就永远没人能释放。

### value 为什么要放唯一标识
value 通常放一个随机串或者“服务实例 ID 加线程 ID”。

原因是：线程 A 的锁因为超时已经过期，线程 B 拿到了新锁。这时 A 业务做完，如果无脑 `DEL`，就会把 B 的锁删掉。

所以释放锁时要先判断 value 是不是自己的，再删除。

### 释放：判断和删除要一起完成
判断和删除是两步，分开发有间隙，要用 Lua 脚本合成一步：

```lua
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```

## 示例
```bash
# 加锁，30 秒自动过期
SET lock:order:1001 8f3a-uuid NX EX 30
# 释放：用 Lua 脚本校验 value 后再删除
EVAL "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end" 1 lock:order:1001 8f3a-uuid
```

## 易错点
- 先 SETNX 再 EXPIRE 分两步写；两步之间宕机会留下没有过期时间的锁
- value 固定写 1；超时后可能误删别人刚拿到的锁
- 业务出异常没有释放锁；释放要放在 finally 里
- 业务时间超过锁的过期时间；这种情况需要续期

## 追问
### [f1] 为什么释放锁要用 Lua，不能先 GET 再 DEL？
GET 判断完、DEL 执行前，锁可能刚好过期并被别人拿到，这时 DEL 就会删掉别人的锁。Lua 脚本在 Redis 里一次执行完，中间不会被打断。
