---
id: q_01M6XCDB7P7WNV48GAGRK0NQ12
title: Redis 有哪几种淘汰策略，各自怎么选？
type: concept
difficulty: medium
importance: 3
category: redis
tags: [replacement-policy]
prerequisites: [q_01M6XCDAQAJH13PEPZ5K2FSAHV, q_01M6XCDAZHCEY793C5R7CMPEYW]
appliesTo: ["LFU 策略：Redis >= 4.0"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
Redis 有八种淘汰策略：noeviction 不淘汰，另外七种按淘汰范围分 allkeys 和 volatile，按依据分 lru、lfu、random、ttl。做缓存通常选 allkeys-lru。

## 要点
- [kp1|3] allkeys 前缀从所有 key 里淘汰；volatile 前缀只从设了过期时间的里淘汰
- [kp2|3] 依据有三种：lru 最久没用、lfu 用得最少、random 随机
- [kp3|2] volatile-ttl 淘汰剩余存活时间最短的 key
- [kp4] LRU 和 LFU 是近似算法，靠随机抽样挑选，不是精确排序

## 详解
### 先搞懂：衣柜满了先扔哪件
衣柜满了要扔衣服。你可以先限定范围：所有衣服都能扔，还是只扔标了“可丢弃”的。再选依据：扔最久没穿的，扔穿得最少的，还是闭眼随便扔。

Redis 的策略名就是“范围 加 依据”拼起来的。

后文用到几个词：

- **LRU**：最近最少使用，最久没被访问的先淘汰。
- **LFU**：最不经常使用，访问次数最少的先淘汰。
- **volatile**：指设置了过期时间的 key。

### 策略一览
- `noeviction`：不淘汰，写入报错。
- `allkeys-lru`、`allkeys-lfu`、`allkeys-random`：在所有 key 中淘汰。
- `volatile-lru`、`volatile-lfu`、`volatile-random`、`volatile-ttl`：只在设了过期时间的 key 中淘汰。

如果 volatile 系列找不到可淘汰的 key，也就是没有 key 设过期时间，行为就和 `noeviction` 一样，写入会报错。

### 方案对比：怎么选
| 策略 | 淘汰范围 | 淘汰依据 | 适合场景 |
|---|---|---|---|
| noeviction | 不淘汰 | 无 | 数据不能丢，宁可报错 |
| allkeys-lru | 所有 key | 最久没访问 | 通用缓存，最常用 |
| allkeys-lfu | 所有 key | 访问次数最少 | 访问热度差别大的缓存 |
| allkeys-random | 所有 key | 随机 | 所有数据访问机会差不多 |
| volatile-lru / lfu | 设过期的 key | 同上 | 缓存和永久数据混用 |
| volatile-ttl | 设过期的 key | 快过期的先走 | 希望优先去掉将过期数据 |

结论：纯缓存默认选 `allkeys-lru`；热点很集中时可考虑 `allkeys-lfu`；缓存和永久数据混在一个实例里，才用 volatile 系列。

### 进阶：近似 LRU（基础薄弱可先跳过）
Redis 不会为所有 key 维护精确的访问顺序，那样太耗内存。它每次随机抽取一小批 key，淘汰其中最合适的。抽样数量由 `maxmemory-samples` 控制，调大更接近精确 LRU，但更耗 CPU。

## 示例
```bash
CONFIG SET maxmemory-policy allkeys-lru
CONFIG GET maxmemory-policy
```

## 易错点
- 以为 volatile 策略会淘汰所有 key；它只管设了过期时间的 key
- 以为 LRU 是精确的；Redis 使用的是抽样近似算法
- 以为 LFU 和 LRU 一样；LFU 看访问频率，LRU 看最近一次访问时间

## 追问
### [f1] LRU 和 LFU 有什么区别，各自的缺点是什么？
LRU 只看最近一次访问，一次性的大扫描可能把热数据挤掉。LFU 看访问次数，能保留长期热点，但以前热、现在不热的数据需要靠衰减才会被淘汰。
