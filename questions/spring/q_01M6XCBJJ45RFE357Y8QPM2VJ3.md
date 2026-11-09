---
id: q_01M6XCBJJ45RFE357Y8QPM2VJ3
title: 实体类属性名和表字段名不一样时，SQL 别名怎么解决？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 SQL 里给查询列起别名，让别名和实体类属性名一致，MyBatis 就能自动把列映射到属性上。

## 要点
- [kp1|3] 列名和属性名不同，对应的值就不会自动填进去
- [kp2|3] 在 select 里用别名，把列名改成实体类属性名
- [kp3|2] 映射不上的属性会是 null，不一定报错
- [kp4] 列很多或要复用时，改用 resultMap 更省事

## 详解
### 先搞懂：MyBatis 是靠“名字”对号入座的
查询结果是一张表格，每列有个名字。实体类是一个对象，每个属性也有名字。MyBatis 默认的做法很朴素：列名和属性名一样，就把值填进去。

这就像收到一份快递清单，上面写“收件人”，而你家的信箱写的是“住户”。名字对不上，快递员不知道放哪个信箱。别名就是在清单上重新写一个信箱认得的名字。

术语说明：

- **别名**：SQL 里的 `列名 别名`，查询结果就用别名作为列名；
- **自动映射**：MyBatis 按名字相同自动把结果列填入对象属性。

### 别名：在 SQL 里改名
假设表里的列是 `order_id`、`order_no`，实体类的属性是 `id` 和 `orderNo`。直接 `select *`，两边名字对不上，属性会拿到 null。

做法是把列改成属性名：`select order_id id, order_no orderNo from orders`。查询结果的列名变成 `id` 和 `orderNo`，和属性一致，就能自动映射了。

这种方法的好处是不用额外配置，改一下 SQL 就行。缺点是每条 SQL 都要写一遍别名，列多了很啰嗦，也容易漏。

### 几个注意点
- 别名只改查询结果的列名，不影响表结构；
- 属性名大小写问题：默认按忽略大小写匹配，但不要依赖这一点；
- 如果只是下划线转驼峰，开启 `mapUnderscoreToCamelCase` 就不用写别名；
- 复杂映射改用 resultMap。

## 示例
```xml
<select id="selectById" resultType="Order">
  select order_id as id, order_no as orderNo
  from orders
  where order_id = #{id}
</select>
```

## 易错点
- 别名写错或漏写，属性只会是 null，MyBatis 一般不会报错
- 以为改了别名就改了表字段，其实别名只影响这一次查询结果
- 每个查询都手写别名，容易漏，列多时应改用 resultMap 或驼峰设置

## 追问
### [f1] 除了别名，还有哪些办法解决字段名和属性名不一致？
可以用 resultMap 显式配置对应关系，也可以在 settings 里开启 `mapUnderscoreToCamelCase`，处理下划线到驼峰的常见情况。
