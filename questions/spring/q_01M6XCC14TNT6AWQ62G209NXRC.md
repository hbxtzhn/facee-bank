---
id: q_01M6XCC14TNT6AWQ62G209NXRC
title: ObjectFactory 是做什么的，怎么自定义？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [sql-mapping, reflection]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：Configuration（objectFactory、plugins、jdbcTypeForNull）", url: "https://mybatis.org/mybatis-3/configuration.html" }
  - { title: "MyBatis 源码：ObjectFactory.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/reflection/factory/ObjectFactory.java" }
estimatedMinutes: 3
---

## 一句话
`ObjectFactory` 是 MyBatis 创建结果对象的工厂。继承默认实现并在配置里注册，就能自定义对象怎么被创建。

## 要点
- [kp1|3] 查询结果映射成 Java 对象时，对象由 `ObjectFactory` 创建
- [kp2|3] 默认实现通过反射调用构造器创建对象
- [kp3|2] 自定义时继承 `DefaultObjectFactory`，重写 `create` 方法
- [kp4|2] 在 `mybatis-config.xml` 的 `<objectFactory>` 里注册，可传属性
- [kp5] 它只管创建对象，字段赋值仍由 MyBatis 负责

## 详解
### 先搞懂：谁来“生”出结果对象
你写 `select * from user`，返回 `List<User>`。每一行数据都要变成一个 `User` 对象，这个对象得有人去 `new` 出来。

MyBatis 不会在代码里写死 `new User()`，因为它不知道你的类是什么。它把“造对象”这件事交给一个专门的工厂，就是 `ObjectFactory`。可以把它想成一个造人的车间：你告诉它要什么类，它给你一个实例。

- **反射**：运行时根据类名找到构造器并调用，不需要提前写 `new`。
- **结果对象**：查询结果每一行映射出来的那个 Java 对象。

### 默认实现：反射调用构造器
默认的 `DefaultObjectFactory` 用反射创建对象。没有构造参数时调用无参构造器，有构造参数映射时调用对应的有参构造器。

它还会处理接口：你声明返回 `List`，它会选一个实现类（如 `ArrayList`）来创建。

### 自定义：继承并注册
想改变创建逻辑，通常继承 `DefaultObjectFactory`，只重写需要的方法。

- 创建对象后设置公共默认值，比如统一给某些字段赋初值。
- 记录日志，观察哪些对象被创建了。
- 交给别的容器创建，比如从 Spring 取对象。

写完后在 `mybatis-config.xml` 里注册，`<property>` 可以给工厂传配置。注册后整个 `Configuration` 都用它。

### 进阶：接口里的几个方法（基础薄弱可先跳过）
- `create(Class)`：用无参构造器创建对象。
- `create(Class, List, List)`：带构造参数类型和参数值创建对象。
- `setProperties`：接收配置里的 `<property>`。
- `isCollection`：判断某个类型是不是集合。

## 示例
```java
public class MyObjectFactory extends DefaultObjectFactory {
    @Override
    public <T> T create(Class<T> type) {
        T obj = super.create(type);
        if (obj instanceof BaseEntity) {
            ((BaseEntity) obj).setSource("db"); // 统一设置默认值
        }
        return obj;
    }
}
```

```xml
<objectFactory type="com.example.MyObjectFactory"/>
```

## 易错点
- 以为 `ObjectFactory` 负责字段赋值；它只创建对象，赋值由结果映射完成
- 只重写无参的 `create`，忘了带参数的版本，使用构造器映射时就不生效
- 以为每个 Mapper 能配不同工厂；它是全局配置

## 追问
### [f1] 实际项目里常自定义 ObjectFactory 吗？
很少。默认实现已经够用，只有需要统一初始化对象、或让对象由其他容器创建时才会自定义。
