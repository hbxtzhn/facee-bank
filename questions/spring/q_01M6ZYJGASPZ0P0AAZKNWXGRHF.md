---
id: q_01M6ZYJGASPZ0P0AAZKNWXGRHF
title: 非 public 方法上的 @Transactional 为什么会失效？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, dynamic-proxy]
appliesTo: ["Spring Framework 6.0 起支持基于类代理的 protected 和包可见方法"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：Using @Transactional（Method visibility）", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html" }
  - { title: "Spring Framework 参考文档：Proxying Mechanisms（CGLIB 限制）", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
estimatedMinutes: 3
---

## 一句话
@Transactional 靠代理拦截方法实现；private 方法代理拦不到，一定失效，事务方法应写成 public。

## 要点
- [kp1|3] 事务靠代理拦截方法调用；代理拦不到的方法，事务不会生效
- [kp2|3] private 方法无法被代理重写和调用，事务一定失效
- [kp3|2] 传统规则：只有 public 方法生效
- [kp4] Spring 6.0 起，类代理也支持 protected 和包可见方法
- [kp5] 最稳妥的做法：事务方法一律写成 public

## 详解
### 先搞懂：代理是怎么“包”住方法的
Spring 给 Bean 创建代理时，常见做法是用 CGLIB 生成一个子类，重写父类的方法。重写的方法里先开事务，再调用父类的真实方法，最后提交或回滚。

类比：保安替你接待访客，只有“对外开放的接待窗口”他才能拦截。你的私人房间在屋里面，他够不到，自然也没法在那里做登记。

后文用到的术语：
- **CGLIB 代理**：通过生成目标类的子类实现代理。
- **JDK 动态代理**：基于接口实现代理，代理只能拦到接口里声明的方法。
- **包可见**：不写访问修饰符的方法，同包内可见。

### 为什么 private 一定不行
子类无法重写父类的 `private` 方法，代理类里没有对应的“包装版本”。调用 `private` 方法时，直接执行目标类里的代码，事务拦截器根本没有机会运行。同样，`final`、`static` 方法也无法被重写，同样拿不到事务。

### 非 private 的情况，要看版本和代理方式
- **JDK 动态代理**：只能拦截接口里声明的方法，而接口方法本来就是 public。
- **CGLIB 代理**：以前 Spring 默认只给 public 方法加事务；Spring 6.0 起，基于类的代理也支持 protected 和包可见方法。
- 不同版本、不同代理方式的行为不完全一致，不去记细节，写成 public 最稳。

### 怎么解决
1. 把需要事务的方法改成 `public`，并通过 Spring 容器里的 Bean 去调用；
2. 如果这个方法是类内部辅助方法，不要期待它自己带事务，把事务放在外层 public 方法上，或把它拆到另一个 Bean 里。

## 示例
```java
@Service
public class OrderService {
    @Transactional          // 失效：private 方法拦不到
    private void saveOrder() { /* ... */ }

    @Transactional          // 推荐：public，并由外部通过代理调用
    public void createOrder() { /* ... */ }
}
```

## 易错点
- 在 private 方法上加 `@Transactional`，以为被事务保护；它不会被拦截
- 在 final 或 static 方法上加事务注解，同样无法被代理重写，不会生效
- 不看使用的 Spring 版本和代理方式，就断言“非 public 绝对失效”；protected 和包可见方法在较新版本中有条件支持

## 追问
### [f1] 事务方法写成 public 就一定生效吗？
不一定。还要保证调用经过代理对象，同类内部用 `this` 调用依然不生效；异常被吞、类没被 Spring 管理，也会失效。

### [f2] 为什么 final 方法的事务也会失效？
CGLIB 通过继承重写方法，`final` 方法不能被重写，代理里没有包装逻辑。
