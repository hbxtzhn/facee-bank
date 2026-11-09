---
id: q_01M6ZYJBYWHKJBZNEY2QQ461ZA
title: 什么是线程中断，interrupt() 是做什么的？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
线程中断是请求线程停下的协作机制：interrupt() 只打上中断标志，线程自己决定怎么响应；阻塞中的线程会抛 InterruptedException。

## 要点
- [kp1|3] interrupt() 只设置中断标志，不会强行终止线程
- [kp2|3] 线程在 sleep、wait、join 阻塞时被中断，会抛 InterruptedException
- [kp3|2] 线程要主动检查中断标志，并自行决定收尾退出
- [kp4] 抛出 InterruptedException 时，中断标志会被清除

## 详解
### 先搞懂：为什么不能强行杀线程
假设后台线程正在写文件，你直接把它「掐掉」，文件可能写一半，锁也没释放，数据就乱了。更稳妥的做法是礼貌地通知它：「请停下来」，它收到后先把手头的事收拾好再退出。这就是中断。

类比：同事在做事，你拍拍他肩膀说「别做了」，他决定什么时候停、怎么收尾；你不能直接拔他的电源。

后文用到的几个词：
- **中断标志**：每个线程内部有一个布尔标记，表示「是否有人请求它中断」。
- **InterruptedException**：线程在阻塞等待时发现被中断，抛出的受检异常。

### interrupt() 做了什么
对目标线程调用 `t.interrupt()`，会出现两种情况：

1. 线程正在正常运行：只是把中断标志设为 true，线程什么都不会发生，要靠线程自己检查标志；
2. 线程正阻塞在 `sleep()`、`wait()`、`join()` 等方法：这些方法会马上结束等待，抛出 `InterruptedException`，同时标志被清除。

### 线程怎么响应中断
常见写法是在循环里检查标志，发现被中断就收尾退出；捕获 `InterruptedException` 后，要么直接结束任务，要么重新调用 `Thread.currentThread().interrupt()` 把标志恢复，让上层代码也能知道。

不要「吞掉」这个异常（空的 catch），否则等于忽略了别人的停止请求。

## 示例
```java
Thread worker = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        try {
            Thread.sleep(1000);
            // 做一次任务
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); // 恢复标志
            break;
        }
    }
});
worker.start();
worker.interrupt(); // 请求停止
```

## 易错点
- 以为 interrupt() 会立刻终止线程；它只是请求，线程不配合就不会停
- catch InterruptedException 后什么都不做；停止请求被吞掉，线程停不下来
- 以为被中断后标志仍是 true；抛出异常时标志已被清除

## 追问
### [f1] 为什么不用 stop() 停止线程？
`stop()` 会强行终止线程并释放锁，可能让对象停在不一致的状态，已被废弃。应该用中断或自定义的停止标志，让线程自己收尾。
