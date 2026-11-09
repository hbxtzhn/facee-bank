---
id: q_01M6XBH9ANRF17HRQG1CR2B9DE
title: AOP 中的切面（Aspect）是什么？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [aop]
prerequisites: [q_01M6XBH92BND8EYH9T6RE07YES]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
切面（Aspect）就是把“在哪里增强”（切点）和“增强什么”（通知）组合在一起的模块，封装了一类横切逻辑，比如日志切面、事务切面。

## 要点
- [kp1|3] 切面 = 切点 + 通知，是 AOP 里的“一个功能模块”
- [kp2|3] 一个切面通常封装一类横切关注点，如日志、权限、事务
- [kp3|2] Spring 中用 @Aspect 标注一个类来定义切面，并交给容器管理
- [kp4] 一个切面里可以有多个切点和多个通知

## 详解
### 先搞懂：切面就像一份“增强说明书”
公司要求“凡是财务部门的文件，送出去前都要盖章并登记”。这句话里：“财务部门的文件”是挑选条件（切点），“盖章并登记”是要做的事（通知），把两者写成一份制度，就是切面。AOP 中，切面就是这样一份说明书，框架照着它去增强目标方法。

后文术语：
- **切点（Pointcut）**：挑选哪些方法要被增强的条件。
- **通知（Advice）**：被选中的方法上要执行的具体代码。

### 切面由什么组成
- **切点**：用表达式描述范围，如“service 包下所有方法”。
- **通知**：前置、后置、环绕等，写具体逻辑。

一个类里放这两样，再加上 `@Aspect` 和 `@Component`，就是一个切面。

### 举例
- 日志切面：切点选中所有 Controller 方法，通知记录请求和耗时。
- 事务切面：切点选中带 `@Transactional` 的方法，通知在方法前后开启、提交或回滚事务。

## 示例
```java
@Aspect
@Component
public class AuthAspect {
    @Pointcut("@annotation(com.demo.NeedLogin)")
    public void needLogin() {}

    @Before("needLogin()")
    public void check() {
        // 校验登录状态
    }
}
```

## 易错点
- 以为切面就是通知；通知只是切面的一部分，还需要切点来指明作用范围
- 以为只写了 @Aspect 就生效；还需要让它成为 Spring Bean（如 @Component）
- 以为一个切面只能有一个通知；可以有多个

## 追问
### [f1] 多个切面作用在同一个方法上，执行顺序怎么控制？
用 `@Order` 注解或实现 `Ordered` 接口，数值越小优先级越高，进入时越靠外层。
