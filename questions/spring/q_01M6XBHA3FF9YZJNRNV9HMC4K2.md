---
id: q_01M6XBHA3FF9YZJNRNV9HMC4K2
title: AOP 中的通知（Advice）是什么？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [aop]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
通知（Advice）是切面在切点处真正要执行的逻辑，按执行时机分前置、后置返回、异常、最终和环绕五类，其中环绕通知最灵活。

## 要点
- [kp1|3] 通知就是“在被选中的方法上，具体做什么”
- [kp2|3] 五种类型：@Before、@AfterReturning、@AfterThrowing、@After、@Around
- [kp3|2] 环绕通知能控制目标方法是否执行，也能改参数和返回值
- [kp4] 其他四种不能阻止目标方法执行（前置通知抛异常除外）

## 详解
### 先搞懂：在方法的哪个时刻插手
把一次方法调用想成寄快递：寄出前可以检查包裹（前置），寄出成功后可以发短信（返回后），丢件时可以报警（异常），不管成败最后都要登记（最终）。环绕则像“代寄人”，全程由他经手，可以决定寄不寄、怎么寄。

后文术语：
- **目标方法**：被增强的原始业务方法。
- **切点**：决定通知作用在哪些方法上。

### 五种通知
| 通知 | 注解 | 执行时机 |
|---|---|---|
| 前置 | `@Before` | 目标方法执行之前 |
| 返回后 | `@AfterReturning` | 目标方法正常返回之后 |
| 异常 | `@AfterThrowing` | 目标方法抛出异常之后 |
| 最终 | `@After` | 无论正常还是异常，最后都会执行 |
| 环绕 | `@Around` | 包住整个方法，自己决定何时调用目标方法 |

结论：简单需求用前置、后置等就够；需要统计耗时、改参数或返回值、统一捕获异常时用环绕。

### 环绕通知的特别之处
环绕通知的参数是 `ProceedingJoinPoint`，必须调用它的 `proceed()` 目标方法才会执行，并且要把返回值返回出去。不调用，目标方法就被拦截了；忘了返回，调用方拿到的是 null。

## 示例
```java
@Around("execution(* com.demo.service..*.*(..))")
public Object around(ProceedingJoinPoint pjp) throws Throwable {
    System.out.println("前");
    Object result = pjp.proceed();
    System.out.println("后");
    return result;
}
```

## 易错点
- 环绕通知里忘记调用 proceed()，目标方法不会执行
- 环绕通知里吞掉异常或忘记 return 结果，调用方拿到 null 或异常被吞
- 以为 @After 只在成功时执行；它无论成功失败都会执行
- 以为 @AfterReturning 能拿到异常；异常要用 @AfterThrowing

## 追问
### [f1] 同一个切面里各类通知的执行顺序是什么？
正常情况：环绕前半段、前置、目标方法、返回后（或异常）、最终、环绕后半段，具体顺序在不同 Spring 版本中略有差别，需要时以所用版本文档为准。
