---
id: q_01M6XBPC9HH4DNDNTVR5XSEA1V
title: 声明式事务的代理对象是在哪一步创建的？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [transaction-management, bean-lifecycle]
prerequisites: [q_01M6XBHD5MJC4VZFMFPVN4VMKC]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Spring Framework 参考文档：Container Extension Points（BeanPostProcessor）", url: "https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html" }
  - { title: "Spring Framework 参考文档：Using @Transactional（代理模式与自调用）", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html" }
---

## 一句话
事务代理在 Bean 初始化之后创建：BeanPostProcessor 发现 Bean 匹配事务切面，就把它替换成代理对象。

## 要点
- [kp1|3] 代理在 Bean 初始化之后，由 BeanPostProcessor 创建
- [kp2|3] 创建时查找与当前 Bean 匹配的切面，事务切面匹配到 @Transactional 就生成代理
- [kp3|2] 容器最终放进去、别人注入到的，是代理对象而不是原始对象
- [kp4] 存在循环依赖时，代理可能提前在属性注入阶段创建

## 详解
### 先搞懂：Bean 出厂前的“加工站”
Spring 创建一个 Bean 大致分几步：先 new 出对象，再注入属性，再执行初始化方法。之后还有一道“加工站”。所有的 **BeanPostProcessor** 会依次再加工一遍。加工后的结果，才是最终放进容器的对象。

可以想成产品出厂前的包装环节：东西做好了，包装车间根据规格（有没有事务注解）决定要不要套上一层保护壳（代理）。

后文用到的术语：
- **BeanPostProcessor**：Bean 后置处理器，在 Bean 创建过程中对它做二次加工。
- **切面（Advisor）**：描述“哪些方法要被拦截、拦截后做什么”的规则；事务就是一个切面。
- **自动代理创建器**：一类特殊的后置处理器，专门负责给匹配的 Bean 创建代理。

### 代理是怎么创建出来的
1. **启用事务管理**：`@EnableTransactionManagement`（Spring Boot 会自动配置）会向容器注册自动代理创建器和事务切面；
2. **单例 Bean 初始化完成后**：Spring 遍历所有 `BeanPostProcessor`，执行它们的 `postProcessAfterInitialization` 方法；
3. **查找匹配的切面**：自动代理创建器检查容器里的所有切面，看哪些适用于当前 Bean；事务切面会检查类或方法上有没有 `@Transactional`；
4. **有匹配就创建代理**：把原始对象包装成代理对象并返回；没有匹配就直接返回原对象；
5. **放入容器**：最终放入容器的，是这个返回值。别的 Bean 注入它时，拿到的就是代理。

### 调用时的流程
外部调用代理对象的方法时，代理先经过事务拦截器：开启事务，调用原始对象的方法，再提交或回滚。

### 进阶：循环依赖时的提前代理（基础薄弱可先跳过）
如果 A 和 B 互相依赖，Spring 为了解决循环依赖，会把一个“提前拿到引用”的入口放进三级缓存。别的 Bean 需要 A 时，通过这个入口提前得到 A 的引用；如果 A 需要被代理，这时就会提前创建代理，而不是等到初始化之后。这样保证注入到 B 里的是代理对象，而不是原始对象。

## 易错点
- 以为代理是在 Bean 实例化时（`new` 的那一步）创建的；它是在初始化之后由后置处理器创建的
- 以为容器里保存的是原始对象；对需要事务的 Bean，容器里存的是代理对象
- 以为所有 Bean 都会被代理；没有匹配切面的 Bean 返回的是原对象

## 追问
### [f1] 为什么自己 new 出来的对象没有事务？
它不是 Spring 容器创建的，没有经过 BeanPostProcessor 的加工，也就没有代理，所以事务注解不会生效。

### [f2] 自调用事务失效和这个创建过程有什么关系？
容器里的 Bean 是代理，代理内部包着原始对象。原始对象里的 `this` 指向它自己，不是代理，所以内部调用绕开了代理。
