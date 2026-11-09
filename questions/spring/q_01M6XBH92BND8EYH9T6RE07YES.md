---
id: q_01M6XBH92BND8EYH9T6RE07YES
title: 什么是 AOP（面向切面编程）？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [aop, dynamic-proxy]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
AOP 是把日志、事务、权限这类与业务无关、很多地方都要用的逻辑抽成一个独立模块，不改业务代码，就能统一加到目标方法上。

## 要点
- [kp1|3] AOP 把多处重复的横切逻辑（日志、事务、权限）抽成切面
- [kp2|3] 业务代码不用改，运行时由代理把切面逻辑织入目标方法
- [kp3|2] 核心概念：切面、连接点、切点、通知、织入
- [kp4] Spring AOP 基于动态代理，只能增强方法的执行

## 详解
### 先搞懂：每个方法都要写日志怎么办
假设有 50 个 Controller 方法，都要在执行前后打日志、统计耗时。如果每个方法都复制一段代码，改一次要改 50 处。AOP 的想法是：把这段逻辑单独写一份，然后告诉框架“把它加到这 50 个方法上”。就像小区的门禁，不用每户自己装锁，统一在大门检查。

后文术语：
- **横切关注点**：与业务无关、却散落在很多模块里的功能，比如日志、事务。
- **切面（Aspect）**：把横切逻辑集中写的那个类。
- **织入（Weaving）**：把切面加到目标方法上的过程。

### 五个核心概念
- **切面**：切点加通知的组合，封装一类横切逻辑。
- **连接点**：可以插入逻辑的位置，Spring 里就是方法的执行。
- **切点**：挑选哪些连接点要被增强的条件。
- **通知**：在切点处具体做什么，有前置、后置、环绕、异常、最终几种。
- **织入**：把以上内容应用到目标对象、生成代理的过程。

### 它带来什么
业务代码只关心业务，横切逻辑集中在一处，修改时不会遗漏；同时降低耦合，业务类不依赖日志、事务代码。Spring 中的声明式事务（`@Transactional`）就是 AOP 的典型应用。

## 示例
```java
@Aspect
@Component
public class LogAspect {
    @Around("execution(* com.demo.service..*.*(..))")
    public Object log(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            System.out.println(pjp.getSignature() + " 耗时 "
                    + (System.currentTimeMillis() - start) + "ms");
        }
    }
}
```

## 易错点
- 以为 AOP 只能用于日志；事务、权限、限流、缓存都适用
- 以为 AOP 会修改原来的类；Spring AOP 是生成代理对象，原类不变
- 以为同类内部方法调用也会被增强；内部调用不经过代理，通知不会触发

## 追问
### [f1] Spring AOP 和 AspectJ 是什么关系？
Spring AOP 基于动态代理，只能增强 Spring 管理的 Bean 的方法；AspectJ 是更完整的 AOP 框架，能在编译期或类加载期织入。Spring 借用了 AspectJ 的注解和切点表达式。
