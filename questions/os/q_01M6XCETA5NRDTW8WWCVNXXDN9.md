---
id: q_01M6XCETA5NRDTW8WWCVNXXDN9
title: poll 相比 select 改进了什么，还剩哪些问题？
type: concept
difficulty: medium
importance: 2
category: os
tags: [io-multiplexing]
prerequisites: [q_01M6XCFX5GC2E61Z4W1WKTKBSN, q_01M6XCFXPA6AC97Z0DF0S2GE8W]
appliesTo: ["Linux"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
poll 用数组代替位图，去掉了 select 对 fd 数量的固定上限；但每次调用仍要拷贝整个数组并线性遍历，本质问题没变。

## 要点
- [kp1|3] poll 用 pollfd 数组传入要监听的 fd，没有 FD_SETSIZE 那样的固定上限
- [kp2|3] 仍然每次调用都把整个数组拷进内核，并线性遍历
- [kp3|2] 事件放在 events 字段，结果写在 revents 字段，不用每次重新设置
- [kp4] 返回后仍要遍历数组，才知道是哪些 fd 就绪

## 详解
### 先搞懂：换了一本更厚的名册，点名方式没变
上一题里，select 像前台文员对着一排门铃挨个检查，而且排数有上限。poll 相当于给他换了一本更厚的名册，不再限制能登记多少个门铃。但他检查的方式没变：还是每次从头看到尾。

后文用到的术语：

- **pollfd**：poll 用的结构体，里面有 fd、关心的事件 `events`、返回的事件 `revents`。
- **线性遍历**：从头到尾逐个检查，耗时和数量成正比。
- **FD_SETSIZE**：select 里 fd_set 位图的大小上限，常为 1024。

### 改进一：没有固定上限
select 的 fd_set 是固定大小的位图。poll 让调用者自己准备一个 `struct pollfd` 数组，数组多大由你决定。所以它不再有 1024 这个固定上限，只受系统对单个进程可打开 fd 数量的限制。

### 改进二：输入输出分开
poll 把“我关心什么事件”放在 `events`，把“实际发生了什么”放在 `revents`，两个字段互不覆盖。所以内核不会改掉你的监听设置，下一轮可以直接复用同一个数组，不必像 select 那样每次重新填。

### 还剩的问题：仍然是全量操作
- **全量拷贝**：每次调用，整个 pollfd 数组都要从用户态拷贝到内核态。监听的 fd 越多，拷贝越多。
- **线性遍历**：内核要逐个检查数组里的每个 fd。耗时随监听数量增长，和活跃数量无关。
- **返回后还要再遍历**：poll 只返回就绪的个数，用户程序仍要把数组从头看一遍，找出 `revents` 不为 0 的项。

所以百万连接里只有几个活跃时，poll 和 select 一样浪费。

### 方案对比：select、poll、epoll
| 方案 | 保存 fd 的方式 | fd 数量限制 | 每次调用拷贝 | 找就绪 fd |
|---|---|---|---|---|
| select | 位图 | 受 FD_SETSIZE 限制 | 整个集合 | 线性遍历 |
| poll | 数组 | 不再有固定上限 | 整个数组 | 线性遍历 |
| epoll | 内核红黑树 | 受系统 fd 限制 | 只拷贝就绪事件 | 直接读就绪列表 |

结论：poll 只是解决了数量上限，要解决效率问题得用 epoll；监听数量不大、需要跨平台时，poll 够用。

## 示例
```c
struct pollfd fds[3];
fds[0].fd = sock1; fds[0].events = POLLIN;
fds[1].fd = sock2; fds[1].events = POLLIN;
fds[2].fd = sock3; fds[2].events = POLLIN;

int n = poll(fds, 3, -1);          // -1 表示一直等
for (int i = 0; i < 3 && n > 0; i++) {
    if (fds[i].revents & POLLIN) { handle(fds[i].fd); n--; }
}
```

## 易错点
- 以为 poll 比 select 快很多；两者都是线性遍历，主要区别是数量上限
- 以为 poll 完全没有 fd 数量限制；仍受系统对进程 fd 数的限制
- 以为 poll 返回的是就绪 fd 列表；它只返回个数，要自己检查 revents

## 追问
### [f1] poll 和 select 的主要区别是什么？
poll 用数组而不是位图，没有固定上限；且输入输出分开，不用每次重新设置。但两者都是全量拷贝加线性遍历。

### [f2] 为什么说 poll 在大量连接下仍然低效？
因为每次调用都要拷贝整个数组、遍历所有 fd，开销和监听总数成正比。活跃的连接少时，大部分工作是浪费的。
