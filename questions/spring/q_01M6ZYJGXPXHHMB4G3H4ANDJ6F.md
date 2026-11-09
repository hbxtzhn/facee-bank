---
id: q_01M6ZYJGXPXHHMB4G3H4ANDJ6F
title: 同一个类中方法互相调用，为什么事务不生效？
type: scenario
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, dynamic-proxy]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：Proxying Mechanisms（Self-invocation）", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
  - { title: "Spring Framework 参考文档：Using @Transactional", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html" }
estimatedMinutes: 3
---

## 一句话
Spring 事务靠代理对象拦截，同一个类里用 this 调用自己的方法不经过代理，被调用方法上的 @Transactional 就不会生效。

## 要点
- [kp1|3] 只有从类外部、通过代理对象调用的方法，才会触发事务拦截
- [kp2|3] 类内部方法 A 调用方法 B，用的是 this，直接调到目标对象，绕过代理
- [kp3|2] 解决办法：把方法拆到另一个 Bean 里，通过注入的 Bean 调用
- [kp4] 其他办法：注入自己的代理对象，或用 AopContext.currentProxy()

## 详解
### 先搞懂：外面进来的人要先过前台
Spring 管理的 Bean 外面包着一层代理。可以想成一栋写字楼：外来的人必须先过前台（代理），前台登记后才放行（开启事务）。但楼里的员工之间互相串门，不经过前台。

所以：外部调用 `A()`，会过前台；`A()` 内部自己调用 `B()`，是屋里的人走动，前台不知道，`B()` 上的事务注解就没人处理。

后文用到的术语：
- **代理对象**：Spring 生成的包装对象，事务逻辑在里面。
- **目标对象**：真正的业务 Bean，内部的 `this` 指向它，而不是代理。
- **自调用**：同一个类里的方法调用自己类里的另一个方法。

### 一个失效的例子
```java
@Service
public class OrderService {
    public void create() {          // 没有事务注解
        this.save();                // 自调用，没有走代理
    }

    @Transactional
    public void save() { /* 写库 */ }
}
```
外部调用 `create()` 时进入的是代理，但 `create()` 本身没有事务；它内部 `this.save()` 拿到的是目标对象，所以 `save()` 的事务不会开启。

注意：这和 `save()` 是 public 还是 private 无关，只要是 `this` 调用，就绕过了代理。

### 几种解决办法
1. **拆到另一个 Bean（最推荐）**：把 `save()` 放到别的 `@Service` 里，通过注入的对象调用，这样就会经过代理。
2. **注入自己**：在类里注入自己的代理对象（可以用 `@Lazy` 避免循环依赖问题），通过它调用。
3. **AopContext.currentProxy()**：先开启 `exposeProxy = true`，再通过 `((OrderService) AopContext.currentProxy()).save()` 调用，代码耦合度较高，不推荐作为首选。
4. **把事务注解移到入口方法**：如果 `create()` 本身就是入口，把 `@Transactional` 加在它上面，整个流程都在事务里。

## 易错点
- 以为把内部被调用方法改成 public 就能生效；只要是 `this` 调用，仍然绕过代理
- 在没有事务的方法里调用有事务的内部方法，以为会开启事务
- 反过来：外层有事务、内部 `this` 调用另一个 `REQUIRES_NEW` 方法，以为会新开事务；实际仍在同一个事务里

## 追问
### [f1] 这个问题只影响事务吗？
不只。所有基于代理的功能都有此问题，比如 `@Async`、`@Cacheable`，自调用时也不会生效。

### [f2] 为什么推荐拆到另一个 Bean？
这样调用天然经过代理，不需要特殊技巧，代码也更清晰，职责划分更明确。
