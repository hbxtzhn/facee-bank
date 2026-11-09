---
id: q_01M6XCBHSPR8QTEPTFSNWX8QQT
title: SqlSessionFactory 是做什么的，一般要创建几次？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, design-pattern]
prerequisites: [q_01M6XCBGG2THFPCV9HY7RH11DQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`SqlSessionFactory` 是创建 `SqlSession` 的工厂，创建代价高，所以整个应用通常只创建一次，做成单例长期使用。

## 要点
- [kp1|3] 作用是创建 `SqlSession`
- [kp2|3] 应用级生命周期，一个应用通常只创建一个
- [kp3|2] 创建代价高，反复创建销毁会浪费资源
- [kp4] 它是工厂模式，持有配置和数据源信息

## 详解
### 先搞懂：像一座工厂
做项目时，要先建好一座工厂，才能一批批生产产品。工厂建一次，之后每次需要产品就让它生产一个，不会每次需要一个产品就新建一座工厂。`SqlSession` 是产品，`SqlSessionFactory` 是工厂。

后文用到的词：

- **单例**：整个应用里只有一个实例。
- **工厂模式**：由专门的对象负责创建其他对象。

### 它做什么
调用 `openSession()` 创建会话。工厂里保存着解析好的配置、映射信息和数据源，所以创建它需要读文件、解析配置，成本较高。

### 为什么只创建一次
- 每次创建都要重新解析配置，浪费时间；
- 重复创建销毁会浪费内存和连接等资源；
- 配置在运行期间通常不变，一个工厂就够所有请求使用。

所以最常见的做法是应用启动时建一次，放进静态变量或交给 Spring 管理。

## 示例
```java
public class MyBatisUtil {
    private static final SqlSessionFactory FACTORY = build();

    private static SqlSessionFactory build() {
        // 读取配置并构建，只执行一次
        return null;
    }

    public static SqlSession openSession() {
        return FACTORY.openSession();
    }
}
```

## 易错点
- 每次操作数据库都新建一个工厂
- 以为工厂线程不安全；它可以被多个线程共享，不安全的是会话

## 追问
### [f1] 工厂和连接池是什么关系？
工厂持有数据源，数据源背后通常是连接池。会话从池里拿连接，工厂本身不是连接池。
