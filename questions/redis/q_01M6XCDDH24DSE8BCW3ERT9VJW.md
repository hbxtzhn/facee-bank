---
id: q_01M6XCDDH24DSE8BCW3ERT9VJW
title: 怎么找出 Redis 里的大 key？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [hot-big-key]
prerequisites: [q_01M6XCDD8YV7QCDV341QCSS9GS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
可以用 redis-cli 的 --bigkeys 参数遍历统计各类型里最大的 key，或者用 redis-rdb-tools 离线分析 RDB 快照文件。

## 要点
- [kp1|3] `redis-cli --bigkeys` 遍历所有 key，每种数据类型报告最大的一个
- [kp2|3] redis-rdb-tools 离线分析 RDB 快照，不占用线上实例
- [kp3|2] `MEMORY USAGE key` 可以查看指定 key 占用的内存
- [kp4] --bigkeys 会扫描全库，要避开业务高峰，最好连从节点执行

## 详解
### 先搞懂：找大 key 就是“称重”
仓库里堆满了货物，想找出最重的几件，只有两个办法：一件件去称，或者看进货单估算。

Redis 里的大 key 也一样。第一种办法是现场遍历所有 key，第二种是拿一份数据快照来离线分析。

后文用到几个词：

- **RDB 快照**：Redis 某一时刻的数据存成的文件，通过 `BGSAVE` 或定时配置生成。
- **遍历**：把所有 key 都过一遍。

### 方式一：redis-cli --bigkeys
命令是 `redis-cli --bigkeys`。它在后台用 `SCAN` 分批遍历整个库，按类型统计，输出每种类型里最大的 key，也就是每种类型的 Top 1，以及整体的统计信息。

注意几点：

- 它按元素个数判断“大”，而不是占用字节数。字符串则看长度。
- 它只给出每种类型最大的一个，想看更多要自己结合其他命令。
- 遍历会增加服务器负担，线上最好在业务低峰期执行，或连接从节点执行。
- 可以加 `-i 0.1` 之类的参数，让每批扫描之间暂停一下，减轻压力。

### 方式二：redis-rdb-tools
这是一个用 Python 写的开源工具，可以解析 RDB 文件，生成内存分析报告，列出占用内存最多的 key。

好处是它在离线文件上工作，完全不影响线上 Redis。缺点是只反映快照那一刻的情况，不是实时的。

### 补充：精确查看单个 key
知道某个 key 可疑后，可以用 `MEMORY USAGE key` 看它大约占用多少字节。

### 方案对比
| 方式 | 数据来源 | 对线上影响 | 特点 |
|---|---|---|---|
| `--bigkeys` | 在线遍历 | 有扫描开销 | 简单直接，每类给一个 |
| redis-rdb-tools | RDB 文件 | 几乎没有 | 结果详细，非实时 |
| `MEMORY USAGE` | 单个 key | 很小 | 只能查已知的 key |

结论：先在低峰期或从节点用 `--bigkeys` 快速定位，要详细报告再用 redis-rdb-tools 分析快照。

## 示例
```bash
redis-cli -h 127.0.0.1 -p 6379 --bigkeys -i 0.1
redis-cli MEMORY USAGE user:list:1
```

## 易错点
- 以为 --bigkeys 是按字节大小统计；集合类型按元素个数判断
- 在业务高峰直连主节点跑 --bigkeys；扫描会占用资源
- 以为 --bigkeys 会列出所有大 key；每种类型只给 Top 1

## 追问
### [f1] 找到大 key 之后怎么办？
可以拆分成多个小 key，或压缩、序列化后再存；需要删除时用 `UNLINK` 异步删除，具体见“怎么处理大 key”。
