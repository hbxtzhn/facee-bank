---
id: q_01M6XCBRN0N32SHJMNVYYM7BA7
title: 嵌套结果是怎么一次查询完成关联映射的？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [association-mapping]
prerequisites: [q_01M6XCBQCHYQCSJGM5XAPRSM41]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MyBatis 3 文档：Mapper XML 文件（Nested Results for Association、id 元素）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
---

## 一句话
嵌套结果就是写一条联表 SQL 一次查出主对象和关联对象的所有列，再由 resultMap 内联映射，把每行数据拆开装进对应的对象里。

## 要点
- [kp1|3] 嵌套结果只发 1 条联表 SQL，没有 N+1 问题
- [kp2|3] 关联对象的字段在 resultMap 里内联映射，不再用 `select` 属性
- [kp3|2] 联表的列要起别名，避免同名列互相覆盖
- [kp4] 一对多时 MyBatis 按主对象的 `<id>` 合并重复行

## 详解
### 先搞懂：一趟把所有东西买齐
还是订单和用户的例子。嵌套查询是先查订单，再一个个查用户。嵌套结果则是写一条 `join`，让数据库一次把订单和用户的列都返回来。

可以把它想成一次性拿到一张大表，每一行左边是订单的信息，右边是用户的信息。MyBatis 负责把这张大表拆成「订单对象里带用户对象」。

后文用到的术语：
- **内联映射**：关联对象的字段，直接写在 `<association>` 或 `<collection>` 标签里面。

### 写法三步
1. 写联表 SQL，把需要的列都查出来，同名的列起别名，如 `u.id as user_id`。
2. resultMap 里用 `<association>`，不写 `select`，在标签里用 `<id>`、`<result>` 映射用户的列。
3. 查询语句用 `resultMap` 引用它。

### MyBatis 内部怎么拆
读到结果集的一行，先按主对象的 `<id>` 或所有列判断这个主对象是否已经创建过。没创建就新建，已有就复用。然后处理 `<association>`：新建关联对象，装好列，赋给主对象。如果是 `<collection>`，就把新建的元素追加进集合。

### 为什么性能更好
关联查询只有一次数据库往返，数据库自己做联表，通常比应用程序反复来回更高效。但这不是绝对的：关联表很大、没有合适索引时，联表也会慢，要看实际执行计划。

### 限制
- 嵌套结果没法延迟加载，它一次就查完了。
- 一对多联表时，主表的列会在每行重复，数据量大时网络传输会变多。

## 示例
```xml
<resultMap id="orderMap" type="Order">
  <id property="id" column="id"/>
  <result property="orderNo" column="order_no"/>
  <association property="user" javaType="User">
    <id property="id" column="user_id"/>
    <result property="name" column="user_name"/>
  </association>
</resultMap>

<select id="listOrders" resultMap="orderMap">
  select o.id, o.order_no, u.id as user_id, u.name as user_name
  from orders o join user u on u.id = o.user_id
</select>
```

## 易错点
- 两张表的列同名又不起别名；后面的列值会覆盖前面的，映射出错
- 以为嵌套结果也能延迟加载；延迟加载只针对嵌套查询
- 一对多联表后直接用 `limit` 分页；它按行分页，会把一个主对象的子记录截断

## 追问
### [f1] 联表有很多列重复时，MyBatis 怎么识别同一个主对象？
靠 resultMap 里的 `<id>`。没写 `<id>` 时，MyBatis 会拿所有列的值来比较，既慢又容易出错，所以建议总是写 `<id>`。
