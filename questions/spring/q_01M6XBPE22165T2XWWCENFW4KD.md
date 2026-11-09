---
id: q_01M6XBPE22165T2XWWCENFW4KD
title: MyBatis 是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [orm]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 是一个半自动 ORM 框架：SQL 由你自己写，连接、参数设置、结果封装这些繁琐工作由框架代劳。

## 要点
- [kp1|3] MyBatis 封装了 JDBC，省去加载驱动、建连接等重复代码
- [kp2|3] SQL 由开发者手写，框架不替你生成
- [kp3|2] 框架负责把查询结果映射成 Java 对象
- [kp4] SQL 可以写在 XML 映射文件里，也可以写在注解里

## 详解
### 先搞懂：它帮你省了哪些事
做项目时，查一个用户要写 SQL，还要拿到连接、设置参数、读结果集。这像点外卖：菜谱（SQL）你自己决定，但买菜、洗菜、送餐这些杂活由平台包办。MyBatis 就是那个平台。

后文用到的词：

- **ORM**：对象关系映射，让程序用对象的方式操作数据库表。
- **JDBC**：Java 访问数据库的标准接口，MyBatis 底层就是它。
- **POJO**：普通的 Java 对象，通常只有属性和 getter、setter。

### MyBatis 做了什么
- **封装 JDBC**：不用自己加载驱动、创建连接和 `Statement`，也不用手动关闭资源。
- **关注 SQL**：SQL 是你自己写的原生 SQL，想怎么优化就怎么优化，框架不会在背后改写它。
- **映射对象**：参数从 Java 对象里取值填进 SQL，查询结果自动封装成 POJO。
- **配置灵活**：映射可以写在 XML 里，也可以用注解。

### 为什么叫"半自动"
因为 SQL 要自己写，只有"SQL 之外的事"是自动的。后一题会专门对比它和 Hibernate 的区别。

## 示例
```java
public interface UserMapper {
    @Select("SELECT id, name FROM user WHERE id = #{id}")
    User findById(long id);
}
```

## 易错点
- 以为 MyBatis 不用写 SQL；实际 SQL 必须自己写
- 以为 MyBatis 和 JDBC 无关；它只是封装了 JDBC，底层仍然走 JDBC

## 追问
### [f1] MyBatis 的 SQL 写在哪里？
可以写在 XML 映射文件里，实现 SQL 与代码分离；简单语句也可以直接写在 Mapper 接口方法的注解上。
