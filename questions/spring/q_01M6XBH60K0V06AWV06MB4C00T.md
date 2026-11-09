---
id: q_01M6XBH60K0V06AWV06MB4C00T
title: 什么是控制反转（IoC）？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
控制反转（IoC）就是把创建对象、组装依赖这件事，从你自己的代码交给 Spring 容器来做，控制权从程序转移到了容器。

## 要点
- [kp1|3] IoC 把对象的创建和依赖关系的管理，从业务代码交给 Spring 容器
- [kp2|3] 「反转」的是控制权：原来是自己 new，现在是容器创建好再给你
- [kp3|2] 好处是类之间耦合降低，替换实现和写测试都更方便
- [kp4] IoC 是一种设计思想，依赖注入（DI）是它最常见的实现方式

## 详解
### 先搞懂：自己做饭 vs 点外卖
想象 Service 要用到 Dao：

- **以前**：Service 里自己 `new UserDao()`。就像自己买菜做饭，吃什么、怎么做全是自己管。想换成另一种 Dao，就得改 Service 的代码。
- **现在**：Service 只声明「我需要一个 Dao」，容器负责创建好并送过来。就像点外卖，你只说想吃什么，做和送由平台安排。

对象由谁创建、依赖谁，不再由使用者控制，而是由容器控制，这就是「控制反转」。

后文用到的词：
- **控制权**：决定「创建哪个对象、什么时候创建、怎么组装」的权力。
- **容器**：Spring 里负责创建并管理对象的那一层。
- **Bean**：被容器管理的对象。

### IoC 前后的对比
没有 IoC：

1. `OrderService` 里写 `new UserDao()`；
2. 自己决定何时创建、何时销毁；
3. 依赖的具体类写死在代码里，换实现就要改代码。

有 IoC：

1. 把类交给 Spring 管理（如加 `@Service`、`@Component`）；
2. 容器启动时创建对象，并根据依赖关系把它们组装起来；
3. 使用方只依赖接口，具体用哪个实现由容器配置决定。

### 为什么这样设计
- **解耦**：使用者不再关心依赖是怎么创建的，类与类之间不再硬绑定；
- **便于替换和测试**：测试时可以换成假的实现，不用改业务代码；
- **统一管理**：对象的创建、销毁、作用域（单例等）都由容器统一负责。

### IoC 和 DI 的关系
IoC 是思想，说的是「控制权交出去」；DI（依赖注入）是实现这个思想最常见的做法，即容器在创建对象后，把它依赖的对象传给它。

## 示例
```java
@Service
public class OrderService {
    private final UserDao userDao;

    // 不自己 new，由容器把 UserDao 传进来
    public OrderService(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

## 易错点
- 以为 IoC 就是依赖注入；IoC 是思想，依赖注入只是常见实现
- 以为 IoC 是 Spring 独有的；这是一种通用设计思想，Spring 是实现之一
- 以为控制反转就是不用写 new；是创建对象的责任转移给了容器

## 追问
### [f1] IoC 和 DI 有什么区别？
IoC 描述的是「把控制权交给容器」这一思想，DI 描述的是具体做法：容器把依赖对象注入进来。

### [f2] IoC 容器是怎么知道要创建哪些对象的？
通过配置：XML、注解（如 @Component、@Service）或 Java 配置类（@Configuration 加 @Bean）。容器启动时读取并解析这些信息，再创建对象。
