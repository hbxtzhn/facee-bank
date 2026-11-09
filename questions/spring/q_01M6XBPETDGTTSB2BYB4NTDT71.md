---
id: q_01M6XBPETDGTTSB2BYB4NTDT71
title: 什么是 JDBC？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [orm]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
JDBC 是 Java 访问关系型数据库的标准接口，直接用它要写很多重复的步骤，所以人们才发明了 MyBatis 这类框架。

## 要点
- [kp1|3] JDBC 是 Java 连接和操作关系型数据库的标准接口
- [kp2|3] 步骤：加载驱动、建连接、建 `Statement`、设参数、执行、解析结果
- [kp3|2] 连接频繁创建释放，开销大
- [kp4] SQL 写在代码里难维护，结果集解析也繁琐

## 详解
### 先搞懂：JDBC 像一套统一的插座标准
做项目时，换数据库往往只需要换一个驱动包。这像插座标准：不管是什么品牌的电器，只要符合标准都能插上。JDBC 就是 Java 和各种数据库之间的"标准插座"，具体数据库由厂商提供驱动去实现。

后文用到的词：

- **驱动**：数据库厂商提供的 jar，负责真正和数据库通信。
- **Statement**：承载 SQL 并发送给数据库的对象。
- **结果集**：查询返回的数据，要一行一行读取。

### 直接用 JDBC 的步骤
1. 加载驱动；
2. 建立连接；
3. 创建 `Statement` 或 `PreparedStatement`；
4. 给 SQL 里的占位符设置参数；
5. 执行 SQL；
6. 遍历结果集，一列一列取值并赋给对象；
7. 关闭结果集、`Statement`、连接。

### 它有哪些不足
- 连接频繁创建和释放，浪费资源；
- SQL 拼在代码字符串里，改起来麻烦；
- 参数要一个一个手工设置；
- 结果集要手工解析成对象。

MyBatis 针对这几点分别给出了办法：连接池、映射文件、自动设参和自动映射。

## 示例
```java
try (Connection conn = DriverManager.getConnection(url, user, password);
     PreparedStatement ps = conn.prepareStatement("SELECT name FROM user WHERE id = ?")) {
    ps.setLong(1, 1L);
    try (ResultSet rs = ps.executeQuery()) {
        if (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }
}
```

## 易错点
- 以为 JDBC 是某个数据库的驱动；它是接口标准，驱动由厂商提供
- 忘记关闭连接，造成连接泄漏

## 追问
### [f1] PreparedStatement 和 Statement 有什么区别？
`PreparedStatement` 用占位符预编译 SQL，能防止 SQL 注入，也便于复用；`Statement` 是直接拼接字符串，不推荐用在带用户输入的场景。
