---
id: q_01M6ZYJCFV59XKPADBT1X4Y8N9
title: interrupt()、isInterrupted() 和 interrupted() 有什么区别？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [thread-basics]
prerequisites: [q_01M6ZYJBYWHKJBZNEY2QQ461ZA]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：Thread（interrupt、isInterrupted、interrupted）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html" }
---

## 一句话
interrupt() 是给线程设置中断标志；isInterrupted() 只读取标志、不清除；静态方法 interrupted() 读取当前线程的标志并把它清除。

## 要点
- [kp1|3] interrupt()：设置目标线程的中断标志为 true
- [kp2|3] isInterrupted()：实例方法，只读标志，不改变它
- [kp3|2] interrupted()：静态方法，读取当前线程的标志并清除（置回 false）
- [kp4|2] interrupted() 看的永远是调用它的当前线程，不是某个 Thread 对象
- [kp5] 阻塞方法抛 InterruptedException 时，也会把标志清除

## 详解
### 先搞懂：标志就像一张便利贴
把中断标志想成贴在线程身上的一张便利贴，上面写着「有人请你停下」。

- `interrupt()`：别人往你身上贴一张便利贴；
- `isInterrupted()`：看一眼有没有便利贴，看完放着不动；
- `interrupted()`：看一眼有没有便利贴，并且把它撕掉。

后文用到的几个词：
- **中断标志**：线程内部的布尔值，true 表示被请求中断。
- **实例方法 / 静态方法**：实例方法通过线程对象调用，静态方法属于类，作用于当前正在执行的线程。

### 三个方法逐个看
**interrupt()**：实例方法，对目标线程设置标志。如果目标线程正阻塞在 `sleep`、`wait`、`join`，会被唤醒并抛 `InterruptedException`。

**isInterrupted()**：实例方法，返回目标线程的标志，调用多少次结果都一样，不会修改标志。适合在循环条件里反复检查。

**interrupted()**：静态方法，检查「当前线程」的标志，返回后立刻清除。所以连续调用两次，第二次通常返回 false。

### 方案对比：三个方法一览
| 方法 | 类型 | 作用对象 | 是否修改标志 | 返回值 |
|---|---|---|---|---|
| `interrupt()` | 实例 | 目标线程 | 置为 true | 无 |
| `isInterrupted()` | 实例 | 目标线程 | 不修改 | 当前标志 |
| `interrupted()` | 静态 | 当前线程 | 读后清除 | 清除前的标志 |

结论：循环里判断是否要退出用 `isInterrupted()`；只有想「消费」掉这次中断时才用 `interrupted()`。

### 进阶：为什么要清除标志
抛 `InterruptedException` 的同时清除标志，是因为异常本身已经把中断信息传递出去了。如果捕获后想让上层仍然感知，要自己调用 `Thread.currentThread().interrupt()` 重新设置标志。

## 示例
```java
Thread t = new Thread(() -> {
    while (true) {
        if (Thread.currentThread().isInterrupted()) {
            System.out.println("被中断了，退出");
            break;
        }
    }
});
t.start();
t.interrupt();
System.out.println(t.isInterrupted()); // 只读标志，不会清除
```

## 易错点
- 在其他线程里写 `t.interrupted()` 以为检查 t 线程；它是静态方法，检查的是调用者自己
- 用 interrupted() 当普通检查，导致标志被清掉，后续代码看不到中断
- 以为 interrupt() 返回的是旧标志；它没有返回值

## 追问
### [f1] 线程已经结束，对它调用 interrupt() 会怎样？
不会抛异常。规范说这不一定有任何效果；JDK 参考实现仍会记下这次中断，`isInterrupted()` 可能返回 true。

### [f2] 捕获 InterruptedException 后应该怎么处理？
能结束任务就直接退出；做不到的话调用 `Thread.currentThread().interrupt()` 恢复标志，让上层知道。不要空 catch 吞掉。
