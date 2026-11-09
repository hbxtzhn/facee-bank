---
id: q_01M6XBH0QCCPA9D1NRH4QB148G
title: AQS（抽象队列同步器）是什么，它的工作原理是什么？
type: concept
difficulty: hard
importance: 3
category: java-concurrency
tags: [aqs, atomic-operation]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
---

## 一句话
AQS 用一个 volatile 的 int 状态表示锁或资源，抢不到的线程排进一个先进先出的等待队列并挂起，释放时唤醒队首的后继线程。

## 要点
- [kp1|3] 核心是 volatile int 类型的 state，用 CAS 修改
- [kp2|3] 获取失败的线程封装成 Node，加入 FIFO 双向等待队列并阻塞
- [kp3|2] 释放资源时唤醒队列中的后继节点，让它重新尝试获取
- [kp4|2] 采用模板方法：子类只实现 tryAcquire、tryRelease 等，排队挂起由 AQS 完成
- [kp5] ReentrantLock、Semaphore、CountDownLatch 都基于 AQS

## 详解
### 先搞懂：排队叫号的公共框架
想象一家小餐馆：桌子是共享资源。有桌子就直接坐，没桌子就在门口拿号排队，有人吃完离开，就叫队伍最前面的人。

JDK 里有各种需要「抢资源、不行就排队」的工具：锁、信号量、倒计时门闩……它们排队的逻辑几乎一样，只有「什么算抢到」的规则不同。AQS（AbstractQueuedSynchronizer）就是把排队这部分抽成统一的框架，各个工具只填自己的规则。

后文用到的术语：

- **state**：AQS 里一个 int 变量，用数字表示资源状态。含义由子类定义，比如锁里 0 表示空闲。
- **CAS**：比较并交换，一条原子操作，用来安全地修改 state。
- **Node**：等待队列的节点，里面保存等待的线程、前后节点和等待状态。
- **挂起 / 唤醒**：让线程暂停执行、不占 CPU，以及之后把它叫醒。

### 三个核心部件
1. **state**：用 `volatile` 修饰，保证各线程都能看到最新值；修改时用 CAS，保证不会同时改乱。
2. **等待队列**：一个先进先出的双向链表，基于 CLH 队列改造。抢不到资源的线程被封装成 Node，加到队尾；队头是一个占位节点。
3. **阻塞与唤醒**：排队的线程用 `LockSupport.park()` 挂起；释放资源的线程用 `LockSupport.unpark()` 唤醒后继节点。

### 获取资源的流程
以独占模式为例，调用 `acquire`：

1. 先调用子类实现的 `tryAcquire` 尝试获取，成功就直接返回；
2. 失败，把当前线程包装成 Node 加入队尾；
3. 在队列里循环：如果自己排在队首后面第一位，就再试一次 `tryAcquire`；还是不行，就挂起；
4. 被唤醒后重新尝试，成功后把自己设为新的队头。

释放时调用 `release`：先调用子类的 `tryRelease`，成功就唤醒队列中的后继节点。

### 两种模式
- **独占模式**：同一时刻只有一个线程能拿到资源，如 ReentrantLock。
- **共享模式**：多个线程可以同时拿到，如 Semaphore、CountDownLatch。

### 对比：模板方法分工
| 角色 | 负责什么 |
|---|---|
| AQS 本身 | 排队、挂起、唤醒、中断处理 |
| 子类（实现者） | 定义 state 含义，实现 `tryAcquire` / `tryRelease`（独占），`tryAcquireShared` / `tryReleaseShared`（共享） |

结论：想自己造一个同步工具，只需要定义 state 的含义并实现 try 开头的几个方法，排队和阻塞交给 AQS。

### 进阶：版本差异（基础薄弱可先跳过）
- 队列节点之间的指针更新、等待状态的具体取值，在不同 JDK 版本里实现有调整，面试讲到「FIFO 队列加 park/unpark」即可。
- AQS 还内置了 `ConditionObject`，ReentrantLock 的多个条件队列就是基于它。

## 示例
```java
// 一个最简单的不可重入互斥锁
class Mutex {
    private static class Sync extends AbstractQueuedSynchronizer {
        @Override
        protected boolean tryAcquire(int arg) {
            if (compareAndSetState(0, 1)) {              // 0 表示空闲
                setExclusiveOwnerThread(Thread.currentThread());
                return true;
            }
            return false;
        }

        @Override
        protected boolean tryRelease(int arg) {
            setExclusiveOwnerThread(null);
            setState(0);
            return true;
        }

        @Override
        protected boolean isHeldExclusively() {
            return getState() == 1;
        }
    }

    private final Sync sync = new Sync();

    public void lock()   { sync.acquire(1); }
    public void unlock() { sync.release(1); }
}
```

## 易错点
- 以为 AQS 本身是一把锁；它是构建锁的框架，需要子类定义规则
- 以为等待队列里的线程在空转；它们是被挂起的，不占 CPU
- 以为 state 一定表示「是否被锁」；含义由子类定义，如重入次数、许可数、剩余计数
- 以为 volatile 就够了；修改 state 要用 CAS，才能保证检查和修改一起完成

## 追问
### [f1] 为什么用队列而不是让线程一直抢？
所有线程一起抢会浪费 CPU，也容易有线程一直抢不到。排队挂起既省 CPU，又让等待有顺序。

### [f2] 哪些类基于 AQS？
ReentrantLock、ReentrantReadWriteLock、Semaphore、CountDownLatch 等。
