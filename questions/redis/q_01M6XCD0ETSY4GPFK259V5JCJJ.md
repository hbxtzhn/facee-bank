---
id: q_01M6XCD0ETSY4GPFK259V5JCJJ
title: save 和 bgsave 有什么区别？
type: concept
difficulty: medium
importance: 2
category: redis
tags: [rdb-aof, process]
prerequisites: [q_01M6XCCZS9XZ69NDV5RERDGZYH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
save 由主进程同步写快照，期间所有请求都被阻塞；bgsave 由 fork 出的子进程在后台写，主进程继续服务，生产环境用 bgsave。

## 要点
- [kp1|3] save 在主进程里同步执行，写完前客户端请求全部等待
- [kp2|3] bgsave 由子进程执行，命令马上返回，主进程继续处理请求
- [kp3|2] bgsave 在 fork 那一刻会短暂阻塞，之后不阻塞
- [kp4] 生产环境用 bgsave，save 只适合数据很少或可以停服的时候

## 详解
### 先搞懂：自己打包还是请人打包
你要把店里的货打包寄走。自己打包（save）的话，打包期间没法接待顾客；请个帮手打包（bgsave），你可以继续接待，只是叫帮手、交接货物时耽误一小会儿。

后文用到的词：
- **阻塞**：主进程忙着别的事，没法回应客户端，客户端只能等。
- **fork**：复制出一个子进程。

### save：主进程亲自写
执行 `save` 时，主进程自己遍历所有数据并写入 RDB 文件，写完才返回。写的过程中，其他客户端发来的命令都不会被处理。数据量大时，可能卡住很久，客户端会超时。

### bgsave：子进程在后台写
执行 `bgsave` 时，主进程 fork 出子进程，立刻返回，子进程负责写文件。主进程继续处理读写请求。需要注意：

- fork 的那一瞬间主进程要复制页表，数据越大这一瞬间越长；
- 快照期间写入多的话，会因为写时复制多占内存；
- 已经有子进程在做持久化时，不会再启动第二个。

### 方案对比：save 与 bgsave
| 命令 | 谁来写文件 | 是否阻塞请求 | 额外开销 | 适合 |
|---|---|---|---|---|
| `save` | 主进程 | 整个过程都阻塞 | 不需要 fork | 数据很少，或服务已停止 |
| `bgsave` | 子进程 | 只在 fork 时短暂阻塞 | fork 和写时复制的内存 | 生产环境 |

结论：默认用 bgsave；只有数据量很小，或者本来就要停服时才考虑 save。

## 示例
```bash
redis-cli save     # 阻塞直到写完
redis-cli bgsave   # 立即返回 Background saving started
```

## 易错点
- 以为 bgsave 完全不阻塞；fork 时会短暂阻塞，实例越大越明显
- 以为 save 更安全所以更好；它只是同步写，代价是整个服务停顿
- 以为两个命令生成的文件格式不同；都是同样的 RDB 文件

## 追问
### [f1] bgsave 正在执行时再执行 save 会怎样？
Redis 会拒绝，提示已有后台保存任务在进行，避免两个任务同时写文件。
