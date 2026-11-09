---
id: q_01M6XBH8EVVJ781F6BQC0TEHFV
title: Spring 可以解决哪些形式的循环依赖？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [bean-lifecycle]
prerequisites: [q_01M6XBH6HXW7SNAMD7FB870PBC, q_01M6XBH86GH1KK78ZH866Y0TVW]
appliesTo: ["Spring Boot >= 2.6（默认禁止循环引用）"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Spring Framework 参考文档：Dependency Injection（Circular dependencies）", url: "https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html" }
  - { title: "Spring Boot 2.6 Release Notes：Circular References Prohibited by Default", url: "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-2.6-Release-Notes" }
  - { title: "Spring Framework Javadoc：@Lazy（注入点上的懒解析代理）", url: "https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Lazy.html" }
---

## 一句话
单例 Bean 用 setter 或字段注入形成的循环依赖 Spring 能解决，两边都用构造器注入的不能；混用时取决于谁先被创建。

## 要点
- [kp1|3] 两个 Bean 都是构造器注入：解决不了，启动报错
- [kp2|3] 两个 Bean 都是 setter 或字段注入：能解决
- [kp3|2] 混用时看创建顺序：先创建的那个必须不是构造器注入
- [kp4|2] prototype 作用域的循环依赖解决不了
- [kp5] 构造器注入的环可以在参数上加 @Lazy 打破

## 详解
### 先搞懂：能不能解决，看“能不能先露个脸”
Spring 解决循环依赖的思路是：先 new 出一个对象（还没填依赖），提前“露个脸”放到缓存里，让别人先拿去引用，自己稍后再补齐依赖。

- 用 setter 或字段注入：对象可以先 new 出来（调用无参构造），之后再注入依赖，所以能提前露脸。
- 用构造器注入：new 对象这一步就要拿到依赖，对象还没造出来就没法露脸，环就卡死了。

后文术语：
- **提前曝光**：对象刚创建、还没注入属性时就放进缓存。
- **构造器注入**：依赖作为构造方法参数传入。

### 各种组合一览
| A 的注入方式 | B 的注入方式 | 结果 | 原因 |
|---|---|---|---|
| 构造器 | 构造器 | 失败 | 谁都造不出来 |
| setter/字段 | setter/字段 | 成功 | 两者都能提前曝光 |
| setter/字段 | 构造器 | 成功（A 先创建时） | A 先曝光，B 构造时能拿到 A |
| 构造器 | setter/字段 | 失败（A 先创建时） | 创建 A 要先造 B，B 要 A，但 A 还没曝光 |

结论：只要环里先被创建的那个 Bean 不依赖构造器注入，就能成功。

### 为什么跟创建顺序有关
Spring 一般按 Bean 定义被注册的顺序创建单例，所以通常 A 先于 B。最后两行的差别就来自这里：如果创建顺序反过来，结果也会反过来。这种“看运气”的写法不可靠，不要依赖。

### 进阶：版本与手段
- Spring Boot 2.6 起，默认连能解决的循环引用也禁止，需配置 `spring.main.allow-circular-references=true`。
- 构造器注入的环，可以在其中一个构造参数上加 `@Lazy`，Spring 会注入一个代理，等真正调用时才取目标对象。

## 易错点
- 以为只要是单例就都能解决；构造器注入的环不行
- 以为“A 先创建”和“B 先创建”结果一样；混用时顺序决定成败
- 以为 prototype 也能靠缓存解决；prototype 不缓存，直接报错

## 追问
### [f1] 为什么构造器注入的环不能靠缓存解决？
提前曝光的前提是对象已经被 new 出来；构造器注入时 new 这一步就需要依赖，对象都不存在，没东西可曝光。
