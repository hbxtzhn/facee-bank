---
id: q_01M6XBH6HXW7SNAMD7FB870PBC
title: 什么是构造器注入？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [ioc-di]
prerequisites: [q_01M6XBH69B62C0G3H54M5E4X7D]
appliesTo: ["Spring Framework >= 4.3"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
references:
  - { title: "Spring Framework 参考文档：Dependency Injection（构造器注入与 setter 注入、循环依赖）", url: "https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html" }
  - { title: "Spring Framework 4.3 参考文档：Annotation-based container configuration（@Autowired，单构造器可省略）", url: "https://docs.spring.io/spring-framework/docs/4.3.x/spring-framework-reference/html/beans.html" }
---

## 一句话
构造器注入就是把依赖作为构造方法的参数传进来，对象一创建完，需要的依赖就已经齐全，Spring 官方也推荐优先使用它。

## 要点
- [kp1|3] 依赖通过构造方法的参数传入，对象创建时依赖就已就绪
- [kp2|3] 依赖字段可以声明为 final，对象创建后不会被改动
- [kp3|2] 类只有一个构造器时，Spring 4.3 起可以省略 @Autowired
- [kp4] 依赖没有准备好时，容器启动阶段就会报错，问题暴露得早

## 详解
### 先搞懂：入职时电脑就配好
员工入职第一天，行政就把电脑配好放在工位上，员工一到岗就能直接工作。构造器注入就是这样：对象被创建出来的那一刻，它要用的依赖已经传进来了。

后文用到的词：
- **构造器（构造方法）**：创建对象时执行的方法。
- **依赖**：这个对象要用的其他对象。
- **final 字段**：赋值一次后不能再改的字段。

### 构造器注入怎么工作
1. Spring 找到类的构造方法，看它需要哪些参数；
2. 从容器里找到（或先创建）这些参数对应的 Bean；
3. 调用构造方法，把它们传进去，得到完整的对象。

因为是在创建对象时一次传入，对象没有「依赖还没设置」的中间状态，使用起来更安全。

### 为什么推荐
- **依赖不可变**：字段可以写成 `final`，之后没人能偷偷换掉；
- **不会拿到半成品**：对象创建出来时依赖已经齐全，不会遇到空指针；
- **依赖一目了然**：看构造方法参数就知道这个类依赖谁；参数多得离谱，也在提醒这个类职责太重；
- **方便测试**：不用 Spring，直接 `new` 并传入假对象即可。

### 注意事项
- Spring 4.3 起，如果类只有一个构造器，可以省略 `@Autowired`；有多个构造器时，需要在要使用的构造器上标注 `@Autowired`；
- 两个 Bean 通过构造器互相依赖，会形成无法解决的循环依赖，容器启动时会抛出异常。

## 示例
```java
@Service
public class OrderService {
    private final UserDao userDao;
    private final PayClient payClient;

    // 只有一个构造器，可以省略 @Autowired
    public OrderService(UserDao userDao, PayClient payClient) {
        this.userDao = userDao;
        this.payClient = payClient;
    }
}
```

## 易错点
- 以为必须写 @Autowired；单构造器时可以省略（Spring 4.3 起）
- 两个 Bean 的构造器互相依赖，容器无法创建，启动失败
- 构造方法参数越来越多还硬塞，应该先考虑拆分类

## 追问
### [f1] 构造器注入和 setter 注入怎么选？
必需的依赖用构造器注入，保证对象创建时就完整；可选的、可能变化的依赖可以用 setter 注入。

### [f2] 构造器注入为什么能暴露循环依赖？
A 的构造器要 B，B 的构造器又要 A，谁都无法先被创建出来，容器启动时会直接报循环依赖的错误，这样问题在启动阶段就发现了。
