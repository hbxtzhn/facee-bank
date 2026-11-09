---
id: q_01M6XBH7BA65HAH617D2F70AZW
title: Spring Bean 的生命周期有哪些阶段？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [bean-lifecycle]
prerequisites: [q_01M6XBH5R4PF3S781XSRZRP188]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Spring Framework 参考文档：Customizing the Nature of a Bean（初始化与销毁回调的顺序、Aware）", url: "https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html" }
  - { title: "Spring Framework Javadoc：BeanFactory（Bean 生命周期方法的完整顺序）", url: "https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/BeanFactory.html" }
---

## 一句话
Spring Bean 的生命周期可以分成实例化、属性赋值、初始化、使用、销毁五步；初始化前后和销毁时，Spring 都留了扩展点，让你插入自己的逻辑。

## 要点
- [kp1|3] 顺序是：实例化、属性赋值、初始化、使用、销毁
- [kp2|3] 初始化阶段有 Aware 回调、BeanPostProcessor 前后处理、@PostConstruct、init-method
- [kp3|2] 销毁阶段依次触发 @PreDestroy、DisposableBean、destroy-method
- [kp4|2] 单例 Bean 随容器关闭销毁；AOP 代理通常在初始化后处理中生成
- [kp5] BeanPostProcessor 对所有 Bean 生效，是 Spring 许多功能的基础

## 详解
### 先搞懂：一个员工从入职到离职
把 Bean 想成公司员工：

- 招聘一个人（创建）；
- 给他发工牌、分配设备（赋值依赖）；
- 入职培训（初始化）；
- 正式上岗工作（使用）；
- 离职交接（销毁）。

公司在每个环节都可以安排一些「额外动作」，Spring 的生命周期回调就是在这些环节让你插手。

后文用到的词：
- **Bean**：被 Spring 容器管理的对象。
- **回调**：Spring 在特定时刻自动调用你写的方法。
- **后置处理器（BeanPostProcessor）**：在 Bean 初始化前后，对所有 Bean 都做加工的扩展点。

### 实例化：先把对象创建出来
容器根据 Bean 的定义，调用构造方法（或工厂方法）创建出一个对象，此时对象里的依赖字段还都是空的。

### 属性赋值：把依赖填进去
容器把依赖和配置值注入进去，相当于完成了 setter 或字段注入。此时对象有了依赖，但还没有走初始化逻辑。

### 初始化：让 Bean 进入可用状态
这是扩展点最多的阶段，大致顺序如下：

1. **Aware 回调**：如果 Bean 实现了 `BeanNameAware`、`ApplicationContextAware` 等接口，容器把相应信息传给它；
2. **BeanPostProcessor 前置处理**：`postProcessBeforeInitialization`，此时标注了 `@PostConstruct` 的方法也会被执行；
3. **InitializingBean**：如果实现了该接口，调用 `afterPropertiesSet()`；
4. **自定义 init-method**：配置里指定的初始化方法；
5. **BeanPostProcessor 后置处理**：`postProcessAfterInitialization`，AOP 代理通常就是在这里把原对象包装成代理对象。

### 使用与销毁
初始化完成后，Bean 放进容器，供其他对象使用。容器关闭时，对单例 Bean 执行销毁回调：

1. `@PreDestroy` 标注的方法；
2. 实现了 `DisposableBean` 的 `destroy()`；
3. 自定义的 destroy-method。

用来释放连接、关闭线程池等资源。

### 方案对比：初始化回调有几种写法
| 写法 | 方式 | 特点 |
|---|---|---|
| `@PostConstruct` | 方法上加注解 | 简单、不依赖 Spring 接口，最常用 |
| `InitializingBean` | 实现接口 | 与 Spring 耦合 |
| `init-method` | 配置里指定方法名 | 适合第三方类，无需改源码 |

结论：自己写的类优先用 `@PostConstruct` 和 `@PreDestroy`；第三方类用 `@Bean(initMethod=..., destroyMethod=...)`。

## 示例
```java
@Component
public class CacheLoader {

    @PostConstruct
    public void init() {
        System.out.println("初始化：预加载缓存");
    }

    @PreDestroy
    public void close() {
        System.out.println("销毁：释放资源");
    }
}
```

## 易错点
- 在构造方法里使用被注入的依赖；构造阶段属性还没赋值，应放到 @PostConstruct 里
- 以为 prototype Bean 也会由容器负责销毁；容器不管理 prototype 的销毁回调
- 以为 Aware 和 BeanPostProcessor 是同一回事；前者只针对实现它的 Bean，后者对所有 Bean 生效

## 追问
### [f1] 为什么不能在构造方法里使用 @Autowired 的字段？
构造方法执行时还处于实例化阶段，属性赋值还没发生，字段还是 null；要用依赖，应该放在初始化阶段（如 @PostConstruct）。

### [f2] AOP 代理是在生命周期哪一步生成的？
通常在初始化之后，由 BeanPostProcessor 的后置处理把原始 Bean 包装成代理对象，容器里最终放的是这个代理。
