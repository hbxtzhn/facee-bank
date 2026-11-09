---
id: q_01M6XCBFE6S6PDPTMXFYEAEP1H
title: MyBatis 是怎么把查询结果自动映射成 Java 对象的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping, reflection]
prerequisites: [q_01M6XBPETDGTTSB2BYB4NTDT71]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 执行完 SQL 后读取结果集，按列名和属性名的对应关系，用反射把每一行数据装进一个 POJO 对象。

## 要点
- [kp1|3] 框架逐行读取结果集，每行生成一个对象
- [kp2|3] 按列名与属性名的对应关系，用反射给属性赋值
- [kp3|2] 列名和属性名不一致时，用别名或 `resultMap` 指定对应关系
- [kp4] 查询多行得到 `List`，单行得到单个对象

## 详解
### 先搞懂：像按表头填表格
做项目时，你只写了查询语句，返回的就是 `User` 对象。这像按表头抄数据：数据库返回的是一张带表头的表（列名），你手里有一份空白卡片（对象），工作人员按表头名找到卡片上同名的栏目，把值抄进去。

后文用到的词：

- **结果集**：查询返回的数据，由多行多列组成。
- **POJO**：普通的 Java 对象，有若干属性。
- **映射**：列名与属性名之间的对应关系。

### 结果是怎么封装的
1. 执行 SQL，得到结果集；
2. 根据 `resultType` 或 `resultMap` 知道要生成什么类型的对象；
3. 对每一行创建一个对象；
4. 按列名找到同名属性，用反射赋值，类型转换由 TypeHandler 完成。

### 列名和属性名不一样怎么办
数据库常用下划线命名，如 `user_name`，Java 属性常用驼峰，如 `userName`。有两种办法：

- 在 SQL 里起别名：`SELECT user_name AS userName`；
- 开启驼峰映射配置，或用 `resultMap` 明确写出对应关系。

## 示例
```xml
<resultMap id="userMap" type="com.example.User">
    <id column="id" property="id"/>
    <result column="user_name" property="userName"/>
</resultMap>

<select id="findById" resultMap="userMap">
    SELECT id, user_name FROM user WHERE id = #{id}
</select>
```

## 易错点
- 列名与属性名不一致又没配映射，对应属性会是空值
- 以为必须写 `resultMap`；名字一致时只写 `resultType` 就够

## 追问
### [f1] 查询返回多行怎么处理？
Mapper 方法返回类型写成 `List`，框架会把每一行封装成一个对象并放进列表。
