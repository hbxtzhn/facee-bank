---
id: q_01M6XBG49186RD6CSF88AV1WET
title: 什么是反射？
type: concept
difficulty: easy
importance: 3
category: java
tags: [reflection]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
反射是程序在运行时读取一个类的结构（类名、字段、方法、构造器）并直接调用它们，不必在写代码时就把类型写死。

## 要点
- [kp1|3] 反射能在运行时获取类的字段、方法、构造器等信息
- [kp2|3] 入口是 Class 对象，可通过 Class.forName、类名.class、对象.getClass() 获得
- [kp3|2] 可以通过反射创建对象、调用方法、读写字段（包括 private，需放开访问）
- [kp4|2] Spring、Jackson、MyBatis 等框架大量使用反射
- [kp5] 反射有一定性能开销，也会绕过封装，不宜滥用

## 详解
### 先搞懂：不知道名字也能叫人办事
平常写代码像是“我知道同事叫张三，直接找他”。反射像是“我拿到一份花名册，按名册上的信息去找人、让他做事”：类名甚至可以是配置文件里的一个字符串，程序运行时才决定用哪个类。

做项目时，Spring 根据配置创建对象、Jackson 把 JSON 填进你的对象，用到的都是这种能力。

后文术语：
- **Class 对象**：每个类加载后在 JVM 里都有一个 Class 对象，记录这个类的结构信息。
- **Method、Field、Constructor**：分别代表方法、字段、构造器。

### 怎么拿到 Class 对象
三种常见写法：
- `Class.forName("com.demo.User")`：用类的全名字符串，最灵活；
- `User.class`：编译时已知类；
- `user.getClass()`：已经有对象。

### 拿到之后能做什么
- `getDeclaredFields()`、`getDeclaredMethods()`、`getDeclaredConstructors()` 读取结构；
- `newInstance` 类的操作用构造器：`constructor.newInstance(...)` 创建对象；
- `method.invoke(对象, 参数)` 调用方法；
- `field.get / field.set` 读写字段。private 成员要先调用 `setAccessible(true)`，在新版本 Java 的模块系统下，对 JDK 内部类这样做可能被限制。

### 它的代价
反射调用比直接调用多了查找和检查，性能一般更差；还能绕过 private，破坏封装；编译器也检查不了写错的名字，错误到运行时才暴露。所以业务代码里能直接调用就不用反射，框架才大量使用。

## 示例
```java
Class<?> clazz = Class.forName("com.demo.User");
Object user = clazz.getDeclaredConstructor().newInstance();
Method m = clazz.getMethod("setName", String.class);
m.invoke(user, "Tom");
```

## 易错点
- 以为反射一定能访问 private 成员；放开访问可能被安全限制挡住
- 方法名或参数类型写错；编译不会报错，运行时才抛 NoSuchMethodException
- 在循环里频繁用反射；每次都查找会增加开销，可以缓存 Method

## 追问
### [f1] 反射有哪些使用场景？
框架：Spring 的依赖注入、Jackson 的 JSON 转换、MyBatis 的结果映射；以及动态代理、读取注解等。
