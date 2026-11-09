---
id: q_01M6XBH9JS1CJS54GKKBX42MZ1
title: AOP 中的连接点（Join Point）是什么？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [aop]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
连接点（Join Point）是程序执行过程中“可以插入增强逻辑的位置”；在 Spring AOP 中，连接点就是方法的执行。

## 要点
- [kp1|3] 连接点是程序运行中能被增强的位置
- [kp2|3] Spring AOP 里连接点总是方法的执行，不支持字段访问、构造器等
- [kp3|2] 切点是从所有连接点里挑出真正要增强的那部分
- [kp4] 通知方法可以通过 JoinPoint 参数拿到方法名、参数等信息

## 详解
### 先搞懂：能下手的“所有位置”
把程序运行想成一条流水线，流水线上每个方法被调用的瞬间，都是一个“可以插手”的位置。这些位置的全体，就是连接点。就像一栋楼里所有的门，每扇门都能装一个检查岗，但你不一定每扇门都装。

后文术语：
- **切点**：从全部连接点中筛选出要装“岗”的那些门。
- **通知**：岗里具体做什么。

### 连接点和切点的关系
连接点是“候选位置”，切点是“选中的位置”。比如项目里有 200 个方法，就有 200 个候选连接点，切点表达式 `execution(* com.demo.service..*.*(..))` 从中选出 service 包下的方法。

### Spring AOP 的限制
完整的 AOP 框架（如 AspectJ）里，连接点还可以是字段读写、构造器调用等。Spring AOP 基于动态代理，只能拦截方法调用，所以连接点只有“方法执行”这一种。

### 在代码里怎么拿到
通知方法可以接收 `JoinPoint` 参数（环绕通知用 `ProceedingJoinPoint`），从中读取方法签名、入参、目标对象。

## 示例
```java
@Before("execution(* com.demo.service..*.*(..))")
public void before(JoinPoint jp) {
    System.out.println("即将执行：" + jp.getSignature().getName());
}
```

## 易错点
- 以为连接点和切点是一回事；连接点是所有候选位置，切点是筛选条件
- 以为 Spring AOP 能拦截构造器或字段访问；它只能拦截方法执行
- 以为 private 方法或内部调用也能被拦截；通过代理才会被增强，内部调用不经过代理

## 追问
### [f1] JoinPoint 和 ProceedingJoinPoint 有什么区别？
`ProceedingJoinPoint` 多了 `proceed()` 方法，能决定是否以及何时执行目标方法，只用于环绕通知。
