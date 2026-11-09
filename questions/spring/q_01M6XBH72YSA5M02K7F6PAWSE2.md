---
id: q_01M6XBH72YSA5M02K7F6PAWSE2
title: 什么是工厂方法注入？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [ioc-di]
prerequisites: [q_01M6XBH69B62C0G3H54M5E4X7D]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
工厂方法注入是让 Spring 调用一个工厂方法（静态的或某个对象上的）来得到需要的对象，并把它作为 Bean 放进容器，使用方照常注入即可。

## 要点
- [kp1|3] 对象不是直接 new 出来，而是由 Spring 调用工厂方法创建
- [kp2|3] 工厂方法分静态工厂和实例（非静态）工厂两种
- [kp3|2] 适合创建过程复杂、需要判断或第三方类（无法加注解）的对象
- [kp4] 注解方式里，@Configuration 类中的 @Bean 方法就是工厂方法的常用写法

## 详解
### 先搞懂：不是自己造，而是找工厂拿
有些对象不能简单地 `new`：比如数据库连接池，要读配置、设置很多参数；又比如第三方库里的类，没法给它加 `@Component`。

这时就像买手机：你不会自己组装，而是找工厂要成品。Spring 也是：告诉它「去调用这个工厂的这个方法，拿到的对象就当作 Bean」。

后文用到的词：
- **工厂方法**：专门负责创建并返回某个对象的方法。
- **静态工厂**：工厂方法是 static 的，通过类名直接调用。
- **实例工厂**：工厂方法是普通方法，需要先有工厂对象，再调用它。

### 两种工厂方法
**静态工厂方法**：方法是 `static` 的，Spring 直接调用「类.静态方法()」得到对象。XML 里用 `factory-method` 指定方法名。

**实例工厂方法**：先有一个工厂 Bean，Spring 再调用这个工厂对象的普通方法。XML 里用 `factory-bean` 指定工厂 Bean，用 `factory-method` 指定方法。

这里的关键是：这些工厂方法由 Spring 来调用，创建出的对象也交给 Spring 管理。如果你自己在代码里写「工厂类.静态方法()」，那只是普通调用，Spring 并不知道。

### 注解方式：@Bean 方法
现在更常见的写法是在配置类里写 `@Bean` 方法：方法体里写创建逻辑，返回值就成为一个 Bean，方法名默认就是 Bean 名。它本质上也是工厂方法。

## 示例
```java
@Configuration
public class DataSourceConfig {

    // @Bean 方法就是工厂方法：返回值交给 Spring 管理
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://localhost:3306/demo");
        return ds;
    }
}
```

```xml
<!-- XML 方式：静态工厂方法 -->
<bean id="client" class="com.example.ClientFactory" factory-method="create"/>
```

## 易错点
- 以为自己在代码里调用工厂方法就等于 Spring 管理了；必须由容器配置并调用，对象才受管理
- 混淆静态工厂和实例工厂；实例工厂要先配置工厂 Bean，再通过 factory-bean 引用
- 以为工厂方法注入是日常主要方式；常见的仍是构造器注入，工厂方法用在特殊对象的创建

## 追问
### [f1] @Bean 方法的参数从哪来？
Spring 会像注入依赖一样，从容器里找到对应类型的 Bean 传给参数，所以一个 @Bean 方法也可以依赖其他 Bean。

### [f2] 什么情况下适合用工厂方法？
创建过程复杂、需要根据条件选择不同实现，或者对象来自第三方库、不能加注解时。
