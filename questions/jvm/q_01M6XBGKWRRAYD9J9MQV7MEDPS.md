---
id: q_01M6XBGKWRRAYD9J9MQV7MEDPS
title: 堆和栈有什么区别？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [memory-area]
prerequisites: [q_01M6XBGKCAKJ13T2AW1YVGFSC3, q_01M6XBGKMFKPYR0RM1Z0HP4VVX]
references:
  - { title: "Java 虚拟机规范 SE 21：2.5 Run-Time Data Areas", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
堆存放对象和数组，线程共享，由 GC 回收，满了抛 OutOfMemoryError；栈存放方法调用和局部变量，线程私有，随方法返回自动释放，满了抛 StackOverflowError。

## 要点
- [kp1|3] 堆存放对象和数组，栈存放方法调用的栈帧和局部变量
- [kp2|3] 堆是线程共享的，栈是线程私有的
- [kp3|2] 堆由 GC 回收，栈帧随方法返回自动弹出，不需要 GC
- [kp4|2] 堆空间不足抛 OutOfMemoryError，栈太深抛 StackOverflowError

## 详解
### 先搞懂：堆是“公共仓库”，栈是“每人手边的小桌”
你写 `User u = new User()`：`new` 出来的对象放在公共仓库（堆）里，大家都能访问；变量 `u` 是一张写着仓库位置的小纸条，放在你自己桌上（栈）。线程走了，桌子也就清空了；仓库里的东西要等 GC 来清理。

术语：
- **堆**：放对象实例和数组；
- **栈**：每个线程有一个，存放方法调用的栈帧和局部变量；
- **GC**：垃圾回收，清理不再使用的对象。

### 方案对比：堆和栈
| 对比项 | 堆 | 栈 |
|---|---|---|
| 存放内容 | 对象实例和数组 | 局部变量、方法调用的栈帧 |
| 线程是否共享 | 所有线程共享 | 线程私有 |
| 是否被 GC 回收 | 是，GC 主要的工作区域 | 否，方法返回栈帧自动弹出 |
| 空间不足时 | `OutOfMemoryError` | `StackOverflowError` |
| 生命周期 | 对象不可达后由 GC 回收 | 随方法调用开始和结束 |

结论：对象和数组放堆，方法调用放栈；遇到报错时，看是 OOM 还是 StackOverflow，就知道是哪块区域不够。

### 为什么这样设计
- 对象可能被多个线程使用，也可能比创建它的方法活得更久，所以放在共享的堆里，等 GC 回收；
- 局部变量只属于当前方法，方法结束就没用了，放在私有的栈里，随方法返回自动释放，速度快，也天然线程安全。

### 一个常见误区
局部变量是引用类型时，栈里存的是引用（指向对象的地址），对象本身仍在堆里。

## 示例
```java
void demo() {
    int n = 10;                // n 是局部变量，在栈上
    String s = new String("a"); // s 在栈上，String 对象在堆上
}
```

## 易错点
- 以为 int 都在栈上；作为对象字段的 int，跟着对象放在堆里
- 以为栈溢出就是内存不足；栈溢出通常是调用层数过深，抛的是 StackOverflowError

## 追问
### [f1] 栈里的数据会被 GC 吗？
不会。栈帧随方法返回自动弹出，不由 GC 管理；GC 管的是堆里不再被引用的对象。
