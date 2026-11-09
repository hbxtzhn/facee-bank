---
id: q_01M6XCCY743N5ZB5A0BCRV65SX
title: Redis 怎么用有序集合做排行榜？
type: concept
difficulty: easy
importance: 2
category: redis
tags: [redis-data-types]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用有序集合 ZSet：成员是用户，分数是得分，`ZADD` 写入或更新分数，按分数从高到低取前几名就是排行榜。

## 要点
- [kp1|3] ZSet 的每个成员都带一个分数，按分数自动排序
- [kp2|3] `ZADD key 分数 成员` 写入，成员已存在则更新分数
- [kp3|2] `ZREVRANGE key 0 n-1 WITHSCORES` 按分数倒序取前 n 名
- [kp4|2] `ZINCRBY` 给成员的分数增加指定值，适合累计得分
- [kp5] `ZREVRANK` 查某个成员的名次，名次从 0 开始

## 详解
### 先搞懂：一张自动排好序的成绩单
老师把学生成绩写在一张表上，每次有人成绩变了，就要重新排一遍。ZSet 像一张会自动排序的成绩单：你只管写「某某多少分」，它自己保证按分数排好。

后文会用到的术语：

- **成员（member）**：集合里的元素，在集合里唯一，比如用户 ID。
- **分数（score）**：成员对应的数字，决定排序。
- **名次**：成员在排序结果里的位置。

### 写入和更新分数
- `ZADD rank 100 alice`：alice 100 分。
- 再执行 `ZADD rank 120 alice`：alice 的分数更新成 120，成员不会重复。
- `ZINCRBY rank 10 alice`：在原来基础上加 10 分，适合每次答对加分、每次点赞加分这类累计场景。

### 取前几名
`ZREVRANGE rank 0 2 WITHSCORES` 按分数从高到低，取下标 0 到 2 的成员，也就是前三名，同时返回分数。

Redis 6.2 起，`ZREVRANGE` 被标记为过时，推荐用 `ZRANGE rank 0 2 REV WITHSCORES`，效果一样。

### 查某人的名次和分数
- `ZREVRANK rank alice`：alice 从高到低的名次，第一名返回 0。
- `ZSCORE rank alice`：alice 的分数。

### 同分怎么办
分数相同时，ZSet 按成员的字典序排。如果希望同分按先到先得，可以把时间戳编码进分数里，比如分数的小数部分放时间。

## 示例
```bash
ZADD rank:game 100 alice 90 bob 120 carol
ZINCRBY rank:game 15 bob               # bob 变成 105
ZREVRANGE rank:game 0 2 WITHSCORES     # 前三名：carol、bob、alice
ZREVRANK rank:game alice               # alice 的名次，从 0 开始
```

## 易错点
- 以为名次从 1 开始；`ZRANK` 和 `ZREVRANK` 的名次从 0 开始
- 以为同一成员多次 `ZADD` 会产生多条；成员唯一，只更新分数
- 分数写成很大的小数；分数是双精度浮点数，过大的整数会丢精度

## 追问
### [f1] 排行榜数据量特别大怎么办？
ZSet 排序取前几名很快，但单个 key 过大会占内存、也不利于迁移。可以按时间或分区拆成多个 key，或只保留前若干名。
