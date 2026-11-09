---
id: q_01M6ZYJ9SHXMBQ6N1VKR00T474
title: 线上 CPU 飙高该怎么排查？
type: scenario
difficulty: medium
importance: 3
category: jvm
tags: [performance-diagnosis, thread-basics]
prerequisites: [q_01M6XBGJ7GR1Y8N82N1SBW0YNR]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
先用 top 找到 CPU 高的进程，再用 top -Hp 找到最忙的线程，把线程号转成 16 进制，到 jstack 的输出里找对应线程的栈，定位到代码。

## 要点
- [kp1|3] 第一步 top 找出 CPU 占用高的 Java 进程号
- [kp2|3] 第二步 `top -Hp` 加进程号，找出进程里占用最高的线程号
- [kp3|2] 线程号转 16 进制，对应 jstack 输出里的 nid
- [kp4|2] 如果高 CPU 线程是 GC 线程，说明问题在内存，要转去排查 GC
- [kp5] 常见原因：死循环、频繁 Full GC、锁竞争引发的大量线程切换

## 详解
### 先搞懂：像找“哪个工位的人最忙”
公司整体很忙，要先找出是哪个部门（进程），再找出是哪个员工（线程），最后看他手上在干什么（线程栈）。

术语：
- **线程栈**：线程当前执行的方法调用链，能看到卡在哪一行代码；
- **nid**：jstack 输出里每个线程的操作系统线程号，用 16 进制表示。

### 步骤
1. `top` 找出 CPU 高的进程，记下进程号 pid；
2. `top -Hp <pid>` 列出该进程下各线程的 CPU 占用，记下最高的线程号 tid（十进制）；
3. 把 tid 转成 16 进制：`printf '%x\n' <tid>`；
4. `jstack <pid>` 导出线程栈，在输出里找 `nid=0x<十六进制号>` 的线程；
5. 阅读该线程的栈，找到对应的业务代码。
6. 再看是不是死循环、复杂计算或其他异常逻辑。

### 找不到业务代码时：想想 GC
如果最忙的线程名字像 GC 线程，说明 CPU 高是 GC 引起的。通常是内存不足、频繁 Full GC。这时候要用 `jstat` 观察 GC，按内存问题排查。

### 常见原因
| 原因 | 现象 |
|---|---|
| 死循环或空转 | 同一线程长期占满一个核 |
| 频繁 Full GC | 高占用的是 GC 线程 |
| 锁竞争、线程数过多 | 大量线程在运行与等待间切换 |

## 示例
```bash
top                          # 找到进程号，如 12345
top -Hp 12345                # 找到最高的线程，如 12399
printf '%x\n' 12399          # 得到 306f
jstack 12345 | grep -A 20 'nid=0x306f'
```

## 易错点
- 忘记转 16 进制；jstack 里的 nid 是 16 进制，直接用十进制搜不到
- 只看一次快照；线程状态瞬间变化，最好间隔几秒多导出几次对比
- 看到 CPU 高就认定业务代码有问题；也可能是 GC 在忙

## 追问
### [f1] 线程栈里 RUNNABLE 的线程一定在占 CPU 吗？
不一定。线程在等待网络或磁盘 IO 时，栈上也可能显示 RUNNABLE，要结合 `top -Hp` 的 CPU 占用一起判断。
