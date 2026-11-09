---
id: q_01M6XCC656D3DVNWQFDAHFQ5M4
title: "@Aspect 和 @Around 怎么写一个切面？"
type: concept
difficulty: easy
importance: 2
category: spring
tags: [aop]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
写一个类标上 `@Aspect` 和 `@Component`，在方法上用 `@Around` 加切点表达式；方法里调用 `proceed()` 执行原方法，前后可以加自己的逻辑。

## 要点
- [kp1|3] `@Aspect` 标注切面类，它还要交给 Spring 管理，如加 `@Component`
- [kp2|3] `@Around` 的参数是切点表达式，决定拦截哪些方法
- [kp3|2] 环绕通知的参数是 `ProceedingJoinPoint`，调用 `proceed()` 才会执行原方法
- [kp4] 环绕通知要把 `proceed()` 的返回值返回，否则调用方拿到空

## 详解
### 先搞懂：不改业务代码，给方法加一层包装
项目里常有这样的需求：每个接口都要记录耗时、打日志、检查权限。如果每个方法里都写一遍，代码又多又乱。

可以把它想成商品出库前的统一检查站：商品（业务方法）本身不变，但每件都先过一遍检查站（切面）。AOP 就是让这类通用逻辑集中写在一处，Spring 自动把它套到目标方法上。

后文用到的术语：

- **切面**：放通用逻辑的那个类；
- **切点**：用表达式描述要拦截哪些方法；
- **通知**：拦截之后要做的事，`@Around` 是其中一种；
- **目标方法**：被拦截、被包装的业务方法。

### 写法：三步
1. 在类上加 `@Aspect` 和 `@Component`。只有 `@Aspect` 不够，Spring 要先把它当成 Bean 才会生效。
2. 在方法上加 `@Around("切点表达式")`，常用 `execution(...)` 匹配某个包下的方法。
3. 方法参数写 `ProceedingJoinPoint`，在需要的位置调用 `proceed()` 执行目标方法。

### @Around：能完全控制目标方法
`@Around` 比 `@Before`、`@After` 更灵活：

- `proceed()` 之前的代码，相当于前置逻辑；
- `proceed()` 之后的代码，相当于后置逻辑；
- 可以决定要不要调用 `proceed()`，也能修改返回值、捕获异常。

所以记录耗时这类需要「前后都有动作」的场景，最适合用它。

## 示例
```java
@Aspect
@Component
public class TimeAspect {

    @Around("execution(* com.example.service..*.*(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed(); // 执行目标方法，并把结果返回
        } finally {
            long cost = System.currentTimeMillis() - start;
            System.out.println(pjp.getSignature() + " 耗时 " + cost + "ms");
        }
    }
}
```

## 易错点
- 忘记调用 `proceed()`，目标方法根本不会执行
- 调用了 `proceed()` 却不返回结果，调用方拿到的是 null
- 同一个类里的方法互相调用，不经过代理，切面不会生效
- 只写 `@Aspect` 没有交给 Spring 管理，切面不生效

## 追问
### [f1] @Around 和 @Before、@After 有什么区别？
`@Before` 只能在方法前执行，`@After` 只能在方法后执行。`@Around` 包住整个调用，能控制目标方法是否执行，也能改返回值。

### [f2] Spring AOP 靠什么实现？
靠动态代理：目标类有接口时通常用 JDK 动态代理，否则用 CGLIB 生成子类。Spring Boot 默认优先使用 CGLIB。
