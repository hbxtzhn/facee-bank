---
id: q_01M6XCBRD3VDDHNCDFM4XXSQ3F
title: 嵌套查询的 N+1 查询问题是什么，怎么解决？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [association-mapping, sql-optimization]
prerequisites: [q_01M6XCBQCHYQCSJGM5XAPRSM41]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MyBatis 3 文档：Mapper XML 文件（Nested Select for Association、Nested Results for Association）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
---

## 一句话
N+1 问题是先用 1 条 SQL 查出 N 条主记录，再为每条记录各发 1 条关联查询，共 N+1 条；改用联表的嵌套结果，或者把关联查询合并成批量查询。

## 要点
- [kp1|3] 嵌套查询里，主查询 1 次，每条记录再触发 1 次关联查询
- [kp2|3] 主查询返回 N 条，就会多出 N 条关联 SQL，共 N+1 条
- [kp3|2] 解决办法一：用联表的嵌套结果，一次查完
- [kp4|2] 解决办法二：先查主表，再用 `in` 一次批量查关联数据

## 详解
### 先搞懂：查 100 个订单，发了 101 条 SQL
页面要展示 100 个订单和每个订单的用户名。写法如果是：先查订单列表，再对每个订单查一次用户。数据库就会收到 1 条订单查询加 100 条用户查询，一共 101 条。

可以把它想成去超市：一次买 100 样东西，你却每样东西都单独跑一趟，比一趟买完要慢得多。

后文用到的术语：
- **嵌套查询**：关联标签用 `select` 属性指向另一条 SQL，关联对象单独再查。
- **N+1**：1 条主查询加 N 条关联查询。

### 问题是怎么出现的
在 `<association>` 或 `<collection>` 里写 `select="另一条查询的id"`，MyBatis 对主查询的每一行结果，都会用这一行的关联列值执行一次那条 SQL。主查询有多少行，就执行多少次。

每次执行都是一次数据库往返，行数大了，网络和数据库的压力都会明显增加。

### 方案对比：怎么避免 N+1
| 方案 | SQL 条数 | 怎么做 | 适合 | 代价 |
|---|---|---|---|---|
| 嵌套结果 | 1 条 | 联表查询，resultMap 内联映射 | 关联数据量小、总是要用 | SQL 复杂，一对多时重复行多 |
| 批量查询 | 2 条 | 先查主表，再用 `in` 查关联 | 关联数据多、需要分页 | 要在代码里自己组装 |
| 延迟加载 | 用到才查 | `fetchType="lazy"` | 关联数据不一定会用 | 全部用到时仍是 N+1 |

结论：关联数据总是要用，默认选嵌套结果；一对多又要分页，选批量查询；不确定会不会用到，才考虑延迟加载。

### 延迟加载能不能解决
延迟加载只是把 N 条关联查询推迟到真正用的时候，如果遍历所有订单并访问每个订单的用户，N 条查询还是会全部发出。它减少的是「没用到的查询」，不是「用到的查询」。

## 示例
```xml
<!-- 嵌套查询：容易出现 N+1 -->
<resultMap id="orderMap" type="Order">
  <id property="id" column="id"/>
  <association property="user" column="user_id" select="selectUser"/>
</resultMap>

<select id="selectUser" resultType="User">
  select * from user where id = #{id}
</select>
```

## 易错点
- 以为开了延迟加载就没有 N+1；只要每个对象的关联属性都被访问，查询次数不变
- 以为联表就一定更快；关联表很大或一对多行数很多时，联表也可能更慢，要看执行计划
- 在循环里自己调用 Mapper 查关联；同样产生 N+1，和 MyBatis 的标签无关

## 追问
### [f1] 批量查询怎么组装结果？
先查出主记录，收集它们的关联 id，用 `in` 一次查出所有关联记录，再按 id 放进 Map，遍历主记录从 Map 取值赋上。一共 2 条 SQL。
