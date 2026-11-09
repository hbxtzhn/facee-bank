---
id: q_01M6XBH9V0BJG8R6ZEYSF2T2R4
title: AOP 中的切点（Pointcut）是什么？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [aop]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
切点（Pointcut）是一组筛选条件，用来指明切面要作用在哪些方法上，比如“某个包下所有 Service 方法”。

## 要点
- [kp1|3] 切点决定“哪些方法要被增强”
- [kp2|3] Spring 用 AspectJ 切点表达式来写，如 execution(...)
- [kp3|2] 也可以按注解选择：@annotation(自定义注解)
- [kp4] 切点可以用 @Pointcut 定义一次，多个通知复用

## 详解
### 先搞懂：从一堆方法里“点名”
项目里有几百个方法，你只想给订单模块的方法加日志。这时需要一个“点名规则”：“com.demo.order 包下所有类的所有方法”。这个规则就是切点。就像考勤只统计“研发部”，规则里写明了范围。

后文术语：
- **连接点**：所有可被增强的方法执行位置。
- **通知**：被选中的方法上要执行的逻辑。

### 常见的写法
- `execution`：按方法签名匹配。例如 `execution(* com.demo.service..*.*(..))` 表示 service 包及子包下所有类的所有方法。
- `@annotation`：匹配带某个注解的方法，例如只增强标了 `@OperLog` 的方法，这种方式灵活，控制权在业务方法上。
- `within`：按类或包匹配。
- 可以用 `&&`、`||`、`!` 组合多个条件。

### 为什么要单独定义
同一个切点可能被前置通知、后置通知同时用。用 `@Pointcut` 声明成一个方法，各个通知引用方法名即可，改范围时只改一处。

## 示例
```java
@Aspect
@Component
public class DemoAspect {
    @Pointcut("execution(* com.demo.service..*.*(..))")
    public void servicePointcut() {}

    @Before("servicePointcut()")
    public void before() {
        System.out.println("进入 service 方法");
    }
}
```

## 易错点
- 以为切点就是方法本身；切点是描述一批方法的条件表达式
- 表达式写得过宽，把不需要的方法也增强了，造成性能或行为问题
- 以为 @Pointcut 标注的方法有逻辑；它的方法体一般是空的，只是个名字

## 追问
### [f1] execution 表达式里的 `..` 是什么意思？
在包路径里，`..` 表示当前包及其所有子包；在参数列表里，`(..)` 表示任意个数、任意类型的参数。
