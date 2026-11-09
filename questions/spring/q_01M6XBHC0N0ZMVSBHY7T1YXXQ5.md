---
id: q_01M6XBHC0N0ZMVSBHY7T1YXXQ5
title: Spring 事务的本质是什么，怎么通过 AOP 实现？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, aop]
prerequisites: [q_01M6XBH92BND8EYH9T6RE07YES]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：Understanding the Spring Framework's Declarative Transaction Implementation", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-decl-explained.html" }
  - { title: "Spring Framework 参考文档：Proxying Mechanisms", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
estimatedMinutes: 3
---

## 一句话
Spring 事务的本质是 AOP：给标注了事务的 Bean 生成代理对象，方法执行前开启事务，执行成功就提交，抛出异常就回滚。

## 要点
- [kp1|3] 事务功能是通过 AOP 代理实现的，不改动业务代码
- [kp2|3] 代理在目标方法执行前开启事务，执行后根据结果提交或回滚
- [kp3|2] 核心拦截器是 TransactionInterceptor，具体的开启、提交、回滚交给事务管理器
- [kp4|2] 数据库连接在同一事务内共用，所以要拿到同一个连接才能一起提交或回滚

## 详解
### 先搞懂：事务代码为什么总是一个套路
扣库存加下单，两步要么都成功要么都失败。如果手写，每个方法都得是这样：开事务、执行业务、没问题就提交、出异常就回滚。几十个业务方法写几十遍，既重复又容易漏掉回滚。

这就像去银行办业务：你只说“我要转账”，柜员会帮你完成登记、核对、确认或撤销的整套流程，你不用自己管。Spring 的代理就是这个柜员。

后文用到的术语：
- **AOP（面向切面编程）**：把重复的公共逻辑（如事务）抽出来，在不改业务代码的前提下套在方法外面执行。
- **代理对象**：Spring 生成的“替身”，调用方拿到的是它，它里面再去调用真正的对象。
- **事务管理器**：真正负责开启、提交、回滚事务的组件，如 `DataSourceTransactionManager`。

### 代理怎么拦截：开启、执行、提交或回滚
Spring 发现某个 Bean 的方法有 `@Transactional`，就为这个 Bean 创建代理。外部调用该方法时，实际先进入代理中的事务拦截器：

1. **开启事务**：向事务管理器要一个事务，通常是从数据源取连接，并把自动提交关掉；
2. **执行目标方法**：调用真正的业务代码；
3. **正常返回**：提交事务；
4. **抛出异常**：判断这个异常是否需要回滚，需要就回滚，再把异常继续往外抛。

整套流程对业务代码是透明的：业务方法里只写业务，事务的“前后动作”由代理在外面包住。

### 为什么同一事务要共用连接
事务是数据库连接上的概念：同一个连接上的多条 SQL 才能一起提交或回滚。Spring 在开启事务时，把事务资源（包括连接）绑定到当前线程。之后 MyBatis、JdbcTemplate 等在同一线程里取连接，拿到的就是这个绑定的连接，所以多个 SQL 属于同一个事务。

这也说明：事务和线程绑定，在方法里新开线程操作数据库，用的就不是原来的事务。

### 这个机制带来的限制
因为靠代理实现，只有**经过代理对象**的调用才有事务。同类内部用 `this` 调用自己的其他方法、非代理管理的对象，都不会触发事务逻辑。这是下面几道“事务失效”题的共同根源。

## 示例
```java
@Service
public class OrderService {
    @Transactional
    public void createOrder() {
        // 两步在同一个事务里：要么都成功，要么都回滚
        stockMapper.decrease();
        orderMapper.insert();
    }
}
```

## 易错点
- 以为事务是数据库自动处理的；Spring 事务是在代理里调用事务管理器控制连接
- 以为在方法里开新线程也在同一个事务内；连接绑定在线程上，新线程用的是别的连接

## 追问
### [f1] Spring 是用 JDK 动态代理还是 CGLIB 实现的？
两种都可能：目标类实现了接口时可以用 JDK 动态代理，没有接口时用 CGLIB。Spring Boot 可能按配置默认启用基于类的（CGLIB）代理。

### [f2] 为什么同类内部调用事务会失效？
内部用 `this` 调用，绕过了代理对象，代理里的事务拦截逻辑不会执行。
