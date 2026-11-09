---
id: q_01M6XBP202CWSPAPYM5DVTYYMA
title: JDK 1.7 和 1.8 的内存区域有什么变化？
type: concept
difficulty: medium
importance: 3
category: jvm
tags: [memory-area]
appliesTo: ["Java 7 与 Java 8 的对比"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
JDK 1.7 有永久代，放在 JVM 堆里；JDK 1.8 把永久代去掉，改用元空间存放类信息，元空间使用本地内存，不再受堆大小限制。

## 要点
- [kp1|3] JDK 1.7 方法区由永久代实现，JDK 1.8 起改由元空间实现
- [kp2|3] 元空间使用操作系统的本地内存，永久代属于 JVM 堆内存
- [kp3|2] 永久代满了抛 OutOfMemoryError: PermGen space，元空间满了抛 Metaspace
- [kp4] JDK 1.8 起，永久代相关参数（-XX:PermSize 等）不再生效，改用元空间参数

## 详解
### 先搞懂：类信息原来放“固定大小的小房间”，后来换成“按需扩大的大仓库”
JVM 加载类之后，要把类的描述信息（有哪些字段、方法等）存起来。1.7 把它们放在永久代，这是一块大小固定的区域，类加载得多就容易满。1.8 换成元空间，直接用系统的本地内存，需要多少就申请多少。

术语：
- **永久代**：1.7 里存放类信息的区域，在堆内；
- **元空间（Metaspace）**：1.8 里存放类信息的区域，在本地内存；
- **方法区**：JVM 规范里“存类信息”的逻辑区域，永久代、元空间都是它的具体实现。

### 区别对比
| 对比项 | JDK 1.7 永久代 | JDK 1.8 元空间 |
|---|---|---|
| 所在位置 | JVM 堆内存 | 本地内存 |
| 大小限制 | 受永久代参数限制 | 默认只受机器内存限制，可用参数设上限 |
| 溢出报错 | `OutOfMemoryError: PermGen space` | `OutOfMemoryError: Metaspace` |
| 调整参数 | `-XX:PermSize`、`-XX:MaxPermSize` | `-XX:MetaspaceSize`、`-XX:MaxMetaspaceSize` |

### 为什么要去掉永久代
- 永久代的大小很难估：设小了容易溢出，设大了又浪费堆内存；
- 元空间用本地内存，自动按需扩展，类加载多时也不容易溢出；
- 便于 HotSpot 与其他 JVM 的实现统一。

### 进阶：字符串常量池的变化（基础薄弱可先跳过）
字符串常量池在 JDK 7 起就从永久代挪到了堆里，所以 1.7 和 1.8 里字符串常量池都在堆中。永久代去掉之后，元空间里主要是类的元数据。元空间虽然不受堆限制，但不设上限也可能吃光机器内存，生产环境建议设置 `-XX:MaxMetaspaceSize`。

## 易错点
- 以为元空间无限大；它受机器内存限制，不设上限可能占满系统内存
- 以为 1.8 之后类加载多就不会溢出；元空间满了照样抛 `Metaspace` 的 OOM
- 在 1.8 里仍然配置 `-XX:PermSize`；该参数已无效，会被忽略并给出警告

## 追问
### [f1] 元空间溢出常见于什么场景？
动态生成类的场景，比如大量使用反射、动态代理、CGLIB，或类加载器泄漏，导致已加载的类一直不能卸载。
