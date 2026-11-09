---
id: q_01M6XBP8ZW6MRCPDSCEACSBRFE
title: 单例 Bean 的线程安全问题怎么解决？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [thread-safety, thread-local]
prerequisites: [q_01M6XBP8QTFKD48SGPZ0P2PB13]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Spring Framework 参考文档：Bean Scopes（singleton、prototype 及其注入单例的行为）", url: "https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html" }
  - { title: "Java SE 21 API：java.lang.ThreadLocal", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ThreadLocal.html" }
---

## 一句话
Spring 默认的单例 Bean 全应用只有一个实例，本身不保证线程安全；解决办法是别在 Bean 里存可变状态，实在要存就加锁或用 ThreadLocal 隔离。

## 要点
- [kp1|3] Spring 只负责创建单例，不会替你处理成员变量的线程安全
- [kp2|3] 首选无状态：Bean 里不放可变成员变量，数据用局部变量
- [kp3|2] 必须有共享可变状态时，用 synchronized 或 Lock 保护读写
- [kp4|2] 每个线程要一份独立数据时，把变量放进 ThreadLocal
- [kp5] 也可以把 Bean 改成 prototype 作用域，每次获取新实例

## 详解
### 先搞懂：为什么单例会出问题
想象公司只有一台共用打印机（单例）。如果打印机里还存着“上一个人的文档”（成员变量），两个人同时来用，文档就串了。Controller、Service 在 Spring 里默认都是单例。同一时刻会被很多请求线程同时调用。所以只要它们里面存了会变的数据，就可能出问题。

后文用到的术语：
- **单例（singleton）**：容器里这个 Bean 只有一个对象，所有线程共用。
- **无状态**：对象里没有会被修改的成员变量，调用结果只取决于传进来的参数。
- **局部变量**：方法里声明的变量，每个线程调用方法时都有自己的一份。
- **ThreadLocal**：给每个线程配一个“自己的小格子”，存取互不干扰。

### 无状态：最省事的办法
把可变数据放进方法参数和局部变量里，Bean 本身只放不会变的东西，比如注入的其他 Bean、配置值。绝大多数 Service、Controller 都能做到这一点，这时根本不需要加锁。

### 加锁：共享状态必须保护时
如果确实需要共享一个计数器或缓存，可以用 `synchronized` 或 `ReentrantLock` 把读写包起来；简单计数也可以用 `AtomicInteger` 之类的原子类。代价是同一时刻只有一个线程能进入，并发度下降，所以锁的范围要尽量小。

### ThreadLocal：每个线程一份
有些数据天然属于“当前请求”，比如当前登录用户。把它放进 `ThreadLocal`，每个线程读写的是自己那一份，不需要加锁。注意：线程池里的线程会被复用，请求结束要调用 `remove()`，否则下一个请求可能读到上一个请求的数据，也容易造成内存泄漏。

### 方案对比：几种办法怎么选
| 方案 | 做法 | 优点 | 代价 |
|---|---|---|---|
| 无状态 | 数据放局部变量 | 无锁，最简单 | 不能在 Bean 里缓存数据 |
| 加锁 | synchronized / Lock | 能保护真正共享的数据 | 并发度下降，写错可能死锁 |
| ThreadLocal | 每线程一份数据 | 不用加锁 | 必须及时 remove |
| prototype 作用域 | 每次获取新实例 | 实例不共享 | 创建次数多；注入到单例里只会注入一次 |

结论：默认写成无状态；要共享数据就加锁；要“每个请求一份”就用 ThreadLocal。

## 示例
```java
@Service
public class OrderService {
    // 错误：多个线程共用这个成员变量
    // private int count;

    // 正确：数据放局部变量
    public int calc(int a, int b) {
        int sum = a + b;
        return sum;
    }
}
```

## 易错点
- 以为 Spring 会自动保证单例线程安全；它只管创建，不管你怎么用成员变量
- 以为注入的 Service 对象也要加锁；只读依赖本身是安全的，要看那个 Bean 是否有可变状态
- 用 ThreadLocal 后不 remove，线程池复用线程时数据会串
- 把 Bean 改成 prototype 后注入单例，以为每次调用都是新对象；实际注入只发生一次

## 追问
### [f1] 哪些 Bean 最容易出现线程安全问题？
带可变成员变量的 Controller、Service。数据库连接池、Mapper 这类框架提供的 Bean 本身是为并发设计的，一般不用担心。

### [f2] ThreadLocal 为什么会内存泄漏？
每个线程内部有个 Map，key 是弱引用，value 是强引用。线程长期存活（线程池）又不调用 remove，value 就一直回收不掉。
