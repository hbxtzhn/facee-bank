---
id: q_01M6XCDDS29S4VTVZV2Q1G6CS6
title: 怎么处理大 key？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [hot-big-key]
prerequisites: [q_01M6XCDD8YV7QCDV341QCSS9GS]
appliesTo: ["UNLINK：Redis >= 4.0"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
处理大 key 分两步：删除时 Redis 4.0 以上用 UNLINK 异步删，低版本用 SCAN 系列命令分批删；日常则把大 value 压缩、大集合拆小。

## 要点
- [kp1|3] Redis 4.0 起用 `UNLINK` 删除，主线程只摘掉 key，内存在后台释放
- [kp2|3] 低版本不要直接 DEL，用 SSCAN、HSCAN 等分批删元素
- [kp3|2] 大字符串用序列化、压缩减小体积
- [kp4|2] 大集合按规则拆成多个小 key，比如按哈希取模分桶

## 详解
### 先搞懂：搬走大箱子不能一口气
还是传送带的比方：有个特别大的箱子要处理掉。一次性搬走，整条传送带停很久；拆开成小件，分几次搬，传送带基本不受影响。

处理大 key，就是避免“一口气”做完。

后文用到几个词：

- **阻塞**：主线程被一个耗时操作占住，其他命令只能等待。
- **异步删除**：把耗时的释放内存工作交给后台线程，主线程立刻继续。

### 删除大 key
**Redis 4.0 及以上：用 `UNLINK`**

`UNLINK` 的用法和 `DEL` 一样。区别是它先在主线程里把 key 从键空间摘掉，真正释放内存的耗时工作交给后台线程。所以主线程基本不会被卡住。

**低于 4.0：分批删除**

此版本没有 `UNLINK`，直接 `DEL` 大集合会阻塞。做法是用 `SCAN` 家族的命令增量遍历，每次取一小批元素，分批删除，最后再删 key 本身：

- Hash 用 `HSCAN` 配合 `HDEL`；
- Set 用 `SSCAN` 配合 `SREM`；
- ZSet 用 `ZSCAN` 配合 `ZREM`；
- List 用 `LTRIM` 逐步裁剪。

### 从根上减小大 key
- **字符串很大**：不方便拆分，可以先序列化，再用压缩算法压小，把体积控制在合理范围。
- **集合元素太多**：拆成多个小 key。比如用户的订单集合，可以按用户 ID 取模，分成若干个桶。
- **预防**：给集合设元素上限，定期清理不再需要的数据。

### 方案对比：删除方式
| 方式 | 适用版本 | 是否阻塞主线程 | 说明 |
|---|---|---|---|
| `DEL` | 全部 | 大 key 会阻塞 | 小 key 没问题 |
| `UNLINK` | 4.0 及以上 | 基本不阻塞 | 释放内存在后台 |
| SCAN 分批删 | 全部 | 每批很小 | 麻烦，但低版本可用 |

结论：4.0 及以上一律用 `UNLINK` 删大 key；低版本才用分批删。

## 示例
```bash
UNLINK big:hash:1

# 低版本：分批删除 Hash 中的字段
HSCAN big:hash:1 0 COUNT 100
HDEL big:hash:1 field1 field2
```

## 易错点
- 以为 UNLINK 立刻释放内存；释放在后台进行，稍后才完成
- 对大集合直接用 DEL，导致 Redis 卡住
- 拆分 key 后没改读写逻辑，导致业务取不到完整数据

## 追问
### [f1] 删除 key 时还有什么办法避免阻塞？
Redis 4.0 起还有 `lazyfree-lazy-eviction`、`lazyfree-lazy-expire` 等配置，让淘汰和过期删除也异步进行。
