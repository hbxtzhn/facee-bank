---
id: q_01M6XCBJTBNNSR25Y1ABPDPBEH
title: 什么是 resultMap，它怎么映射字段和属性？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
prerequisites: [q_01M6XCBFE6S6PDPTMXFYEAEP1H]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
resultMap 是一张手写的映射表：用 `<result>` 标签写明“哪个列对应哪个属性”，主键用 `<id>` 标签，查询时再引用它。

## 要点
- [kp1|3] resultMap 显式声明查询结果列与实体类属性的对应关系
- [kp2|3] `<result>` 的 `property` 写属性名，`column` 写列名
- [kp3|2] 主键对应的映射用 `<id>` 标签，其余用 `<result>`
- [kp4] 在 select 上用 `resultMap` 属性引用，可被多条查询复用

## 详解
### 先搞懂：自动对不上时，自己画一张对照表
MyBatis 默认按名字相同来填值。列叫 `order_no`，属性叫 `orderNo`，名字不同，就填不进去。你可以在每条 SQL 里改别名，也可以只写一次对照表，以后大家都按它来。

这像是公司通讯录：花名和真名对不上，就印一张对照表放在前台，谁来都查这张表。resultMap 就是这张表。

术语说明：

- **resultMap**：一份结果映射配置，写在 Mapper XML 里，有自己的 id；
- **property**：实体类的属性名；
- **column**：查询结果的列名（或别名）。

### resultMap：怎么写
先在 XML 里定义，给它一个 id 和对应的实体类型。里面一行一条对应关系：

- 主键写成 `<id property="id" column="order_id"/>`；
- 其他字段写成 `<result property="orderNo" column="order_no"/>`。

`<id>` 和 `<result>` 都是把列映射到属性。区别是 `<id>` 标明这是主键，MyBatis 会用它来判断两行数据是不是同一个对象，在关联查询里能提高效率和正确性。

定义好后，在 `<select>` 上写 `resultMap="定义的id"`，就用上了这张对照表。

### 什么时候用它
- 列名和属性名差别大，不只是下划线风格；
- 多条查询要共用同一套映射；
- 需要做关联查询、嵌套对象或集合映射，只有 resultMap 能做到。

如果只是下划线转驼峰，开一个全局开关就够，不必写 resultMap。

## 示例
```xml
<resultMap id="orderMap" type="Order">
  <id property="id" column="order_id"/>
  <result property="orderNo" column="order_no"/>
</resultMap>

<select id="selectById" resultMap="orderMap">
  select order_id, order_no from orders where order_id = #{id}
</select>
```

## 易错点
- 同一个 select 上同时写 `resultType` 和 `resultMap`，只能二选一
- `column` 写成属性名，`property` 写成列名，两个写反了
- 漏写的列仍会按名字自动映射，不代表没配置就不会填

## 追问
### [f1] resultMap 和 resultType 怎么选？
简单的单表查询、名字一致，用 `resultType` 最省事。列名对不上、要复用映射、有关联或嵌套对象时，用 `resultMap`。
