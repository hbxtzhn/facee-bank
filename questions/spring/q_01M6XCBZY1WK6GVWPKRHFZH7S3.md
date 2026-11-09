---
id: q_01M6XCBZY1WK6GVWPKRHFZH7S3
title: 为什么 Mapper 接口不需要实现类？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [mybatis-internals, dynamic-proxy]
prerequisites: [q_01M6XCBGRWDPSDMVC1HYFX55X8]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
MyBatis 在运行时用 JDK 动态代理，通过 MapperProxyFactory 为 Mapper 接口生成 MapperProxy 代理对象，调用接口方法时由代理转成 SQL 执行，所以不需要自己写实现类。

## 要点
- [kp1|3] 启动时每个 Mapper 接口会注册一个 `MapperProxyFactory`
- [kp2|3] `getMapper` 时由工厂创建 JDK 动态代理，得到 `MapperProxy`
- [kp3|2] `MapperProxy` 实现 `InvocationHandler`，方法调用进入 `invoke`
- [kp4|2] 接口全名加方法名对应 XML 里的 namespace 加语句 id
- [kp5] JDK 动态代理要求目标是接口，所以 Mapper 必须是接口

## 详解
### 先搞懂：接线员代替你办事
你打客服电话，接线员接起来，根据你说的需求去对应的部门办理，你不用知道具体是谁办的。

Mapper 接口就是电话号码清单，只有“方法名”，没有具体内容。MyBatis 在运行时临时派出一个“接线员”（代理对象）：你调用方法，它接起来，根据方法名去找对应的 SQL，执行后把结果交给你。

后文用到的词：

- **动态代理**：程序运行时，临时生成一个对象来代替真实对象处理方法调用。
- **InvocationHandler**：JDK 动态代理里，真正处理方法调用的接口，核心方法是 `invoke`。
- **Mapper 接口**：只有方法声明的接口，如 `UserMapper`。

### 启动时：为每个接口登记工厂
解析配置时，`MapperRegistry` 会为每个 Mapper 接口创建一个 `MapperProxyFactory`，把接口类型存进去，并保存在一个 Map 里。

同时，XML 里每条 SQL 会登记成 `MappedStatement`，它的 ID 是 namespace 加语句 id，比如 `com.example.UserMapper.findById`。

### 获取 Mapper：用工厂生成代理
调用 `session.getMapper(UserMapper.class)` 时：

1. `MapperRegistry` 找到这个接口对应的 `MapperProxyFactory`；
2. 工厂创建一个 `MapperProxy` 对象，里面保存了 `SqlSession` 和接口信息；
3. 用 `Proxy.newProxyInstance` 生成代理对象并返回。

你拿到的 `UserMapper`，实际是这个代理对象，没有手写的实现类。

### 调用时：进入 invoke
调用 `userMapper.findById(1)` 时，调用被转给 `MapperProxy.invoke`：

- 如果调用的是 `toString`、`hashCode` 这类 `Object` 的方法，直接处理；
- 否则，根据接口全名和方法名找到对应的 SQL，交给 `SqlSession` 执行。

接口全名加方法名，就是 SQL 的 ID，所以 XML 里的 namespace 要写接口全名，语句 id 要和方法名一致。

### 为什么要用动态代理
Mapper 接口方法的作用是“按名字执行一条 SQL”，每个方法的逻辑都是重复的：取参数、找 SQL、执行、转结果。

用代理把这些重复的事统一处理，开发者只需写接口和 SQL，不用写模板代码。

### 在 Spring 里怎么对应
Spring 通过 `@MapperScan` 扫描接口，为每个接口注册一个 `MapperFactoryBean`，由它调用 `getMapper` 得到代理，再注入到你的 Service。

## 示例
```java
public interface UserMapper {
    User findById(Long id);   // 只有声明，没有实现类
}
```

```xml
<!-- namespace 是接口全名，id 是方法名，两者合起来对应这个方法 -->
<mapper namespace="com.example.UserMapper">
    <select id="findById" resultType="User">
        select * from user where id = #{id}
    </select>
</mapper>
```

## 易错点
- namespace 写得和接口全名不一致，调用时找不到 SQL
- Mapper 定义成普通类；JDK 动态代理只能代理接口
- 以为接口里的方法能重载并对应不同 SQL；SQL ID 只看方法名，重载会冲突

## 追问
### [f1] Mapper 接口里能写 default 方法吗？
可以。代理在遇到 default 方法时，会直接调用接口自己的默认实现，不再去找 SQL。

### [f2] 为什么不用 CGLIB 代理？
Mapper 本来就是接口，JDK 动态代理够用，也不需要额外依赖。
