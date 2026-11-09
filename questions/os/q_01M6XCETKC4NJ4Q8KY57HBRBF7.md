---
id: q_01M6XCETKC4NJ4Q8KY57HBRBF7
title: epoll 为什么比 select 和 poll 高效？
type: concept
difficulty: medium
importance: 3
category: os
tags: [io-multiplexing]
prerequisites: [q_01M6XCFWPGHQWTXE0J8FY9ZRNP, q_01M6XCFX5GC2E61Z4W1WKTKBSN, q_01M6XCFXPA6AC97Z0DF0S2GE8W]
appliesTo: ["Linux"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
epoll 把要监听的 fd 登记在内核里，只返回已经就绪的 fd，所以不用每次全量拷贝和遍历。

## 要点
- [kp1|3] 用 epoll_ctl 把 fd 一次登记到内核红黑树，不必每次调用都重新传入
- [kp2|3] 就绪的 fd 被放进就绪链表，epoll_wait 只返回这些
- [kp3|2] 耗时只和就绪数量有关，不随监听总数线性增长
- [kp4] 支持水平触发（LT）和边缘触发（ET）两种模式

## 详解
### 先搞懂：前台只登记一次，门铃响了自动通知
前面的 select 和 poll，像前台文员每次都把整排门铃查一遍。epoll 的做法是：先把要看的门铃一次登记好，之后哪个门铃响了，就会自动记到一张“待处理清单”上。文员只要看清单就行，不用再逐个检查。

后文用到的术语：

- **红黑树**：一种查找、增删都比较快的树结构，这里用来保存被监听的 fd。
- **就绪链表**：内核里专门记录“已经有事件的 fd”的链表。
- **回调**：事件发生时内核自动调用的函数，这里负责把 fd 加入就绪链表。

### epoll 的三个调用
- `epoll_create`：创建一个 epoll 实例，内核里随之建好红黑树和就绪链表。
- `epoll_ctl`：增加、修改或删除要监听的 fd。每个 fd 只在登记时传一次。
- `epoll_wait`：等待事件，返回就绪的那些 fd。

### 为什么高效：两处改进
**第一，监听集合保存在内核里。** select 和 poll 每次调用都得把全部 fd 传进去。epoll 用 `epoll_ctl` 把 fd 加进内核的红黑树，之后不需要重复传入。红黑树的增删查一般是 O(log n)。

**第二，只返回就绪的 fd。** 某个 fd 有事件时，内核通过回调把它挂到就绪链表上。`epoll_wait` 只需检查链表是否为空，有就把这些就绪项拷贝给用户程序。所以拷贝量和遍历量都只和就绪数量有关。

### 方案对比：select、poll、epoll
| 方案 | 监听集合在哪 | 每次调用传输 | 找就绪 fd | 适合 |
|---|---|---|---|---|
| select | 用户态位图 | 整个集合 | 内核加用户各遍历一次 | 少量 fd、跨平台 |
| poll | 用户态数组 | 整个数组 | 内核加用户各遍历一次 | 少量 fd、没有上限要求 |
| epoll | 内核红黑树 | 只返回就绪项 | 直接读就绪链表 | Linux 上大量连接、少量活跃 |

结论：Linux 上连接多、活跃少的服务端默认用 epoll；只有少量 fd 或需要跨平台时，select 或 poll 也够用。

### 进阶：水平触发和边缘触发（基础薄弱可先跳过）
- **水平触发（LT）**：只要 fd 里还有数据没读完，每次 `epoll_wait` 都会再通知。这是默认模式，编程简单。
- **边缘触发（ET）**：只在状态变化时通知一次，所以必须一次把数据读到读不出为止，通常配合非阻塞 IO 使用。
- epoll 是 Linux 特有的；BSD 和 macOS 对应的是 kqueue。

## 示例
```c
int epfd = epoll_create1(0);
struct epoll_event ev = { .events = EPOLLIN, .data.fd = sockfd };
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);   // 只登记一次

struct epoll_event ready[64];
while (1) {
    int n = epoll_wait(epfd, ready, 64, -1);    // 只返回就绪的
    for (int i = 0; i < n; i++) handle(ready[i].data.fd);
}
```

## 易错点
- 以为 epoll 在任何场景都更快；连接很少或几乎都活跃时，差距不明显
- 以为 epoll 没有任何开销；登记 fd 需要系统调用，也要占内核内存
- 用 ET 模式却只读一次数据，剩余数据不会再通知，连接会卡住

## 追问
### [f1] LT 和 ET 有什么区别？
LT 只要还有数据没读完就会反复通知；ET 只在状态变化时通知一次，所以要一次读完，并配合非阻塞 IO。

### [f2] epoll 一定比 select 快吗？
不一定。监听的 fd 很少，或者大部分都活跃时，select 的全量拷贝和遍历开销不大，差距不明显。epoll 的优势在连接多、活跃少的场景。
