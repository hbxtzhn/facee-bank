---
id: q_01M6XBPB0NBQ01A9JZ6QWXJPF5
title: 怎么用 AOP 实现操作日志记录？
type: scenario
difficulty: medium
importance: 2
category: spring
tags: [aop]
prerequisites: [q_01M6XBH92BND8EYH9T6RE07YES]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
自定义一个注解标在要记录的方法上，用切点选中它，在环绕通知里取出类、方法、参数、请求信息，执行完再把日志存进数据库。

## 要点
- [kp1|3] 用自定义注解加 `@annotation` 切点，精确选中要记录的方法
- [kp2|3] 用环绕通知包住目标方法，前后都能拿到信息
- [kp3|2] 通过 `ProceedingJoinPoint` 取类名、方法名、参数和注解内容
- [kp4|2] 通过 `RequestContextHolder` 取请求路径、方式、IP
- [kp5] 日志入库建议异步，别拖慢主流程

## 详解
### 先搞懂：不改业务代码也能记录“谁做了什么”
后台系统常要求记录操作日志：谁在什么时间改了哪条数据。如果每个方法都手写一段保存日志的代码，既重复又容易漏。用 AOP 的话，只需要在方法上贴一个标签，日志逻辑集中写在一个切面里。

后文术语：
- **自定义注解**：自己定义的标签，用来标记哪些方法需要记录。
- **环绕通知**：包住目标方法的通知，可以在前后做事。
- **切点**：挑选被增强方法的条件。

### 实现步骤
1. **定义注解**：比如 `@OperLog`，里面放操作描述、模块名。
2. **写切面**：切点用 `@annotation(OperLog)` 选中被标记的方法。
3. **环绕通知里取信息**：从 `ProceedingJoinPoint` 取类名、方法名、参数；从注解取描述；从当前请求取路径、请求方式、IP；从登录态取操作人。
4. **执行目标方法**：调用 `proceed()`，记下耗时和结果。
5. **异常也要记录**：用 `try/catch` 捕获异常，记录失败状态后再抛出。
6. **保存**：把日志对象写入数据库。

### 几点注意
- 参数里可能有密码、文件流，保存前要脱敏或过滤。
- 日志入库失败不能影响业务，应当捕获异常。
- 日志量大时，可以放进线程池或消息队列异步写入。

## 示例
```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface OperLog {
    String value();
}

@Aspect
@Component
public class OperLogAspect {
    @Around("@annotation(operLog)")
    public Object around(ProceedingJoinPoint pjp, OperLog operLog) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();
        long cost = System.currentTimeMillis() - start;
        String method = pjp.getSignature().toShortString();
        // 保存日志：描述、方法、参数、耗时
        logService.save(operLog.value(), method, pjp.getArgs(), cost);
        return result;
    }
}
```

## 易错点
- 环绕通知里忘记返回 `proceed()` 的结果，接口返回 null
- 只在正常返回时记录，方法抛异常时没有日志
- 直接把全部参数入库，把密码也存了
- 日志同步写库且不处理异常，数据库故障拖垮业务

## 追问
### [f1] 为什么用注解切点而不是包路径切点？
注解切点由业务方法自己决定是否记录，范围清楚、可以带描述信息；包路径切点范围大，容易把不需要的方法也记录进来。
