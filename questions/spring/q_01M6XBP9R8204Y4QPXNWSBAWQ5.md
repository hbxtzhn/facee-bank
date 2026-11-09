---
id: q_01M6XBP9R8204Y4QPXNWSBAWQ5
title: 什么是织入（Weaving），Spring 在什么时候完成织入？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [aop, dynamic-proxy]
prerequisites: [q_01M6XBH9ANRF17HRQG1CR2B9DE]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Spring Framework 参考文档：AOP Concepts（Weaving 的定义）", url: "https://docs.spring.io/spring-framework/reference/core/aop/introduction-defn.html" }
  - { title: "Spring Framework 参考文档：Proxying Mechanisms（运行时代理、内部调用）", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
---

## 一句话
织入就是把切面的逻辑应用到目标对象、生成代理的过程；Spring AOP 在运行时、Bean 创建完成后通过代理完成织入。

## 要点
- [kp1|3] 织入是把切面逻辑加到目标对象上的过程
- [kp2|3] Spring AOP 是运行时织入，靠动态代理实现
- [kp3|2] 具体在 Bean 初始化之后，由后置处理器生成代理并替换原对象
- [kp4] AspectJ 还支持编译期和类加载期织入

## 详解
### 先搞懂：织入就是“把增强缝进去”
切面是一份说明书，目标对象是原来的业务类。织入就像把说明书上的要求缝进衣服里：缝完之后，调用的人拿到的是“带增强的版本”。

后文术语：
- **目标对象**：被增强的原始 Bean。
- **代理对象**：Spring 生成的包装对象，调用时先走切面逻辑，再转给目标对象。
- **后置处理器**：在 Bean 创建过程中介入、可以替换对象的扩展点。

### 织入可以发生在哪些时刻
- **编译期**：编译源码时就把切面代码织进去（AspectJ 编译器）。
- **类加载期**：类被加载进 JVM 时修改字节码（AspectJ 的加载时织入）。
- **运行期**：程序运行中生成代理对象来增强（Spring AOP）。

### Spring 在什么时候织入
容器创建 Bean 时，先实例化、注入属性、执行初始化。初始化完成后，一个叫自动代理创建器的后置处理器会检查这个 Bean 是否被某个切点选中。选中了，就生成代理对象，容器里最终放的是代理，而不是原对象。

所以别的 Bean 注入它时，拿到的就是代理，调用方法自然会先经过通知。

### 为什么选运行期
运行期织入不需要特殊编译器或启动参数，用普通 Java 编译就行，使用成本低。代价是只能增强通过代理调用的方法。

## 易错点
- 以为织入会改写原来的类；Spring 是生成新的代理对象，原类不变
- 以为编译期就完成织入；Spring AOP 是在运行时
- 以为类内部方法互相调用也会被织入；内部调用不经过代理

## 追问
### [f1] 为什么同类内部调用 @Transactional 方法不生效？
内部调用用的是 this，也就是原对象，没有经过代理，通知不会触发。可以把方法拆到另一个 Bean 里，或注入自身代理来调用。
