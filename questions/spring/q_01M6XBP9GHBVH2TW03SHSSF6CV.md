---
id: q_01M6XBP9GHBVH2TW03SHSSF6CV
title: 解决循环依赖为什么需要三级缓存，只用二级缓存不行吗？
type: concept
difficulty: hard
importance: 3
category: spring
tags: [bean-lifecycle, dynamic-proxy]
prerequisites: [q_01M6XBH86GH1KK78ZH866Y0TVW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "Spring Framework 源码：AbstractAutoProxyCreator（getEarlyBeanReference、postProcessAfterInitialization）", url: "https://github.com/spring-projects/spring-framework/blob/main/spring-aop/src/main/java/org/springframework/aop/framework/autoproxy/AbstractAutoProxyCreator.java" }
  - { title: "Spring Framework 源码：AbstractAutowireCapableBeanFactory（getEarlyBeanReference 与原始版本被注入的异常）", url: "https://github.com/spring-projects/spring-framework/blob/main/spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java" }
---

## 一句话
三级缓存里的工厂能延迟决定“提前暴露的是原始对象还是 AOP 代理”，保证没有循环依赖的 Bean 仍在初始化之后才生成代理；只用二级缓存就得改变这个设计。

## 要点
- [kp1|3] 三级缓存放的是 ObjectFactory，调用时才决定早期引用是原始对象还是代理
- [kp2|3] 正常情况下，AOP 代理在 Bean 初始化完成之后才生成
- [kp3|2] 发生循环依赖时，需要把代理提前到依赖注入阶段生成
- [kp4|2] 二级缓存保证多次获取早期引用拿到同一个对象
- [kp5] 只用二级缓存，要么所有 Bean 都提前生成代理，要么早期引用可能不是最终对象

## 详解
### 先搞懂：问题出在“代理”
打个比方：A 是个员工，需要“经理代理人”（AOP 代理）替他对外办事。通常是 A 办好入职（初始化）后，才给他配代理人。但如果 B 在 A 入职前就要找 A，B 拿到的应该是代理人，而不是 A 本人，否则 B 绕过了代理（比如事务、日志不生效）。

后文术语：
- **AOP 代理**：Spring 生成的包装对象，调用方法时先执行切面逻辑。
- **早期引用**：Bean 还没创建完成就被别人拿去用的那个对象。
- **后置处理器**：在 Bean 创建过程的各个阶段介入、可以替换对象的扩展点，AOP 代理就由它生成。

### 工厂做了什么
在三级缓存里存放的 ObjectFactory，被调用时执行 `getEarlyBeanReference`。如果这个 Bean 需要被 AOP 代理，就在这时提前生成代理并返回；不需要代理就返回原始对象。生成过的代理会记录下来，等初始化之后不会再重复生成。

没有循环依赖时，这个工厂根本不会被调用，代理仍按常规流程在初始化之后创建。

### 二级缓存的作用
同一个早期对象可能被多个 Bean 依赖。第一次通过工厂拿到早期引用后放进二级缓存，之后再来取的 Bean 直接从二级拿，保证拿到的是同一个对象，不会反复生成多个代理。

### 方案对比：只用二级缓存会怎样
| 假设方案 | 做法 | 问题 |
|---|---|---|
| 二级缓存只放原始对象 | 暴露原始半成品 | 依赖方拿到原始对象，后面 Bean 被替换成代理，两边不是同一个对象 |
| 二级缓存直接放代理 | 实例化后立刻为所有 Bean 提前生成代理 | 没有循环依赖的 Bean 也提前生成代理，违背“初始化后再生成代理”的设计 |
| 三级缓存（Spring 实际做法） | 放工厂，被依赖时才决定 | 多一层结构，换来延迟决定 |

结论：不是说技术上绝对做不到，而是为了让只有真正发生循环依赖的 Bean 才提前生成代理，其余保持正常生命周期。

### 进阶：原始对象泄露时会怎样
如果某个 Bean 的早期引用（原始对象）已经被别人拿走，而它在初始化阶段又被后置处理器包装成另一个对象（例如 `@Async` 生成的代理），就会出问题。Spring 会发现最终对象与早期引用不一致。它会抛出 `BeanCurrentlyInCreationException`，提示该 Bean 的原始版本已被注入到其他 Bean。

## 易错点
- 以为只有三级缓存才能解决循环依赖；关键是提前暴露，三级缓存是为了保持代理生成时机
- 以为所有 Bean 都会提前生成代理；只有发生循环依赖时才会
- 以为二级缓存没用；它保证同一个早期引用只生成一次

## 追问
### [f1] 如果循环依赖里的 Bean 带事务，事务能生效吗？
能。早期引用阶段已经按需生成了代理，依赖方拿到的是代理，调用时事务通知会生效。

### [f2] 为什么说“代理在初始化之后生成”？
Spring 通过后置处理器在 Bean 初始化完成后（`postProcessAfterInitialization`）判断是否需要代理并替换对象，这是 AOP 与生命周期结合的默认位置。
